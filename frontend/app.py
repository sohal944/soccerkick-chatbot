import streamlit as st
import requests
from scraper_for_ui import scrape_from_livescore  # Assuming you imported the scraper here

# ---------- Config ----------
st.set_page_config(page_title="Sports Chatbot", layout="wide")

# Set background color, text styles, and fonts
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff;
        font-family: 'Poppins', sans-serif;
    }
    .main {
        padding: 20px;
    }
    h1 {
        font-size: 48px;
        color: #1E90FF;
        text-align: center;
        font-weight: bold;
    }
    h2 {
        font-size: 32px;
        color: #FF4500;
        text-align: center;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Flex container for aligning elements to the right */
    .live-score-container {
        display: flex;
        flex-direction: column;  /* Stack elements vertically */
        justify-content: flex-start;  /* Align at the top */
        align-items: flex-end;     /* Align items to the right */
        margin-top: 20px;
        font-size: 24px;
    }

    .live-score-title {
        color: #1E90FF;
        margin-bottom: 10px;  /* Space between title and score */
        font-size: 30px;
        font-weight: bold;
    }

    .current-score {
        color: #ffc500;
        font-size: 32px;
        margin-bottom: 20px;  /* Space between score and football animation */
    }

    .stSidebar {
        background-color: #9fc5e8;
    }
    .stSelectbox {
        background-color: transparent;  /* Remove the white box behind the dropdown */
        border: none;  /* Remove the border of the dropdown */
    }
    .stMarkdown {
        font-size: 18px;
        line-height: 1.6;
    }
    .stChatMessage {
        font-family: 'Courier New', Courier, monospace;
    }
    .stInput {
        font-size: 18px;
    }

    /* Animation styles */
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    .live-dot {
        background-color: red;
        border-radius: 50%;
        width: 10px;
        height: 10px;
        display: inline-block;
        animation: blink 1s infinite;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("SoccerKicks ⚽")

# ---------- Fetch Live Matches from Scraper ----------
live_matches = scrape_from_livescore()  # Get live matches from the scraper function

# ---------- Handle Empty Live Matches ----------
if not live_matches:
    st.warning("No live matches available at the moment.")
    live_matches = {
        "Real Madrid vs Barcelona": "2 - 1",  # Mock data in case the scraper fails or returns empty
        "Manchester City vs Liverpool": "1 - 1",
        "PSG vs Bayern Munich": "0 - 2"
    }

# ---------- Sidebar with Blinking Dot for Live Matches ----------
st.sidebar.markdown("""
    <h2 style="display: inline; color: black;">
         Live Matches
    </h2>           
    <span class="live-dot"></span>
""", unsafe_allow_html=True)

# ---------- Sidebar Match Dropdown ----------
selected_match = st.sidebar.selectbox(
    "Select a live match to view stats",
    options=list(live_matches.keys())  # Only show match names
)

# ---------- Live Match Info Display ----------
# Create a container for both title, score, and football animation using flexbox
st.markdown(f"""
    <div class="live-score-container">
        <span class="live-score-title"> {selected_match}</span>
        <span class="current-score"> Score: {live_matches[selected_match]}</span>
    </div>
""", unsafe_allow_html=True)

st.info("Live commentary and stats coming soon...")

st.markdown("---")

# ---------- Chat Section ----------
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------- User Input & Query Forwarding ----------
user_input = st.chat_input("Ask something about the match...")

if user_input:
    # Save user's message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Forward query to backend API (replace this with your actual backend URL)
    
    backend_url = "http://localhost:8000/query"

    payload = {"query": user_input, "match": selected_match}  # Include match info in payload

    # Send request to backend
    response = requests.post(backend_url, json=payload)

    # Check if response is valid
    if response.status_code == 200:
        bot_response = response.json().get("response", "Sorry, something went wrong.")
    else:
        bot_response = "Sorry, I couldn't get a response from the backend."

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Rerun to show updated messages
    st.rerun()