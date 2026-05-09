import re

def check_compliance(text: str):
    """
    Enterprise Compliance Agent
    Checks for PII (Personally Identifiable Information) and security policy violations.
    """
    patterns = {
        "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        "phone": r'\+?\d[\d -]{8,}\d',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
    }
    
    violations = []
    for name, pattern in patterns.items():
        if re.search(pattern, text):
            violations.append(name)
            
    return {
        "compliant": len(violations) == 0,
        "violations": violations
    }
