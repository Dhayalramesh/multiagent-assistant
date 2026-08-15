import streamlit as st
import json
import torch
import requests
from urllib.parse import quote
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------- VERSION CHECK ----------
st.write("🚀 VERSION 5.0 - Live Wikipedia Search")

# Test Wikipedia API
try:
    test_response = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/Python", timeout=5)
    if test_response.status_code == 200:
        st.success("✅ Wikipedia API is working!")
    else:
        st.error(f"❌ Wikipedia API error: {test_response.status_code}")
except Exception as e:
    st.error(f"❌ Network error: {e}")

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    model.to("cpu")
    return tokenizer, model

tokenizer, model = load_model()

def generate_text(prompt: str, max_new_tokens=150) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to("cpu") for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# ---------- AGENT ----------
class ResearchAssistant:
    MAX_STEPS = 5
    def __init__(self):
        self.step_count = 0
        self.log = []

    def _validate_input(self, query):
        if not query.strip():
            raise ValueError("Empty query")
        return query.strip()

    def _circuit_breaker(self):
        self.step_count += 1
        if self.step_count > self.MAX_STEPS:
            raise RuntimeError("Circuit breaker: exceeded max steps")

    def plan(self, query):
        prompt = f"Given: '{query}', plan a research strategy: search, extract, write. Output JSON with 'plan' list."
        response = generate_text(prompt)
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                plan = json.loads(response[start:end])
                if "plan" in plan:
                    return plan
        except:
            pass
        return {"plan": ["search", "extract", "write"]}

    def _clean_query(self, query):
        prefixes = [
            "what is ", "what are ", "what's ",
            "who is ", "who are ", "who's ",
            "where is ", "where are ",
            "when is ", "when was ",
            "how to ", "how do ",
            "tell me about ", "explain ",
            "define ", "definition of "
        ]
        cleaned = query.lower().strip()
        if cleaned.endswith('?'):
            cleaned = cleaned[:-1]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        if not cleaned:
            cleaned = query.strip()
        
        cleaned = cleaned.strip()
        # Special cases
        if cleaned.lower() == "ai":
            return "AI"
        if cleaned.lower() == "c++":
            return "C++"
        if cleaned.lower() == "c#":
            return "C#"
        if cleaned.lower() == "r":
            return "R (programming language)"
        if cleaned.lower() == "python":
            return "Python (programming language)"
        if cleaned.lower() == "java":
            return "Java (programming language)"
        
        return cleaned.capitalize()

    def _search(self, query):
        """Search Wikipedia for a concise summary."""
        try:
            search_term = self._clean_query(query)
            encoded_term = quote(search_term)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_term}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "extract" in data:
                    summary = data["extract"]
                    sentences = summary.split('. ')
                    facts = [s.strip() + '.' for s in sentences[:3] if s.strip()]
                    if facts:
                        return facts
            
            # Fallback
            fallback_term = quote(query.strip())
            fallback_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{fallback_term}"
            response = requests.get(fallback_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "extract" in data:
                    summary = data["extract"]
                    sentences = summary.split('. ')
                    facts = [s.strip() + '.' for s in sentences[:3] if s.strip()]
                    if facts:
                        return facts
            
            return [f"Wikipedia did not return a result for '{search_term}'. Please try a different query."]
        except Exception as e:
            return [f"Could not fetch info for '{query}': {str(e)}"]

    def _extract(self, results, query):
        return results

    def write_summary(self, facts, query):
        if not facts:
            return "No facts found to answer your question."
        context = " ".join(facts)
        prompt = f"Question: {query}\nFacts: {context}\nAnswer the question concisely based on the facts."
        response = generate_text(prompt, max_new_tokens=100)
        if len(response) < 5:
            return facts[0]
        return response

    def run(self, query):
        self.step_count = 0
        self.log = []
        try:
            query = self._validate_input(query)
        except Exception as e:
            return {"answer": "", "log": [{"error": str(e)}], "status": "error"}

        self._circuit_breaker()
        plan = self.plan(query)
        self.log.append({"step": "plan", "data": plan})
        steps = plan.get("plan", ["search", "extract", "write"])

        raw_results = []
        facts = []
        for step in steps:
            self._circuit_breaker()
            if step == "search":
                raw_results = self._search(query)
                self.log.append({"step": "search", "data": raw_results})
            elif step == "extract":
                facts = self._extract(raw_results, query)
                self.log.append({"step": "extract", "data": facts})
            elif step == "write":
                summary = self.write_summary(facts, query)
                self.log.append({"step": "write", "data": summary})
                return {"answer": summary, "log": self.log, "status": "success"}
        return {"answer": "No summary generated.", "log": self.log, "status": "incomplete"}

# ---------- UI ----------
st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")
st.title("🔍 Multi‑Agent Research Assistant")
st.markdown("Ask a question, and the agent will **plan → search → extract → write** a summary.")

query = st.text_input("Your Question", placeholder="e.g., What is Python?")
if st.button("Run Agent"):
    if query:
        with st.spinner("Agent is thinking..."):
            agent = ResearchAssistant()
            result = agent.run(query)
            answer = result.get("answer", "No answer")
            log = json.dumps(result.get("log", []), indent=2)
        st.success("Done!")
        st.subheader("Answer")
        st.write(answer)
        st.subheader("Step-by-Step Log")
        st.code(log, language="json")
    else:
        st.warning("Please enter a question.")
