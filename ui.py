

import streamlit as st
import time
from typing import Dict, Any, Optional



COLORS = {
    "primary": "#D12027",      
    "background": "#0D0D0D",   
    "surface": "#1A1A1A",      
    "surface_light": "#2A2A2A", 
    "text": "#E0E0E0",         
    "text_muted": "#888888",   
    "success": "#28A745",      
    "warning": "#FFC107",      
    "danger": "#DC3545",       
    "info": "#17A2B8",        
}

SCL_COLORS = {
    1: "#6C757D",  
    2: "#17A2B8",  
    3: "#28A745",  
    4: "#FFC107",  
    5: "#D12027",  
}

SCL_LABELS = {
    1: "ENTRY-LEVEL",
    2: "STANDARD",
    3: "ELEVATED",
    4: "HIGH",
    5: "EXECUTIVE",
}


def apply_custom_style():
    """
    Injects global CSS to create the U-SIOP Terminal aesthetic.
    Removes default Streamlit padding, header, and footer.
    Implements monospaced typography and custom color scheme.
    """
    custom_css = f"""
    <style>
        /* ============================================
           GLOBAL RESET & BASE STYLES
           ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@500;700&display=swap');
        
        /* Hide Streamlit default elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* Remove default padding */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }}
        
        /* Main app background */
        .stApp {{
            background-color: {COLORS['background']};
        }}
        
        /* ============================================
           TYPOGRAPHY
           ============================================ */
        html, body, [class*="css"] {{
            font-family: 'JetBrains Mono', monospace !important;
            color: {COLORS['text']};
        }}
        
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif !important;
            color: {COLORS['primary']} !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        /* ============================================
           SIDEBAR STYLES
           ============================================ */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['surface']};
            border-right: 2px solid {COLORS['primary']};
        }}
        
        [data-testid="stSidebar"] .block-container {{
            padding-top: 0.5rem !important;
        }}
        
        /* ============================================
           CHAT CONTAINER STYLES
           ============================================ */
        .stChatMessage {{
            background-color: {COLORS['surface']} !important;
            border: 1px solid {COLORS['surface_light']} !important;
            border-radius: 4px !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .stChatMessage [data-testid="chatAvatarIcon-assistant"] {{
            background-color: {COLORS['primary']} !important;
        }}
        
        .stChatMessage [data-testid="chatAvatarIcon-user"] {{
            background-color: {COLORS['info']} !important;
        }}
        
        /* Chat input styling */
        .stChatInputContainer {{
            background-color: {COLORS['surface']} !important;
            border-top: 2px solid {COLORS['primary']} !important;
        }}
        
        .stChatInputContainer textarea {{
            background-color: {COLORS['surface_light']} !important;
            color: {COLORS['text']} !important;
            border: 1px solid {COLORS['primary']} !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        
        /* ============================================
           CUSTOM COMPONENTS
           ============================================ */
        .employee-card {{
            background: linear-gradient(145deg, {COLORS['surface']}, {COLORS['surface_light']});
            border: 2px solid {COLORS['primary']};
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        .scl-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .status-indicator {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(209, 32, 39, 0.7); }}
            50% {{ opacity: 0.7; box-shadow: 0 0 0 10px rgba(209, 32, 39, 0); }}
            100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(209, 32, 39, 0); }}
        }}
        
        .logo-container {{
            text-align: center;
            padding: 1rem;
            border-bottom: 1px solid {COLORS['surface_light']};
            margin-bottom: 1rem;
        }}
        
        .logo-text {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.2rem;
            color: {COLORS['primary']};
            font-weight: 700;
            letter-spacing: 3px;
        }}
        
        .terminal-header {{
            background: linear-gradient(90deg, {COLORS['primary']}22, transparent);
            border-left: 4px solid {COLORS['primary']};
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
        }}
        
        .data-field {{
            display: flex;
            justify-content: space-between;
            padding: 0.3rem 0;
            border-bottom: 1px solid {COLORS['surface_light']};
            font-size: 0.85rem;
        }}
        
        .data-label {{
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 1px;
        }}
        
        .data-value {{
            color: {COLORS['text']};
            font-weight: 500;
        }}
        
        .transmission-box {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['primary']}44;
            border-radius: 4px;
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['background']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['primary']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['primary']}cc;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_logo():
    """Renders the Umbrella Corporation logo with pulse effect"""
    logo_html = f"""
    <div class="logo-container">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">☂️</div>
        <div class="logo-text">UMBRELLA</div>
        <div style="font-size: 0.7rem; color: {COLORS['text_muted']}; letter-spacing: 2px;">
            CORPORATION
        </div>
        <div style="margin-top: 0.5rem;">
            <span class="status-indicator" style="background-color: {COLORS['primary']};"></span>
            <span style="font-size: 0.65rem; color: {COLORS['text_muted']};">SYSTEM MONITORING ACTIVE</span>
        </div>
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)


