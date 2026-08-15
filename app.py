import streamlit as st
import json
from transformers import pipeline

# Load the pipeline once with caching
@st.cache_resource
def load_pipeline():
    # Use CPU, small model
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-small",
        device=-1,  # CPU
        max_length=200
    )

pipe = load_pipeline()

def generate_text(prompt: str) -> str:
    result = pipe(prompt, max_new_tokens=150, do_sample=False)[0]['generated_text']
    return result.strip()

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

    def write_summary(self, facts, query):
        prompt = f"Facts: {' '.join(facts)}. Answer: '{query}' in one short paragraph."
        return generate_text(prompt)

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

        facts = []
        raw_results = []
        for step in steps:
            self._circuit_breaker()
            if step == "search":
                # Simulated search – replace with real API later
                if "python" in query.lower():
                    raw_results = ["Python is a programming language.", "Python is interpreted."]
                elif "ai" in query.lower():
                    raw_results = ["AI is artificial intelligence.", "AI includes machine learning."]
                else:
                    raw_results = [f"Result for {query}"]
                self.log.append({"step": "search", "data": raw_results})
            elif step == "extract":
                extracted = [r.split('.')[0] for r in raw_results if r]
                facts.extend(extracted)
                self.log.append({"step": "extract", "data": extracted})
            elif step == "write":
                summary = self.write_summary(facts, query)
                self.log.append({"step": "write", "data": summary})
                return {"answer": summary, "log": self.log, "status": "success"}
        return {"answer": "No summary.", "log": self.log, "status": "incomplete"}

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
