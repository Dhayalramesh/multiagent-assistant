import streamlit as st
import requests
from urllib.parse import quote

st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")
st.title("🔍 Multi‑Agent Research Assistant")
st.markdown("Ask a question, and the agent will **search Wikipedia** and show the summary.")

# ---------- Helper: Clean query ----------
def clean_query(query):
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
    
    # Special cases
    cleaned = cleaned.strip()
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

# ---------- Main logic ----------
def get_wikipedia_summary(query):
    search_term = clean_query(query)
    encoded = quote(search_term)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "extract" in data:
                return data["extract"]
        return f"Could not find a Wikipedia page for '{search_term}'."
    except Exception as e:
        return f"Error fetching data: {e}"

# ---------- UI ----------
query = st.text_input("Your Question", placeholder="e.g., What is Python?")
if st.button("Run Agent"):
    if query:
        with st.spinner("Searching Wikipedia..."):
            answer = get_wikipedia_summary(query)
        st.success("Done!")
        st.subheader("Answer")
        st.write(answer)
    else:
        st.warning("Please enter a question.")