def render_employee_card(employee: Dict[str, Any]):
    """
    Renders a high-fidelity Employee ID Card (Dossier style)
    with SCL-based badge coloring.
    """
    if not employee:
        st.warning("No employee data available")
        return
    
    # Extract employee data
    full_name = f"{employee.get('name', 'Unknown')} {employee.get('lastname', '')}"
    emp_id = str(employee.get('employee_id', 'N/A'))[:8]
    position = employee.get('position', 'Unassigned')
    department = employee.get('department', 'Unassigned')
    location = employee.get('location', 'Unknown')
    location_security = employee.get('location_security_level', 'GAMMA')
    scl = employee.get('clearance_level', 1)
    hire_date = employee.get('hire_date', 'Unknown')
    has_facility = employee.get('has_facility_access', False)
    
    # Get SCL styling
    scl_color = SCL_COLORS.get(scl, SCL_COLORS[1])
    scl_label = SCL_LABELS.get(scl, "UNKNOWN")
    
    # Employee Card HTML
    card_html = f"""
    <div class="employee-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 0.65rem; color: {COLORS['text_muted']}; letter-spacing: 2px; margin-bottom: 0.25rem;">
                EMPLOYEE DOSSIER
            </div>
            <div style="font-size: 1.1rem; color: {COLORS['text']}; font-weight: 600;">
                {full_name.upper()}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; font-family: 'JetBrains Mono', monospace;">
                ID: {emp_id}
            </div>
        </div>
        
        <div style="text-align: center; margin: 1rem 0;">
            <span class="scl-badge" style="background-color: {scl_color}22; color: {scl_color}; border: 1px solid {scl_color};">
                SCL-{scl} | {scl_label}
            </span>
        </div>
        
        <div style="margin-top: 1rem;">
            <div class="data-field">
                <span class="data-label">Position</span>
                <span class="data-value">{position}</span>
            </div>
            <div class="data-field">
                <span class="data-label">Department</span>
                <span class="data-value">{department}</span>
            </div>
            <div class="data-field">
                <span class="data-label">Facility</span>
                <span class="data-value">{location}</span>
            </div>
            <div class="data-field">
                <span class="data-label">Security Level</span>
                <span class="data-value" style="color: {COLORS['warning'] if location_security == 'ALPHA' else COLORS['text']};">
                    {location_security}
                </span>
            </div>
            <div class="data-field">
                <span class="data-label">Hire Date</span>
                <span class="data-value">{hire_date}</span>
            </div>
            <div class="data-field">
                <span class="data-label">Facility Access</span>
                <span class="data-value" style="color: {COLORS['success'] if has_facility else COLORS['text_muted']};">
                    {'LEVEL-4 AUTHORIZED' if has_facility else 'STANDARD ONLY'}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_security_status(scl: int):
    """Renders the current security status panel"""
    scl_color = SCL_COLORS.get(scl, SCL_COLORS[1])
    
    status_html = f"""
    <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['surface_light']}; 
                border-radius: 4px; padding: 0.75rem; margin-top: 1rem;">
        <div style="font-size: 0.65rem; color: {COLORS['text_muted']}; letter-spacing: 1px; margin-bottom: 0.5rem;">
            SECURITY STATUS
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="color: {COLORS['text']}; font-size: 0.8rem;">Clearance Active</span>
            <span style="width: 10px; height: 10px; border-radius: 50%; background-color: {scl_color}; 
                         box-shadow: 0 0 8px {scl_color};"></span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.5rem;">
            <span style="color: {COLORS['text']}; font-size: 0.8rem;">Monitoring</span>
            <span style="width: 10px; height: 10px; border-radius: 50%; background-color: {COLORS['primary']}; 
                         animation: pulse 2s infinite;"></span>
        </div>
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)


