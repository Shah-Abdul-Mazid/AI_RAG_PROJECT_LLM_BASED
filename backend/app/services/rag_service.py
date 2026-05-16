from app.agents.supervisor import supervisor_agent

class RAGService:
    async def answer_query(self, query: str, provider: str = None):
        # Simply delegate to the Supervisor Agent
        return await supervisor_agent.process_request(query, provider=provider)

rag_service = RAGService()
