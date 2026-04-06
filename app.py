import streamlit as st
import openai
import base64
import json

# ========= CONFIG =========
openai.api_key = st.secrets.get("OPENAI_API_KEY")

USER_EMAIL = "bilal52taroon@gmail.com"
USER_PASSWORD = "bilal_secure_123"

SYSTEM_PROMPT = """
You are an elite senior developer.

- Always generate FULL working code
- Focus on Android, web apps, APIs
- Use modern UI (React, Tailwind, Material UI)
- Understand images deeply if provided
- Output production-ready code
- Include file structure when needed
- Be direct, smart, and developer-focused
"""

st.set_page_config(page_title="AI Dev Pro", layout="wide")

# ========= LOGIN =========
def login():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == USER_EMAIL and password == USER_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong credentials")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login()
    st.stop()

# ========= UI STYLE =========
st.markdown("""
<style>
.stChatMessage {
    border-radius: 15px;
    padding: 10px;
}
.stButton button {
    border-radius: 10px;
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ========= SIDEBAR =========
with st.sidebar:
    st.title("⚙️ Dev Tools")

    uploaded_files = st.file_uploader(
        "Upload files/images",
        accept_multiple_files=True,
        type=["png", "jpg", "txt", "pdf"]
    )

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Save Chat"):
        with open("chat_history.json", "w") as f:
            json.dump(st.session_state.messages, f)
        st.success("Saved!")

# ========= CHAT MEMORY =========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ========= MAIN =========
st.title("🤖 AI Developer Pro")

# Show messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
prompt = st.chat_input("Build apps, fix code, generate anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Building..."):

            content = [{"type": "text", "text": prompt}]

            # Handle uploads
            if uploaded_files:
                for file in uploaded_files:
                    if file.type.startswith("image/"):
                        encoded = base64.b64encode(file.read()).decode()
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded}"
                            }
                        })
                    else:
                        text = file.read().decode(errors="ignore")
                        content.append({
                            "type": "text",
                            "text": f"\nFILE:\n{text}"
                        })

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ],
                max_tokens=4000
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
