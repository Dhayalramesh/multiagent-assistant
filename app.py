import streamlit as st
import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model and tokenizer (CPU)
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
        # Simpler plan – we can hardcode the steps to avoid LLM confusion
        # But we keep the LLM plan for flexibility with a better prompt
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
        # Fallback: use a fixed plan
        return {"plan": ["search", "extract", "write"]}

    def _search(self, query):
        """Enhanced simulated search with more facts."""
        q_lower = query.lower()
        if "python" in q_lower:
            return [
                "Python is a high-level, interpreted programming language.",
                "Python is known for its simplicity and readability.",
                "Python is widely used in data science, web development, and automation."
            ]
        elif "java" in q_lower:
            return [
                "Java is a high-level, class-based, object-oriented programming language.",
                "Java is designed to have as few implementation dependencies as possible.",
                "Java is used for building enterprise-scale applications and Android mobile apps."
            ]
        elif "ai" in q_lower or "artificial intelligence" in q_lower:
            return [
                "Artificial Intelligence (AI) is the simulation of human intelligence in machines.",
                "AI includes machine learning, deep learning, and natural language processing.",
                "AI is used in robotics, healthcare, finance, and autonomous vehicles."
            ]
        else:
            return [f"Result for {query}: {query} is a broad topic."]

    def _extract(self, results, query):
        """Extract key sentences from search results."""
        # For simplicity, we just take the first sentence of each result.
        extracted = []
        for r in results:
            # Split by period and take first non-empty part
            sentences = r.split('.')
            if sentences:
                first = sentences[0].strip()
                if first:
                    extracted.append(first)
        return extracted

    def write_summary(self, facts, query):
        """Generate a concise answer using the LLM, with a better prompt."""
        if not facts:
            return "No facts found to answer your question."
        # Combine facts into a concise context
        context = " ".join(facts)
        prompt = f"Question: {query}\nFacts: {context}\nAnswer the question concisely based on the facts."
        response = generate_text(prompt, max_new_tokens=100)
        # If response is too short or empty, fall back to the first fact
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

# Streamlit UI
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
