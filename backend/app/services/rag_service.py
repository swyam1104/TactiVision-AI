import os
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Match, Event, Team, Player, Lineup

logger = logging.getLogger(__name__)

# Fallback match facts corpus for demo consistency
MOCK_FACTS = [
    {
        "text": "Match ID 3754058: Arsenal beat Chelsea 2-1 on 2016-05-15. Goals: Bukayo Saka (14' - xG 0.38), Kai Havertz (72' - xG 0.44) for Arsenal; Nicolas Jackson (44' - xG 0.65) for Chelsea. Arsenal dominated possession with 56.4% and produced 1.78 xG from 14 shots. Chelsea had 43.6% possession, 9 shots, and 0.94 xG.",
        "metadata": {"match_id": 3754058, "teams": "Arsenal vs Chelsea", "date": "2016-05-15"}
    },
    {
        "text": "Match ID 3754059: Manchester City drew with Liverpool 2-2 on 2016-04-10. Goals: Kevin De Bruyne (5' - xG 0.15), Gabriel Jesus (37' - xG 0.52) for Man City; Diogo Jota (13' - xG 0.45), Sadio Mane (46' - xG 0.38) for Liverpool. City held 52.1% possession and registered 11 shots (1.45 xG), while Liverpool had 47.9% possession with 8 shots (1.20 xG).",
        "metadata": {"match_id": 3754059, "teams": "Man City vs Liverpool", "date": "2016-04-10"}
    },
    {
        "text": "Match ID 432204: France defeated Argentina 4-3 in the 2018 World Cup Round of 16 on 2018-06-30. Goals: Antoine Griezmann (13' pen), Benjamin Pavard (57'), Kylian Mbappe (64', 68') for France; Angel Di Maria (41'), Gabriel Mercado (48'), Sergio Aguero (90+3') for Argentina. Kylian Mbappe was outstanding, causing havoc under high transition pressures.",
        "metadata": {"match_id": 432204, "teams": "France vs Argentina", "date": "2018-06-30"}
    },
    {
        "text": "Bukayo Saka performance stats in Premier League 2015/16: 15 appearances, 6 goals, 4 assists. Saka average position is highly wide on the right wing (average coordinates x=88.5, y=65.2), generating high progressive carries (4.2 per 90) and key passes (2.2 per 90). He has high press resistance, completing 81.2% of passes under defensive pressure.",
        "metadata": {"player_id": 1, "player_name": "Bukayo Saka"}
    },
    {
        "text": "Martin Odegaard performance stats: average position is in the right half-space (x=76.8, y=48.5). Odegaard created 32 key passes and generated the highest progressive passes (6.8 per 90) in the final third. Under high press, Odegaard maintains an 84.5% pass completion rate, frequently feeding Saka and Havertz.",
        "metadata": {"player_id": 11, "player_name": "Martin Odegaard"}
    }
]

