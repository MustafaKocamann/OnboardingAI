import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# ============================================================
# ROLE-DEPARTMENT-SCL MAPPING - Business Logic Consistency
# ============================================================
ROLE_DEPARTMENT_MAPPING = {
    "Research Scientist": {
        "department": "R&D",
        "scl": 3,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe", "Umbrella Asia"]
    },
    "Senior Research Lead": {
        "department": "R&D",
        "scl": 4,
        "allowed_locations": ["Raccoon City HQ"]
    },
    "Software Engineer": {
        "department": "IT",
        "scl": 2,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe", "Umbrella Asia", "Umbrella North America", "Umbrella South America"]
    },
    "IT Security Specialist": {
        "department": "IT",
        "scl": 3,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe"]
    },
    "Operations Manager": {
        "department": "Operations",
        "scl": 2,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe", "Umbrella Asia", "Umbrella North America", "Umbrella South America"]
    },
    "HR Specialist": {
        "department": "HR",
        "scl": 1,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe", "Umbrella North America"]
    },
    "HR Director": {
        "department": "HR",
        "scl": 2,
        "allowed_locations": ["Raccoon City HQ"]
    },
    "Security Officer": {
        "department": "Security",
        "scl": 4,
        "allowed_locations": ["Raccoon City HQ", "Umbrella Europe"]
    },
    "Junior Lab Technician": {
        "department": "R&D",
        "scl": 1,
        "allowed_locations": ["Umbrella Europe", "Umbrella Asia", "Umbrella North America", "Umbrella South America"]
    },
    "Facility Administrator": {
        "department": "Operations",
        "scl": 5,
        "allowed_locations": ["Raccoon City HQ"]
    }
}

# ============================================================
# LOCATION-SPECIFIC PROTOCOLS - Location-Based Security
# ============================================================
LOCATION_PROTOCOLS = {
    "Raccoon City HQ": {
        "security_level": "ALPHA",
        "has_underground_facility": True,
        "special_protocols": ["Protocol Omega", "Containment Level-4 Access"],
        "emergency_contact": "ext. 4-UMBRELLA"
    },
    "Umbrella Europe": {
        "security_level": "BETA",
        "has_underground_facility": False,
        "special_protocols": ["Standard Security"],
        "emergency_contact": "ext. EU-SECURE"
    },
    "Umbrella Asia": {
        "security_level": "BETA",
        "has_underground_facility": False,
        "special_protocols": ["Standard Security"],
        "emergency_contact": "ext. ASIA-SEC"
    },
    "Umbrella North America": {
        "security_level": "GAMMA",
        "has_underground_facility": False,
        "special_protocols": ["Remote Operations Protocol"],
        "emergency_contact": "ext. NA-OPS"
    },
    "Umbrella South America": {
        "security_level": "GAMMA",
        "has_underground_facility": False,
        "special_protocols": ["Remote Operations Protocol"],
        "emergency_contact": "ext. SA-OPS"
    }
}


def generate_employee_data(num_employees=5):
    """
    Generates consistent employee data:
    - Position and Department are matched
    - SCL is assigned based on role
    - Location is selected according to role
    """
    employees = []
    
    for _ in range(num_employees):
        # Select position and get related data
        position = random.choice(list(ROLE_DEPARTMENT_MAPPING.keys()))
        role_data = ROLE_DEPARTMENT_MAPPING[position]
        
        department = role_data["department"]
        scl = role_data["scl"]
        location = random.choice(role_data["allowed_locations"])
        
        # Get location protocols
        location_data = LOCATION_PROTOCOLS.get(location, {})
        
        employee = {
            "employee_id": fake.uuid4(),
            "name": fake.first_name(),
            "lastname": fake.last_name(),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "position": position,
            "department": department,
            "clearance_level": scl,
            "location": location,
            "location_security_level": location_data.get("security_level", "UNKNOWN"),
            "has_facility_access": location_data.get("has_underground_facility", False) and scl >= 4,
            "skills": random.sample([
                "Python", "Project Management", "Data Analysis", 
                "Genetic Research", "Cybersecurity", "Machine Learning",
                "Leadership", "Database Management", "Public Speaking",
                "Biohazard Handling", "Containment Protocols", "Crisis Management"
            ], k=random.randint(2, 5)),
            "hire_date": (
                datetime.now() - timedelta(days=random.randint(1, 365 * 10))
            ).strftime("%Y-%m-%d"),
            "supervisor": fake.name(),
            # CONFIDENTIAL FIELDS - These fields will be hidden in prompts
            "_confidential_salary": round(random.uniform(40000, 120000), 2),
            "_confidential_performance_score": round(random.uniform(1.0, 5.0), 1),
            "emergency_contact_ext": location_data.get("emergency_contact", "ext. 0-HELP")
        }
        
        employees.append(employee)
    
    return employees


def get_location_protocols(location: str) -> dict:
    """Return location-based security protocols"""
    return LOCATION_PROTOCOLS.get(location, {})


def get_role_requirements(position: str) -> dict:
    """Return role requirements"""
    return ROLE_DEPARTMENT_MAPPING.get(position, {})