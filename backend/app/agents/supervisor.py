from app.core.config import settings
from app.agents.retriever import retriever_agent
from app.agents.generator import generator_agent
from app.agents.compliance import compliance_agent
from app.agents.live_data import live_data_agent

class SupervisorAgent:
    """The Master Orchestrator that manages the Agentic Workflow"""
    
    async def process_request(self, query: str):
        logs = [f"Supervisor: Orchestrating workflow using {settings.LLM_PROVIDER.upper()}"]

        if live_data_agent.can_handle(query):
            try:
                live_answer = live_data_agent.run(query)
                check = compliance_agent.run(live_answer["answer"])
                if not check["compliant"]:
                    live_answer["answer"] = "REDACTED: Response blocked by enterprise security policy."
                    live_answer["agent_logs"].append("SYSTEM ALERT: Compliance violation detected!")
                return live_answer
            except Exception as exc:
                logs.append(f"Live Data Agent: API lookup failed ({exc})")
                logs.append("Supervisor: Falling back to enterprise knowledge retrieval")
        
        # 1. Delegate to Retriever
        context, sources = retriever_agent.run(query)
        logs.append("Retriever Agent: Context retrieved from Pinecone Cloud")
        
        # 2. Delegate to Generator
        answer = generator_agent.run(query, context)
        logs.append("Generator Agent: Synthesized answer from retrieved data")
        
        # 3. Delegate to Compliance
        check = compliance_agent.run(answer)
        logs.append("Compliance Agent: Security & PII check complete")
        
        if not check["compliant"]:
            answer = "REDACTED: Response blocked by enterprise security policy."
            logs.append("SYSTEM ALERT: Compliance violation detected!")

        return {
            "answer": answer,
            "sources": sources,
            "agent_logs": logs
        }

supervisor_agent = SupervisorAgent()
