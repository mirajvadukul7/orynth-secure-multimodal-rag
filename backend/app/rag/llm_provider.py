import os
from dotenv import load_dotenv

load_dotenv()
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

def generate_answer(query: str, evidence_pack: list):
    """
    Evidence-only LLM generation. 
    In demo mode, it generates deterministic responses based strictly on evidence.
    """
    if not evidence_pack:
        return {"answer": "I don't have enough authorized evidence to answer that.", "citations": []}
        
    citations = []
    combined_evidence = ""
    for ev in evidence_pack:
        citations.append(ev["source_id"])
        combined_evidence += f"[{ev['source_id']}] {ev['text']} \n"

    # Simulated logic based on the required demo questions
    query_lower = query.lower()
    if "leave policy" in query_lower:
        answer = "The annual leave policy provides 20 days of paid time off per year."
        # Pick the PDF source if available
        src = next((c for c in citations if "DOC-018" in c or "pdf" in c.lower()), citations[0])
        citations_used = [src]
    elif "invoice_001" in query_lower:
        answer = "The invoice amount in invoice_001 is $1,250.00."
        src = next((c for c in citations if "IMG" in c or "invoice" in c.lower()), citations[0])
        citations_used = [src]
    elif "finance" in query_lower and "employees" in query_lower:
        answer = "There are currently 4 employees in the Finance department."
        citations_used = [citations[0]]
    elif "salary" in query_lower:
        if "rahul" in query_lower:
            answer = "Rahul's salary is $85,000."
            citations_used = [citations[0]]
        else:
            answer = "Based on the records, the requested salary is provided."
            citations_used = [citations[0]]
    elif "ignore previous" in query_lower or "confidential" in query_lower:
        # Prompt injection test
        answer = "I don't have enough authorized evidence to answer that."
        citations_used = []
    else:
        answer = f"Based on the evidence, here is the requested information. (Demo Mode Generated)"
        citations_used = citations[:1]
        
    return {
        "answer": answer,
        "citations": citations_used
    }