def render_sidebar(employee: Dict[str, Any]):
    """Renders the complete sidebar with Employee Dossier"""
    with st.sidebar:
        render_logo()
        render_employee_card(employee)
        render_security_status(employee.get('clearance_level', 1))
        
        # Footer
        st.markdown(f"""
        <div style="position: fixed; bottom: 0; left: 0; width: inherit; padding: 0.5rem; 
                    background-color: {COLORS['surface']}; border-top: 1px solid {COLORS['surface_light']};
                    font-size: 0.6rem; color: {COLORS['text_muted']}; text-align: center;">
            U-SIOP v2.0 | © Umbrella Corp.
        </div>
        """, unsafe_allow_html=True)


def render_terminal_header():
    """Renders the terminal header with system info"""
    header_html = f"""
    <div class="terminal-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: {COLORS['primary']}; font-weight: 600;">U-SIOP TERMINAL</span>
                <span style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-left: 1rem;">
                    Security-Integrated Onboarding Protocol
                </span>
            </div>
            <div style="font-size: 0.7rem; color: {COLORS['text_muted']};">
                <span class="status-indicator" style="background-color: {COLORS['success']};"></span>
                CONNECTED
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def typewriter_effect(text: str, speed: float = 0.01):
    """
    Simulates a typewriter effect for AI responses.
    Creates the feel of secure data transmission.
    """
    placeholder = st.empty()
    displayed_text = ""
    
    # Process text in chunks for performance
    chunk_size = 5
    for i in range(0, len(text), chunk_size):
        displayed_text += text[i:i+chunk_size]
        placeholder.markdown(displayed_text)
        time.sleep(speed)
    
    return placeholder


def render_chat_message(role: str, content: str, use_typewriter: bool = False):
    """
    Renders a chat message with proper styling.
    Optionally applies typewriter effect for AI messages.
    """
    avatar = "☂️" if role == "ai" else "👤"
    
    with st.chat_message(role, avatar=avatar):
        if use_typewriter and role == "ai":
            typewriter_effect(content)
        else:
            st.markdown(content)


def render_chat_interface(messages: list, assistant, welcome_message: str = None):
    """
    Renders the complete chat interface.
    Handles message display, input, and response generation.
    """
    render_terminal_header()
    
    # Create a container for messages with fixed layout
    chat_container = st.container()
    
    with chat_container:
        # Display message history
        for message in messages:
            role = message.get("role", "ai")
            content = message.get("content", "")
            render_chat_message(role, content, use_typewriter=False)
    
    # Chat input at the bottom
    if prompt := st.chat_input("Enter your inquiry...", key="chat_input"):
        # Add user message
        messages.append({"role": "human", "content": prompt})
        render_chat_message("human", prompt)
        
        # Generate and display AI response
        with st.spinner(""):  # Hidden spinner
            response = assistant.get_response(prompt)
        
        messages.append({"role": "ai", "content": response})
        render_chat_message("ai", response, use_typewriter=True)
        
        # Rerun to update the interface
        st.rerun()

def format_welcome_message(template: str, employee: Dict[str, Any]) -> str:
    """Formats the welcome message with employee data"""
    try:
        return template.format(
            employee_full_name=f"{employee.get('name', 'Unknown')} {employee.get('lastname', '')}",
            employee_id=str(employee.get('employee_id', 'N/A'))[:8],
            department=employee.get('department', 'Unassigned'),
            position=employee.get('position', 'Unassigned'),
            location=employee.get('location', 'Unknown'),
            location_security_level=employee.get('location_security_level', 'GAMMA'),
            clearance_level=employee.get('clearance_level', 1)
        )
    except KeyError as e:
        return f"Welcome to U-SIOP. Employee data incomplete: {e}"

def initialize_ui(employee: Dict[str, Any], messages: list, assistant, welcome_message_template: str):
    """
    Main function to initialize the complete U-SIOP Terminal UI.
    Call this from app.py after setting up the assistant.
    """
    # Apply custom styling
    apply_custom_style()
    
    # Render sidebar with employee dossier
    render_sidebar(employee)
    
    # Initialize messages with welcome message if empty
    if not messages:
        formatted_welcome = format_welcome_message(welcome_message_template, employee)
        messages.append({"role": "ai", "content": formatted_welcome})
    
    # Render chat interface
    render_chat_interface(messages, assistant, welcome_message_template)