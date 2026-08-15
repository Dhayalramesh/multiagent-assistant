import gradio as gr
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_text(prompt: str, max_new_tokens=150) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tokenizer.eos_token_id)
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

def run_agent(query):
    agent = ResearchAssistant()
    result = agent.run(query)
    return result.get("answer", "No answer"), json.dumps(result.get("log", []), indent=2)

with gr.Blocks(title="Multi-Agent Research Assistant") as demo:
    gr.Markdown("# Multi‑Agent Research Assistant")
    query_input = gr.Textbox(label="Your Question", placeholder="e.g., What is Python?")
    submit_btn = gr.Button("Run Agent")
    answer_output = gr.Textbox(label="Answer", lines=3)
    log_output = gr.Textbox(label="Step‑by‑Step Log", lines=10)
    submit_btn.click(fn=run_agent, inputs=query_input, outputs=[answer_output, log_output])

demo.launch()