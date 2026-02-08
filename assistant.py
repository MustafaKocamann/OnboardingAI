import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

# Import templates from prompts.py
from prompts import (
    ACCESS_DENIED_MESSAGES,
    SCL_SYSTEM_INSTRUCTIONS,
    LOCATION_REMINDERS
)

# Logger setup
logger = logging.getLogger(__name__)


# ============================================================
# PYDANTIC OUTPUT SCHEMA - Corporate Format Requirement
# ============================================================
class TransmissionResponse(BaseModel):
    """Umbrella Corporation standard communication format"""
    asset_name: str = Field(description="Employee's full name")
    asset_id: str = Field(description="Employee ID")
    scl_level: int = Field(description="Security Clearance Level (1-5)")
    subject: str = Field(description="Brief summary of the query")
    protocol_response: str = Field(description="Main response content")
    security_notification: str = Field(description="Security notification")
    access_granted: bool = Field(description="Was access granted?")


# ============================================================
# SECURITY CLEARANCE LEVELS - Permission Definitions
# ============================================================
SCL_PERMISSIONS = {
    1: {
        "allowed_topics": ["general_policies", "hr_benefits", "office_locations"],
        "restricted_keywords": ["outbreak", "specimen", "t-virus", "g-virus", "nemesis", "tyrant", "secret", "classified"],
        "max_retrieval_k": 2
    },
    2: {
        "allowed_topics": ["general_policies", "hr_benefits", "office_locations", "safety_protocols", "emergency_procedures"],
        "restricted_keywords": ["outbreak", "specimen", "t-virus", "g-virus", "nemesis", "tyrant"],
        "max_retrieval_k": 3
    },
    3: {
        "allowed_topics": ["general_policies", "hr_benefits", "office_locations", "safety_protocols", "emergency_procedures", "research_guidelines"],
        "restricted_keywords": ["t-virus", "g-virus", "nemesis", "tyrant"],
        "max_retrieval_k": 4
    },
    4: {
        "allowed_topics": ["general_policies", "hr_benefits", "office_locations", "safety_protocols", "emergency_procedures", "research_guidelines", "containment_protocols"],
        "restricted_keywords": ["nemesis", "tyrant"],
        "max_retrieval_k": 5
    },
    5: {
        "allowed_topics": ["*"],  # Full access
        "restricted_keywords": [],
        "max_retrieval_k": 10
    }
}


