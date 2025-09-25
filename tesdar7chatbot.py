import streamlit as st
import time
import re

# --------------------------
# URL auto-linking helper
# --------------------------
URL_RE = re.compile(r'(?P<url>((https?://)?(?:www\.)?[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s<>\)]*)?))', re.IGNORECASE)

def linkify(text: str) -> str:
    text = text or ""
    def _repl(m):
        url = m.group('url')
        href = url if url.startswith(('http://', 'https://')) else f'https://{url}'
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{url}</a>'
    return URL_RE.sub(_repl, text)

# --------------------------
# Substring matching helpers
# --------------------------
def contains_any(message: str, patterns) -> bool:
    m = (message or "").lower()
    return any(p.lower() in m for p in patterns)

def contains_number(message: str, num: str) -> bool:
    return re.search(rf"{re.escape(num)}", message or "") is not None

# --------------------------
# Simple rule-based chatbot function
# --------------------------
def chatbot_response(user_message: str) -> str:
    user_message = (user_message or "").lower().strip()

    # greetings
    if contains_any(user_message, ["hi", "hello", "hey", "start"]):
        return "👋 Hello! How can I help you today?"

    # 1) Create account (BSRS - scholarship)
    elif contains_any(user_message, [
        "create account bsrs", "bsrs", "scholar", "scholarship", "bsrs.tesda.gov.ph"
    ]) or contains_number(user_message, "1"):
        return "📝 You can create an account for scholarship here: https://bsrs.tesda.gov.ph/"

    # 2) Create account (TOP - online programs)
    elif contains_any(user_message, [
        "create account top", "top", "e-tesda", "etesda", "online program", "online course", "e learning", "e-learning"
    ]) or contains_number(user_message, "2"):
        return "📝 You can create an account for online programs here: https://e-tesda.gov.ph/"

    # 3) TESDA Programs / Courses
    elif contains_any(user_message, [
        "courses", "course", "programs", "program", "training regulations", "training_regulations", "tr"
    ]) or contains_number(user_message, "3"):
        return "📦 Sure! Explore the available TESDA Programs here: https://tesda.gov.ph/Download/Training_Regulations"

    # 4) Verification
    elif contains_any(user_message, [
        "verify", "verification", "rwac", "nc verification", "certificate check", "check nc", "validate nc"
    ]) or contains_number(user_message, "4"):
        return "✅ You can verify your National Certificates (NCs) here: https://tesda.gov.ph/Rwac/"

    # 5) Talk to agent / human
    elif contains_any(user_message, [
        "talk to agent", "agent", "human", "support", "helpdesk", "call", "speak to person", "connect me"
    ]) or contains_number(user_message, "5"):
        return "📞 Okay, I’m connecting you to our human support staff."

    # 6) Help / menu
    elif contains_any(user_message, [
        "help", "menu", "options", "what can you do", "assist"
    ]) or contains_number(user_message, "6"):
        return "🙋 For more assistance, you may contact the TESDA Regional Office through its Social Media account: https://facebook.com/tesdasietecentralvisayas"

    else:
        return "❓ Sorry, I didn’t understand that. Please choose an option below or type 'help'."

# --------------------------
# Page config and session
# --------------------------
st.set_page_config(page_title="Simple Chatbot", page_icon="🤖", layout="wide")

if "messages" not in st.session_state:
    # messages is a list of tuples: (role, text)
    st.session_state.messages = [("Bot", "👋 Hi! Welcome to TESDA Chatbot. Type 'help' to see options.")]

# last_action will hold a quick-action command when a button is clicked
if "last_action" not in st.session_state:
    st.session_state.last_action = None

# --------------------------
# Sidebar info + reset
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This is a simple **rule-based chatbot** built with Streamlit. You can:")
    st.markdown("""
    - 👋 Greet the bot  
    - 📝 Create an account (TOP/ BSRS)  
    - 📦 View TESDA Programs  
    - 📞 Talk to a human agent  
    """)
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = [("Bot", "👋 Hi! Welcome to TESDA Bot. Type 'help' to see options.")]
        st.session_state.last_action = None
        st.experimental_rerun()

# --------------------------
# Top title
# --------------------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>😾 Rule-Based Chatbot</h1>", unsafe_allow_html=True)
st.write("Interact with the chatbot by typing or using quick action buttons below.")

# --------------------------
# Quick action buttons (safe pattern)
# --------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)
if col1.button("📝 Create Account (Scholarship)"):
    st.session_state.last_action = "create account bsrs"
if col2.button("📝 Create Account (Online Courses)"):
    st.session_state.last_action = "create account top"
if col3.button("📋TESDA Programs"):
    st.session_state.last_action = "courses"
if col4.button("📞 Talk to Agent"):
    st.session_state.last_action = "talk to agent"
if col5.button("✅ Verification"):
    st.session_state.last_action = "verify"
if col6.button("🙋 Help"):
    st.session_state.last_action = "help"

# --------------------------
# Determine user_input:
# - priority: last_action (button) -> chat_input (if available) -> text_input fallback
# --------------------------
user_input = None

# If a button was clicked (last_action set), consume it exactly once
if st.session_state.last_action:
    user_input = st.session_state.last_action
    # clear it immediately so it won't repeat on next run
    st.session_state.last_action = None

# Try to use chat_input (Streamlit >= 1.25). If not available, fall back to text_input.
try:
    # chat_input returns a value only when user submits
    if user_input is None:
        chat_in = st.chat_input("Type your message here...")
        if chat_in:
            user_input = chat_in
except Exception:
    # fallback to text_input with a session_state key so we can clear it after processing
    if user_input is None:
        # use a session key so we can reset it safely
        if "typed_value" not in st.session_state:
            st.session_state.typed_value = ""
        typed = st.text_input("Type your message here:", value=st.session_state.typed_value, key="typed_value")
        # Only process if not empty and not same as last processed (to avoid reprocessing)
        if typed and (len(st.session_state.messages) == 0 or st.session_state.messages[-1] != ("You", typed)):
            user_input = typed

# --------------------------
# Process a single user_input (if any)
# --------------------------
if user_input:
    # Append user message
    st.session_state.messages.append(("You", user_input))

    # Simulate typing effect (non-blocking visual)
    with st.spinner("Bot is typing..."):
        time.sleep(0.9)

    # Get bot reply
    try:
        bot_reply = chatbot_response(user_input)
    except Exception as e:
        bot_reply = f"⚠️ An internal error occurred while generating a reply: {e}"

    st.session_state.messages.append(("Bot", bot_reply))

    # If using the text_input fallback, clear stored value after processing
    if "typed_value" in st.session_state:
        st.session_state.typed_value = ""

# --------------------------
# Display conversation safely (with linkify)
# --------------------------
for entry in st.session_state.messages:
    # defensive check to avoid unpacking errors
    if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
        # skip malformed entries
        continue
    role, msg = entry
    if role == "You":
        safe_msg = linkify(msg)
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; margin:5px; text-align:right;'>"
            f"🧑 <b>{role}:</b> {safe_msg}</div>",
            unsafe_allow_html=True,
        )
    else:
        safe_msg = linkify(msg)
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; margin:5px; text-align:left;'>"
            f"😾 <b>{role}:</b> {safe_msg}</div>",
            unsafe_allow_html=True,
        )
