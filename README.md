# 🔍 Multi‑Agent Research Assistant

A production‑ready, multi‑agent system that answers general‑knowledge questions by **planning**, **searching Wikipedia**, **extracting** key facts, and **summarising** the results. Built with **Streamlit**, **Hugging Face Transformers (Flan‑T5)**, and the **Wikipedia REST API**.

---

## 🚀 Live Demo

**[👉 Click here to run the live demo](https://multiagent-assistant-gdrjlkhxxckpwmibqwqstz.streamlit.app/#answer)**  

## ✨ Features

- **Natural language understanding** – handles questions like `"what is Python"`, `"who is Einstein"`.
- **Wikipedia integration** – fetches real‑time summaries using the Wikipedia REST API.
- **Smart query cleaning** – removes common prefixes (`"what is "`, `"who is "`, etc.) and handles special cases (`C++`, `AI`).
- **Fallback search** – if a direct page match fails, the agent uses the Wikipedia Search API.
- **Step‑by‑step logging** – every action (plan, search, extract, write) is logged for full transparency and debugging.
- **Guardrails** – input validation, circuit breaker (max 5 steps), and error handling.
- **Lightweight & fast** – uses `flan‑t5‑small` for optional summarisation (the live demo uses direct Wikipedia extracts for speed).

---

## 🏗️ Architecture
User Question
│
▼
┌─────────────┐
│ Plan │ → Decide the order of steps (search → extract → write)
└─────────────┘
│
▼
┌─────────────┐
│ Search │ → Query Wikipedia (REST API) and retrieve facts
└─────────────┘
│
▼
┌─────────────┐
│ Extract │ → Clean and structure the retrieved facts
└─────────────┘
│
▼
┌─────────────┐
│ Write │ → Generate a concise answer (using Flan‑T5 or direct extract)
└─────────────┘
│
▼
Answer


---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| LLM (optional summarisation) | [Flan‑T5‑small](https://huggingface.co/google/flan-t5-small) |
| Data source | [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/) |
| Deployment | [Streamlit Cloud](https://streamlit.io/cloud) |
| Language | Python 3.9+ |

---

## 🧪 How to Run the Demo (Locally)

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Dhayalramesh/multiagent-assistant.git
   cd multiagent-assistant/project1_multiagent

 2.  Install dependencies
 pip install -r requirements.txt

 3.Run the Streamlit app
 streamlit run app.py

 project1_multiagent/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md  