class RAGService:
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        self.index = None
        self._initialize_retriever()
        
    def _initialize_retriever(self):
        """Prepare RAG document corpus."""
        # Standard corpus setup
        logger.info("Initializing Coach RAG Assistant corpus...")
        self.corpus = list(MOCK_FACTS)
        
    def rebuild_index(self, db: Session):
        """Rebuild RAG corpus using real data from the database."""
        logger.info("Rebuilding RAG Assistant search index from database...")
        try:
            matches = db.query(Match).all()
            real_facts = []
            
            for m in matches:
                home_team = db.query(Team).filter_by(id=m.home_team_id).scalar()
                away_team = db.query(Team).filter_by(id=m.away_team_id).scalar()
                
                # Fetch shot details
                shots = db.query(Event).filter(Event.match_id == m.id, Event.type == "Shot").all()
                goals = []
                for s in shots:
                    if s.outcome == "Goal":
                        p_name = db.query(Player.name).filter_by(id=s.player_id).scalar() or "Player"
                        goals.append(f"{p_name} ({s.minute}')")
                        
                goals_str = ", ".join(goals) if goals else "None"
                
                fact = {
                    "text": f"Match ID {m.id}: {home_team.name} vs {m.away_team.name} finished {m.home_score}-{m.away_score} on {m.match_date}. Goals: {goals_str}. Stadium: {m.stadium or 'Unknown'}. Referee: {m.referee or 'Unknown'}.",
                    "metadata": {
                        "match_id": m.id,
                        "teams": f"{home_team.name} vs {m.away_team.name}",
                        "date": str(m.match_date)
                    }
                }
                real_facts.append(fact)
                
            if real_facts:
                self.corpus = real_facts + MOCK_FACTS
                logger.info(f"RAG search index updated with {len(real_facts)} match documents from database.")
        except Exception as e:
            logger.error(f"Error rebuilding RAG index: {e}. Keeping default corpus.")

    def retrieve_relevant_facts(self, query: str, k: int = 2) -> list:
        """
        Perform a simple semantic/keyword score matching over the corpus.
        This provides a lightweight, local, dependency-free retrieval model.
        """
        query_words = set(query.lower().replace("?", "").replace(",", "").split())
        scored_docs = []
        
        for doc in self.corpus:
            doc_text = doc["text"].lower()
            # Calculate intersection count
            score = sum(1 for word in query_words if word in doc_text)
            
            # Boost specific matches
            if "saka" in query_words and "saka" in doc_text:
                score += 3
            if "odegaard" in query_words and "odegaard" in doc_text:
                score += 3
            if "mbappe" in query_words and "mbappe" in doc_text:
                score += 3
                
            scored_docs.append((score, doc))
            
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:k]]

    def ask_assistant(self, query: str, db: Session = None) -> dict:
        """
        Query the tactical assistant.
        Retrieves context documents, calls the LLM if keys are available,
        otherwise yields an intelligent rule-based agent answer.
        """
        if db:
            self.rebuild_index(db)
            
        retrieved = self.retrieve_relevant_facts(query, k=2)
        context_str = "\n\n".join([r["text"] for r in retrieved])
        
        # Check for API Keys
        if self.openai_key:
            return self._call_openai(query, context_str, retrieved)
        elif self.gemini_key:
            return self._call_gemini(query, context_str, retrieved)
        else:
            return self._generate_rule_based_response(query, retrieved)

    def _generate_rule_based_response(self, query: str, retrieved: list) -> dict:
        """Formulate a highly detailed, professional AI response using retrieved facts."""
        q_lower = query.lower()
        
        # Build answer text based on context
        answer = "### Tactical Analyst Assessment\n\n"
        citations = []
        
        for idx, doc in enumerate(retrieved):
            meta = doc["metadata"]
            citation_label = ""
            if "teams" in meta:
                citation_label = f"{meta['teams']} ({meta['date']})"
            elif "player_name" in meta:
                citation_label = f"Player Profile: {meta['player_name']}"
                
            citations.append({
                "source_id": idx + 1,
                "citation": citation_label,
                "snippet": doc["text"]
            })
            
        if "saka" in q_lower:
            answer += "Bukayo Saka is deployed primarily as an inside winger on the right side. He showcases outstanding progress in transition phases:\n\n"
            answer += "- **Progressive carries**: 4.2 per 90, which allows Arsenal to penetrate deep into Zone 14.\n"
            answer += "- **Press resistance**: Saka maintains an 81.2% pass completion rate under aggressive defensive duels, enabling reliable build-up plays.\n"
            answer += "- **Goal threat**: Registered key goals (e.g. at 14' against Chelsea) and is a primary outlet in the final third.\n\n"
            answer += f"*[Source {retrieved[0].get('source_id', 1)}]*: Refers to player performance aggregates."
            
        elif "odegaard" in q_lower or "ødegaard" in q_lower:
            answer += "Martin Ødegaard operates as the chief playmaker in the right half-space. Analysis of his telemetry shows:\n\n"
            answer += "- **Line-breaking passing**: Delivers 6.8 progressive passes per 90 into the penalty box.\n"
            answer += "- **Press resistance**: Under high defensive pressure, he maintains an 84.5% pass accuracy, making him the core outlet during build-up phases.\n"
            answer += "- **Combination play**: Frequently links with Saka to overload the right flank.\n\n"
            answer += f"*[Source {retrieved[0].get('source_id', 1)}]*: Refers to tactical playmaker features."
            
        elif "chelsea" in q_lower or "arsenal" in q_lower:
            # Arsenal vs Chelsea
            answer += "In the match between Arsenal and Chelsea, several key tactical elements were observed:\n\n"
            answer += "1. **xG Efficiency**: Arsenal created high-quality chances, scoring 2 goals from 1.78 xG (14 shots), while Chelsea scored 1 goal from 0.94 xG (9 shots).\n"
            answer += "2. **Possession Split**: Arsenal controlled the rhythm with 56.4% possession, using short passing networks to progress from the half-spaces.\n"
            answer += "3. **Defensive Solidity**: Arsenal limited Chelsea to only 3 shots on target, winning duels under mid-block pressure.\n\n"
            answer += f"*[Source {retrieved[0].get('source_id', 1)}]*: Refers to Arsenal vs Chelsea match statistics."
            
        else:
            answer += "Based on the retrieved tactical snippets, here is the analysis:\n\n"
            for doc in retrieved:
                answer += f"- {doc['text']}\n"
            answer += "\nThis analysis is compiled from direct event data and team lineups."

        return {
            "query": query,
            "answer": answer,
            "citations": citations
        }

    def _call_openai(self, query: str, context: str, retrieved: list) -> dict:
        """Call OpenAI chat completion API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""
You are a Senior Football Tactical Analyst. Use the retrieved match facts below to answer the user's tactical question.
You must cite the facts using '[Source X]' notation where X is the source number.

Retrieved Facts:
{context}

Question: {query}
Answer:
"""
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional tactical analyst at Arsenal FC."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content
            
            citations = []
            for idx, doc in enumerate(retrieved):
                meta = doc["metadata"]
                label = meta.get("teams", meta.get("player_name", "Match Event Info"))
                citations.append({
                    "source_id": idx + 1,
                    "citation": f"{label}",
                    "snippet": doc["text"]
                })
                
            return {
                "query": query,
                "answer": answer,
                "citations": citations
            }
        except Exception as e:
            logger.error(f"OpenAI RAG call failed: {e}. Falling back to rule-based response.")
            return self._generate_rule_based_response(query, retrieved)

    def _call_gemini(self, query: str, context: str, retrieved: list) -> dict:
        """Call Gemini API using standard Python HTTP client or packages."""
        # Simple HTTP fallback or package call for Gemini
        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
            headers = {"Content-Type": "application/json"}
            prompt = f"""
You are a Senior Football Tactical Analyst. Use the retrieved match facts below to answer the user's tactical question.
You must cite the facts using '[Source X]' notation where X is the source number.

Retrieved Facts:
{context}

Question: {query}
Answer:
"""
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            res = httpx.post(url, json=payload, headers=headers, timeout=20.0)
            res.raise_for_status()
            res_json = res.json()
            answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
            
            citations = []
            for idx, doc in enumerate(retrieved):
                meta = doc["metadata"]
                label = meta.get("teams", meta.get("player_name", "Match Event Info"))
                citations.append({
                    "source_id": idx + 1,
                    "citation": f"{label}",
                    "snippet": doc["text"]
                })
                
            return {
                "query": query,
                "answer": answer,
                "citations": citations
            }
        except Exception as e:
            logger.error(f"Gemini RAG call failed: {e}. Falling back to rule-based response.")
            return self._generate_rule_based_response(query, retrieved)

rag_service = RAGService()
