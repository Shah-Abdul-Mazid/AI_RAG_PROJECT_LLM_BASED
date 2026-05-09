from app.agents.supervisor import supervisor_agent

class RAGService:
    async def answer_query(self, query: str):
        # Simply delegate to the Supervisor Agent
        return await supervisor_agent.process_request(query)

rag_service = RAGService()
