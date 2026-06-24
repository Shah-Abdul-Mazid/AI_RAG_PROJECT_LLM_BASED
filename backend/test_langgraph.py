import asyncio
import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.supervisor import supervisor_agent

async def main():
    print("=== TESTING RAG ROUTE ===")
    rag_query = "What is our leave policy?"
    rag_result = await supervisor_agent.process_request(rag_query, provider="openai")
    print(f"Query: {rag_query}")
    print("Logs:", rag_result.get("agent_logs"))
    print("Answer:", rag_result.get("answer"))
    
    print("\n=== TESTING LIVE DATA ROUTE ===")
    # live_data_agent.can_handle usually looks for phrases like "stock", "weather", etc. Let's assume stock.
    live_query = "What is the stock price of AAPL?"
    live_result = await supervisor_agent.process_request(live_query, provider="openai")
    print(f"Query: {live_query}")
    print("Logs:", live_result.get("agent_logs"))
    print("Answer:", live_result.get("answer"))
    
    print("\n=== TESTING EXPLAIN ROUTE ===")
    explain_query = "Explain applicant 8"
    explain_result = await supervisor_agent.process_request(explain_query, provider="openai")
    print(f"Query: {explain_query}")
    print("Logs:", explain_result.get("agent_logs"))
    print("SHAP Values:", explain_result.get("shap"))
    print("LIME Weights:", explain_result.get("lime"))
    print("Fairness Summary:", explain_result.get("fairness"))
    print("Answer:", explain_result.get("answer"))

if __name__ == "__main__":
    asyncio.run(main())
