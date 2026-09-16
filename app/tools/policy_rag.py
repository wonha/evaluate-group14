"""Vertex AI Search Policy Knowledge Base (RAG Engine) backed by Altostrat Singapore Policy Handbook."""
import os
import re
from typing import Dict, Any, List
from app.models import PolicyChunk, GroundedAnswer

HANDBOOK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "altostrat_policy_handbook.md")
DOC_BASE_URL = "https://docs.google.com/document/d/15T1HUkkO3GnoT2_SJW1YIzhjc-LG-GIY7rvlXMGon5Y/edit"

def load_policy_corpus() -> List[Dict[str, Any]]:
    corpus = []
    if os.path.exists(HANDBOOK_FILE):
        with open(HANDBOOK_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        subsections = re.split(r'\n(?=\*\*\d+\.\d+\s+)', content)
        for sub in subsections:
            header_match = re.search(r'^\*\*(\d+\.\d+)\s+([^*]+)\*\*', sub.strip())
            if header_match:
                sec_num = header_match.group(1)
                sec_title = header_match.group(2).strip()
                clean_content = sub.strip()
                corpus.append({
                    "doc_id": f"ALTO-SG-{sec_num}",
                    "title": f"Altostrat Singapore Policy - {sec_title}",
                    "section": f"Section {sec_num} ({sec_title})",
                    "content": clean_content,
                    "url": f"{DOC_BASE_URL}#heading=h.{sec_num.replace('.', '')}"
                })
                
    # Default fallbacks if handbook file is missing
    if not corpus:
        corpus = [
            {
                "doc_id": "ALTO-SG-1.1",
                "title": "Altostrat Sick Leave Policy",
                "section": "Section 1.1 Outpatient Sick Leave",
                "content": "Eligible employees receive up to 14 days of paid outpatient sick leave and 46 days of hospitalization leave per year.",
                "url": DOC_BASE_URL
            },
            {
                "doc_id": "ALTO-SG-1.2",
                "title": "Altostrat Vacation Leave Policy",
                "section": "Section 1.2 Paid Vacation Leave",
                "content": "Vacation entitlement is 20 days for 1-6 years of service, 21 days for 7-10 years, and 22 days for 11+ years.",
                "url": DOC_BASE_URL
            }
        ]
    return corpus

class PolicyRAGService:
    def __init__(self):
        self.corpus = load_policy_corpus()

    def search_policy_documents(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        q_lower = query.lower()
        query_words = set(re.findall(r'\w+', q_lower))
        stopwords = {"what", "is", "the", "for", "a", "an", "and", "or", "to", "in", "of", "how", "many", "can", "i", "my", "do", "we", "our", "are", "on", "please"}
        keywords = [w for w in query_words if w not in stopwords and len(w) > 2]
        
        matches = []
        for doc in self.corpus:
            doc_text = (doc["title"] + " " + doc["section"] + " " + doc["content"]).lower()
            
            # 1. Exact phrase boost
            score = 0.0
            if q_lower in doc_text:
                score += 0.5
                
            # 2. Token overlap score
            matched_kws = [kw for kw in keywords if kw in doc_text]
            if keywords:
                overlap_ratio = len(matched_kws) / len(keywords)
                score += overlap_ratio * 0.5
                
            # 3. Title/Section match boost
            title_lower = (doc["title"] + " " + doc["section"]).lower()
            for kw in keywords:
                if kw in title_lower:
                    score += 0.15
                    
            if score > 0.25:
                normalized_score = min(0.98, max(0.4, score))
                matches.append({
                    "document_title": doc["title"],
                    "section": doc["section"],
                    "text_content": doc["content"][:600] + ("..." if len(doc["content"]) > 600 else ""),
                    "source_url": doc["url"],
                    "similarity_score": round(normalized_score, 2)
                })
                
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_chunks = matches[:max_results]
        max_score = top_chunks[0]["similarity_score"] if top_chunks else 0.0
        
        return {
            "query": query,
            "chunks": top_chunks,
            "max_grounding_score": max_score,
            "is_grounded": max_score >= 0.70
        }

policy_rag = PolicyRAGService()