# ============================================================
# SQLITE CHAT HISTORY - Persistent Memory Management
# ============================================================
class ChatMessageHistory:
    """SQLite-based message history management"""
    
    def __init__(self, db_path: str = "chat_history.db", session_id: str = "default"):
        self.db_path = db_path
        self.session_id = session_id
        self._init_db()
    
    def _init_db(self):
        """Create the database table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS message_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
    
    def add_message(self, role: str, content: str):
        """Add a new message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO message_history (session_id, role, content) VALUES (?, ?, ?)",
                    (self.session_id, role, content)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding message: {e}")
    
    def get_messages(self) -> List[dict]:
        """Retrieve all messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM message_history WHERE session_id = ? ORDER BY id",
                    (self.session_id,)
                )
                rows = cursor.fetchall()
                return [{"role": row[0], "content": row[1]} for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    
    def get_langchain_messages(self):
        """Return messages in LangChain format"""
        messages = self.get_messages()
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "human":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                langchain_messages.append(AIMessage(content=msg["content"]))
        return langchain_messages
    
    def clear(self):
        """Clear all messages in this session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM message_history WHERE session_id = ?",
                    (self.session_id,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error clearing messages: {e}")


# ============================================================
# SECURITY GUARDRAILS - Security Layer (prompts.py integration)
# ============================================================
class SecurityGuardrails:
    """SCL-based security filtering and prompt injection protection"""
    
    # OMEGA-Level confidential keywords - must never be disclosed
    CONFIDENTIAL_KEYWORDS = ["salary", "maaş", "performance", "performans", "evaluation", "değerlendirme", "compensation", "ücret"]
    
    # Underground facility keywords
    FACILITY_KEYWORDS = ["underground", "yeraltı", "sub-level", "basement", "bodrum", "gizli tesis"]
    
    def __init__(self, employee_info: Dict[str, Any]):
        self.employee_info = employee_info or {}
        # Use clearance_level directly from employees.py
        self.scl_level = self.employee_info.get("clearance_level", 1)
        self.location = self.employee_info.get("location", "Unknown")
        self.location_security = self.employee_info.get("location_security_level", "GAMMA")
        self.has_facility_access = self.employee_info.get("has_facility_access", False)
        self.permissions = SCL_PERMISSIONS.get(self.scl_level, SCL_PERMISSIONS[1])
    
    def _generate_ref_id(self, seed: str) -> str:
        """Generate a unique reference ID"""
        return f"{hash(seed) % 10000:04d}"
    
    def check_query_permission(self, query: str) -> tuple[bool, str]:
        """
        Check query permissions based on SCL level
        Returns: (is_allowed, denial_message)
        """
        query_lower = query.lower()
        
        # OMEGA-Level confidential data check (salary, performance, etc.)
        for keyword in self.CONFIDENTIAL_KEYWORDS:
            if keyword in query_lower:
                return False, self._generate_confidential_denial()
        
        # Location-based restriction check (underground facility)
        if any(kw in query_lower for kw in self.FACILITY_KEYWORDS):
            if not self.has_facility_access:
                return False, self._generate_facility_denial()
        
        # SCL-based restricted keyword check
        for keyword in self.permissions["restricted_keywords"]:
            if keyword in query_lower:
                return False, self._generate_scl_denial(keyword)
        
        return True, ""
    
    def _generate_confidential_denial(self) -> str:
        """OMEGA-Level confidential data access denial - uses prompts.py template"""
        return ACCESS_DENIED_MESSAGES["confidential_data"]
    
    def _generate_facility_denial(self) -> str:
        """Underground facility access denial - uses prompts.py template"""
        return ACCESS_DENIED_MESSAGES["underground_facility"]
    
    def _generate_scl_denial(self, triggered_keyword: str) -> str:
        """SCL-based access denial - uses prompts.py template"""
        # Determine which SCL level is required
        required_scl = 5  # Default
        for scl, perms in SCL_PERMISSIONS.items():
            if triggered_keyword not in perms["restricted_keywords"]:
                required_scl = scl
                break
        
        return ACCESS_DENIED_MESSAGES["scl_insufficient"].format(
            required_scl=required_scl,
            scl_level=self.scl_level,
            ref_id=f"SCL-{self._generate_ref_id(triggered_keyword)}"
        )
    
    def _generate_location_denial(self) -> str:
        """Location-based access denial - uses prompts.py template"""
        return ACCESS_DENIED_MESSAGES["location_restricted"].format(
            required_location="Raccoon City HQ",
            current_location=self.location,
            ref_id=f"LOC-{self._generate_ref_id(self.location)}"
        )
    
    def get_retrieval_k(self) -> int:
        """Return retrieval k value based on SCL level"""
        return self.permissions["max_retrieval_k"]
    
    def get_dynamic_system_instruction(self) -> str:
        """Get dynamic system instruction based on SCL level - from prompts.py"""
        scl_instruction = SCL_SYSTEM_INSTRUCTIONS.get(self.scl_level, SCL_SYSTEM_INSTRUCTIONS[1])
        location_reminder = LOCATION_REMINDERS.get(self.location, "")
        
        return scl_instruction + location_reminder


# ============================================================
# ONBOARDING ASSISTANT - Main Class
# ============================================================
class OnboardingAssistant:
    def __init__(
        self,
        system_prompt: str,
        llm,
        message_history: Optional[List] = None,
        vector_store = None,
        employee_information: Optional[Dict] = None,
        session_id: str = "default",
        db_path: str = "chat_history.db",
        retrieval_score_threshold: float = 0.5
    ):
        self.system_prompt = system_prompt
        self.llm = llm
        self.vector_store = vector_store
        self.employee_information = employee_information or {}
        self.retrieval_score_threshold = retrieval_score_threshold
        
        # Initialize Security Guardrails
        self.security = SecurityGuardrails(self.employee_information)
        
        # SQLite-based message history
        self.chat_history = ChatMessageHistory(db_path=db_path, session_id=session_id)
        
        # Initialize the chain
        self.chain = self._get_conversational_chain()
    
    def _get_conversational_chain(self):
        """Create RAG-powered conversational chain"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def _retrieve_policy_information(self, query: str) -> str:
        """
        Retrieve relevant policy information from vector store
        Applies SCL-based k value and score_threshold
        """
        if self.vector_store is None:
            logger.warning("Vector store is not initialized")
            return "No policy information available."
        
        try:
            # Get k value based on SCL level
            k_value = self.security.get_retrieval_k()
            
            # Retriever with optimized parameters
            retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": k_value,
                    "score_threshold": self.retrieval_score_threshold
                }
            )
            
            docs = retriever.invoke(query)
            
            if not docs:
                return "No relevant policy information found within your clearance level."
            
            # Merge documents
            policy_info = "\n\n---\n\n".join([
                f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" 
                for doc in docs
            ])
            return policy_info
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return "Policy database temporarily unavailable. Please try again later."
    
    def _format_employee_information(self) -> str:
        """Prepare employee information in LLM-friendly format"""
        if not self.employee_information:
            return "No employee information available."
        
        # Structured format for better LLM understanding - filter confidential fields
        emp = self.employee_information
        formatted = f"""
Asset Profile[cite: 1881]:
- Name: {emp.get('name', 'Unknown')} {emp.get('lastname', '')}
- ID: {emp.get('employee_id', 'N/A')[:8] if emp.get('employee_id') else 'N/A'}
- Position: {emp.get('position', 'Unassigned')}[cite: 139]
- Department: {emp.get('department', 'Unassigned')}[cite: 126]
- Location: {emp.get('location', 'Unknown')} (Security Level: {emp.get('location_security_level', 'GAMMA')})[cite: 1016, 1099]
- Security Clearance Level: SCL-{self.security.scl_level}[cite: 1028]
- Hire Date: {emp.get('hire_date', 'Unknown')}
- Supervisor: {emp.get('supervisor', 'Unassigned')}
- Facility Access: {'Level-4 Authorized' if emp.get('has_facility_access') else 'Standard Access Only'}[cite: 1049]
"""
        return formatted
    
    def _format_transmission_response(self, response: str) -> str:
        """Convert response to corporate Transmission format"""
        emp = self.employee_information
        full_name = f"{emp.get('name', 'Unknown')} {emp.get('lastname', '')}"
        emp_id = emp.get('employee_id', 'N/A')[:8] if emp.get('employee_id') else 'N/A'
        
        # If response is already in Transmission format, return as-is
        if "**TRANSMISSION START**" in response:
            return response
        
        # Get location-specific security reminder
        location_reminder = LOCATION_REMINDERS.get(self.security.location, "")
        
        # Otherwise, format the response
        formatted = f"""
**TRANSMISSION START**
---
**IDENTIFIED ASSET**: {full_name} | {emp_id} | SCL-{self.security.scl_level} | {self.security.location}
**SUBJECT**: Employee Inquiry Response

**PROTOCOL RESPONSE**: 
{response}

**SECURITY COMPLIANCE NOTIFICATION**: 
This transmission is logged under Protocol 7-Alpha[cite: 1121]. Any unauthorized distribution of this information 
will result in immediate termination of employment and potential Experimental Participation assignment[cite: 1341].

{location_reminder}

"Our business is life itself."
---
**TRANSMISSION END**
"""
        return formatted.strip()
    
    def get_response(self, user_input: str) -> str:
        """Generate response to user input - Full Security Pipeline"""
        try:
            # =============================================
            # STEP 1: Security Pre-Check (SCL Filtering)
            # =============================================
            is_allowed, denial_message = self.security.check_query_permission(user_input)
            if not is_allowed:
                # Still save the messages
                self.chat_history.add_message("human", user_input)
                self.chat_history.add_message("ai", denial_message)
                return denial_message
            
            # =============================================
            # STEP 2: RAG Retrieval (with SCL-based k)
            # =============================================
            retrieved_policy_information = self._retrieve_policy_information(user_input)
            
            # =============================================
            # STEP 3: Context Preparation
            # =============================================
            employee_info = self._format_employee_information()
            dynamic_instruction = self.security.get_dynamic_system_instruction()
            
            # Update system prompt
            formatted_system_prompt = self.system_prompt.format(
                employee_information=employee_info,
                retrieved_policy_information=retrieved_policy_information
            ) + "\n" + dynamic_instruction
            
            # =============================================
            # STEP 4: LLM Invocation with LangSmith Tracing
            # =============================================
            prompt = ChatPromptTemplate.from_messages([
                ("system", formatted_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            chat_history = self.chat_history.get_langchain_messages()
            
            # LangSmith metadata for filtering and analysis
            emp = self.employee_information
            langsmith_config = RunnableConfig(
                metadata={
                    "employee_id": str(emp.get("employee_id", "unknown"))[:8],
                    "employee_name": f"{emp.get('name', '')} {emp.get('lastname', '')}",
                    "scl_level": self.security.scl_level,
                    "department": emp.get("department", "unknown"),
                    "position": emp.get("position", "unknown"),
                    "location": self.security.location,
                    "location_security": self.security.location_security,
                    "has_facility_access": emp.get("has_facility_access", False),
                    "query_type": "normal",
                },
                tags=[
                    f"scl-{self.security.scl_level}",
                    f"dept-{emp.get('department', 'unknown')}",
                    f"loc-{self.security.location.replace(' ', '-')}",
                ]
            )
            
            response = chain.invoke(
                {
                    "chat_history": chat_history,
                    "input": user_input
                },
                config=langsmith_config
            )
            
            # =============================================
            # STEP 5: Output Formatting (Transmission Format)
            # =============================================
            formatted_response = self._format_transmission_response(response)
            
            # =============================================
            # STEP 6: Save to History
            # =============================================
            self.chat_history.add_message("human", user_input)
            self.chat_history.add_message("ai", formatted_response)
            
            return formatted_response
            
        except Exception as e:
            # =============================================
            # ERROR HANDLING - Graceful Degradation
            # =============================================
            logger.error(f"Response generation error: {e}")
            
            error_response = """
**TRANSMISSION START**
---
**SYSTEM ALERT**: Temporary Access Restriction[cite: 1121]

**PROTOCOL RESPONSE**: 
The U-SIOP system is currently experiencing high demand or maintenance. 
Your inquiry has been queued for processing.

Please retry your request in a few moments. If this issue persists, 
contact the IT Help Desk at extension 4-UMBRELLA.

**SECURITY COMPLIANCE NOTIFICATION**: 
System outages are logged. Do not attempt to bypass security protocols during this time.
Unauthorized system access attempts may result in Basement Cleaning Detail (BCD) assignment[cite: 1333].

"Our business is life itself."
---
**TRANSMISSION END**
"""
            return error_response.strip()
    
    def clear_history(self):
        """Clear conversation history"""
        self.chat_history.clear()
    
    def get_conversation_history(self) -> List[dict]:
        """Return conversation history"""
        return self.chat_history.get_messages()
    
    def get_employee_scl(self) -> int:
        """Return current employee's SCL level"""
        return self.security.scl_level
    
    def get_location_security(self) -> str:
        """Return current employee's location security level"""
        return self.security.location_security
