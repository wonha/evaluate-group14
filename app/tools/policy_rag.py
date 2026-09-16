"""Vertex AI Search Policy Knowledge Base (RAG Engine)."""
from typing import Dict, Any, List
from app.models import PolicyChunk, GroundedAnswer

POLICY_CORPUS = [
    {
        "doc_id": "HR-POL-04",
        "title": "Bereavement Leave Policy",
        "section": "Section 3.2 - Entitlement Guidelines",
        "keywords": ["bereavement", "funeral", "death", "immediate family"],
        "content": "Employees are eligible for up to 5 consecutive days of paid Bereavement Leave in the event of the death of an immediate family member (spouse, child, parent, sibling). For extended family members, up to 3 days of paid leave is granted.",
        "url": "https://hr.corp.internal/policies/leave#bereavement"
    },
    {
        "doc_id": "HR-POL-08",
        "title": "Remote Work and Home Office Policy",
        "section": "Section 2.1 - Equipment Procurement",
        "keywords": ["remote", "monitor", "home office", "hardware", "desk", "peripheral"],
        "content": "Designated remote employees are entitled to request company-provided home office equipment, including one external 27-inch monitor, ergonomic keyboard, and mouse. Requests must be submitted via ServiceImmediately with a verified residential shipping address.",
        "url": "https://hr.corp.internal/policies/remote-work#equipment"
    },
    {
        "doc_id": "HR-POL-12",
        "title": "Medical and Sick Leave Policy",
        "section": "Section 1.1 - Outpatient and Short-Term Leave",
        "keywords": ["medical", "sick", "doctor", "short-term leave", "certificate"],
        "content": "Employees are provided with 10 days of paid sick leave annually. For consecutive absences exceeding 3 days, a valid medical certificate from a licensed physician must be submitted upon return. Manager access delegation is automatically routed via IT Service Desk.",
        "url": "https://hr.corp.internal/policies/medical-leave"
    },
    {
        "doc_id": "HR-POL-15",
        "title": "International Relocation Guidelines",
        "section": "Section 4.0 - European Transfers",
        "keywords": ["relocation", "london", "transfer", "moving allowance", "uk"],
        "content": "Employees approved for transfer to the London UK office are entitled to a tax-compliant relocation allowance of up to £5,000 GBP for moving expenses. Employees must update their WorkWeek address record and request local building access security badges.",
        "url": "https://hr.corp.internal/policies/relocation#london"
    },
    {
        "doc_id": "HR-EXP-02",
        "title": "Expense Reimbursement Guidelines",
        "section": "Section 5.3 - Tech Accessories",
        "keywords": ["expense", "headphone", "noise-canceling", "accessories"],
        "content": "Employees may expense noise-canceling headphones up to $150 USD once every two years if their role requires frequent audio conferencing or focused programming in shared environments.",
        "url": "https://hr.corp.internal/policies/expense#tech"
    }
]

class PolicyRAGService:
    def search_policy_documents(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        q_lower = query.lower()
        matches = []
        
        for doc in POLICY_CORPUS:
            score = 0.0
            for kw in doc["keywords"]:
                if kw in q_lower:
                    score += 0.35
            if score > 0:
                score = min(1.0, score + 0.3)
                matches.append({
                    "document_title": doc["title"],
                    "section": doc["section"],
                    "text_content": doc["content"],
                    "source_url": doc["url"],
                    "similarity_score": score
                })
                
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_chunks = matches[:max_results]
        
        max_score = top_chunks[0]["similarity_score"] if top_chunks else 0.0
        return {
            "query": query,
            "chunks": top_chunks,
            "max_grounding_score": max_score,
            "is_grounded": max_score >= 0.82
        }

policy_rag = PolicyRAGService()
