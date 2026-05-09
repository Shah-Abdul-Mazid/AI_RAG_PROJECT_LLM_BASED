from app.utils.compliance import check_compliance

class ComplianceAgent:
    def run(self, answer: str):
        print("Compliance Agent active...")
        return check_compliance(answer)

compliance_agent = ComplianceAgent()
