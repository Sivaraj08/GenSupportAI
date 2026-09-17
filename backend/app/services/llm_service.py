import requests
import json
from ..config import settings

class LLMService:
    def __init__(self):
        self.endpoint = f"{settings.OLLAMA_URL}/api/generate"

    def compile_prompt(self, context_chunks: list, history: list, query: str) -> str:
        """
        Combines RAG context chunks, conversation history, and user query into the final prompt.
        """
        # Format context chunks
        formatted_context = ""
        if context_chunks:
            formatted_context = "\n\n".join([f"[Source Page {c['metadata'].get('page_num', 'Unknown')}]: {c['text']}" for c in context_chunks])
        else:
            formatted_context = "No documentation found for this query."

        # Format history
        formatted_history = ""
        for msg in history[-5:]: # limit history context window to last 5 messages
            sender_label = "User" if msg["sender"] == "user" else "AI"
            formatted_history += f"{sender_label}: {msg['content']}\n"

        # Create structured template
        prompt = (
            "System Prompt:\n"
            "You are the College Student Query Assistant, a helpful, polite administrative virtual assistant.\n"
            "Answer the student's question using ONLY the facts provided in the Context sections below.\n"
            "Guidelines for answering student queries:\n"
            "1. Provide clear, accurate, and structured answers based directly on the provided Context (such as course syllabus, calendars, certificates, and policies).\n"
            "2. When explaining schedules, dates, requirements, or syllabus modules, present them in a readable, bulleted format if appropriate.\n"
            "3. Do not assume or fabricate information. If the answer is not in the Context, follow the default fallback response.\n"
            "4. Do NOT mention page numbers, source files, row numbers, document names, or refer the student to external sections. Simply output the requested facts directly.\n"
            "If the Context does not contain the answer, reply exactly with:\n"
            "\"I am sorry, but I cannot locate that information in the official documentation. Would you like me to open a support ticket for our human agents?\"\n\n"
            "Context:\n"
            "---------------------\n"
            f"{formatted_context}\n"
            "---------------------\n\n"
            "Conversation History:\n"
            f"{formatted_history}\n"
            f"User Question: {query}\n"
            "AI Response:\n"
        )
        return prompt

    def generate_title(self, query: str) -> str:
        """
        Generates a 2-4 word summary of the query to act as the chat session title.
        """
        prompt = (
            "System Prompt:\n"
            "You are an assistant that summarizes user queries into extremely brief topic titles (maximum 2-4 words).\n"
            "Output ONLY the title. Do not include quotes, prefix text, or punctuation.\n"
            "Examples:\n"
            "Query: How do I apply for college admission?\n"
            "Title: College Admission\n"
            "Query: Need to get my bonafide certificate, what is the procedure?\n"
            "Title: Bonafide Certificate\n"
            "Query: When is the exam timetable releasing?\n"
            "Title: Exam Timetable\n\n"
            f"Query: {query}\n"
            "Title:"
        )
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 10
            }
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=settings.OLLAMA_TIMEOUT)
            if response.status_code == 200:
                title = response.json().get("response", "").strip()
                title = title.replace('"', '').replace("'", "").strip()
                if title:
                    return title
        except Exception as e:
            print(f"Ollama error during title generation: {e}")
        
        words = query.split()
        return " ".join(words[:3]) + "..." if len(words) > 3 else query

    def generate_response(self, context_chunks: list, history: list, query: str) -> str:
        """
        Sends compiled prompt to local Ollama API.
        Falls back to a polite error message if Ollama is not running.
        """
        prompt = self.compile_prompt(context_chunks, history, query)
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2, # low temperature for high factual accuracy
                "num_predict": 300  # limit output size
            }
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=settings.OLLAMA_TIMEOUT)
            if response.status_code == 200:
                result_json = response.json()
                return result_json.get("response", "").strip()
            else:
                return (
                    "I am sorry, but I encountered an error communicating with the local AI model (Ollama). "
                    "Please ask your system administrator to verify that Ollama is running and that the model is downloaded."
                )
        except requests.exceptions.RequestException as e:
            print(f"Ollama connection error: {e}")
            return (
                "I am sorry, but the local AI service is currently unreachable. "
                f"Please ensure Ollama is running locally at {settings.OLLAMA_URL} and the model '{settings.LLM_MODEL}' is active."
            )

llm_service = LLMService()
