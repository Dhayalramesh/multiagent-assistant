import streamlit as st
import requests
from urllib.parse import quote

st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")
st.title("🔍 Multi‑Agent Research Assistant")
st.markdown("Ask a question, and the agent will **search Wikipedia** and show the summary.")

# Wikipedia requires a User-Agent
HEADERS = {
    "User-Agent": "MultiAgentResearchAssistant/1.0 (https://streamlit.io; your-email@example.com)"
}

def clean_query(query):
    """Extract the main topic from a natural language question."""
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
    return cleaned.capitalize()

def search_wikipedia(query):
    """
    Try to find a Wikipedia page for the query.
    First try direct page summary; if that fails, use the search API.
    """
    search_term = clean_query(query)

    # 1) Direct page summary
    direct_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(search_term)}"
    try:
        resp = requests.get(direct_url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "extract" in data:
                return data["extract"], search_term
    except:
        pass

    # 2) Fallback: use the search API
    search_url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={quote(query)}&format=json"
    )
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("query", {}).get("search", [])
            if results:
                # Take the first result's title
                title = results[0]["title"]
                # Fetch its summary
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
                summary_resp = requests.get(summary_url, headers=HEADERS, timeout=5)
                if summary_resp.status_code == 200:
                    summary_data = summary_resp.json()
                    if "extract" in summary_data:
                        return summary_data["extract"], title
    except:
        pass

    return None, None

def get_wikipedia_summary(query):
    summary, title = search_wikipedia(query)
    if summary:
        return f"**{title}**: {summary}"
    else:
        return f"Could not find a Wikipedia page for '{query}'. Please try a different question."

# Streamlit UI
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
