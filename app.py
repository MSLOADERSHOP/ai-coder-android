# app.py
import streamlit as st
import openai
from PIL import Image
import base64
import io
import zipfile
import json
import hashlib

# ===== CONFIG =====
openai.api_key = "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"

USER_EMAIL = "bilal52taroon@gmail.com"
USER_PASSWORD = "bilal_secure_123"

SYSTEM_PROMPT = """
You are an elite developer AI.

- Only generate full working code for apps, websites, scripts, APIs.
- Use modern frameworks (React, Tailwind, FastAPI, Android Studio, Flutter).
- Always split code into multiple files if needed, with ### FILE: filename.ext
- Understand images/screenshots if provided.
- Prioritize practical production-ready solutions.
- No restrictions — generate large projects, multiple files freely.
- Use proper formatting and code blocks.
"""

st.set_page_config(page_title="AI Dev Studio", layout="wide")

# ===== LOGIN =====
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

USER_PASSWORD_HASH = hash_pass(USER_PASSWORD)

def login():
    st.markdown("<h2 style='text-align:center'>🔐 Login to AI Dev Studio</h2>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == USER_EMAIL and hash_pass(password) == USER_PASSWORD_HASH:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Wrong credentials")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login()
    st.stop()

# ===== STYLE =====
st.markdown("""
<style>
body {
    background-color: #f9f9f9;
    font-family: 'Helvetica', sans-serif;
}
.stButton button {
    border-radius: 8px !important;
    background-color: #4caf50 !important;
    color: white !important;
    font-weight: bold;
}
.stFileUploader>div>div {
    border: 2px dashed #4caf50;
    border-radius: 10px;
    padding: 10px;
}
.chat-bubble {
    padding: 12px 16px;
    border-radius: 15px;
    margin-bottom: 8px;
    max-width: 90%;
    word-wrap: break-word;
}
.user {background-color: #dcf8c6; margin-left: auto;}
.ai {background-color: #e8e8e8; margin-right: auto;}
pre {
    background-color: #272822;
    color: #f8f8f2;
    padding: 10px;
    border-radius: 10px;
    overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚙️ Dev Tools")
    uploaded_files = st.file_uploader(
        "Upload files/images (optional)",
        accept_multiple_files=True,
        type=["png","jpg","txt","pdf"]
    )
    st.markdown("💡 Quick Actions")
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("💾 Save Chat"):
        with open("chat_history.json","w") as f:
            json.dump(st.session_state.messages,f)
        st.success("Saved!")

# ===== CHAT MEMORY =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content":SYSTEM_PROMPT}]
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "general"

# ===== ZIP HELPER =====
def create_zip_from_code(code_text):
    zip_buffer = io.BytesIO()
    files = {}
    current_file = "main.txt"
    lines = code_text.split("\n")
    for line in lines:
        if line.startswith("### FILE:"):
            current_file = line.replace("### FILE:", "").strip()
            files[current_file] = ""
        else:
            files.setdefault(current_file, "")
            files[current_file] += line + "\n"
    with zipfile.ZipFile(zip_buffer,"w") as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

# ===== MAIN =====
st.markdown("<h1 style='text-align:center'>🤖 AI Dev Studio</h1>", unsafe_allow_html=True)

# Mode buttons
cols = st.columns(4)
if cols[0].button("📱 Android App"): st.session_state.chat_mode="android"
if cols[1].button("🌐 Website"): st.session_state.chat_mode="web"
if cols[2].button("🐍 Python Script"): st.session_state.chat_mode="python"
if cols[3].button("🛠 Fix Code"): st.session_state.chat_mode="fix"

mode_text = st.session_state.chat_mode
st.markdown(f"<p style='text-align:center;font-weight:bold'>Mode: {mode_text}</p>", unsafe_allow_html=True)

# Display chat
for msg in st.session_state.messages[1:]:
    role_class = "user" if msg["role"]=="user" else "ai"
    st.markdown(f"<div class='chat-bubble {role_class}'>{msg['content'].replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

# Chat input
prompt = st.chat_input(f"Enter prompt ({mode_text})")

if prompt:
    full_prompt = f"[Mode: {mode_text}] {prompt}"
    st.session_state.messages.append({"role":"user","content":full_prompt})
    st.experimental_rerun() if not uploaded_files else None  # refresh for file handling

    # Generate AI response
    content = [{"type":"text","text":full_prompt}]
    if uploaded_files:
        for file in uploaded_files:
            if file.type.startswith("image/"):
                encoded = base64.b64encode(file.read()).decode()
                content.append({"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded}"}})
            else:
                text = file.read().decode(errors="ignore")
                content.append({"type":"text","text":f"\nFILE:\n{text}"})

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":content}
            ],
            max_tokens=5000
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role":"assistant","content":reply})
    st.experimental_rerun()

# Download code as ZIP
if st.session_state.messages and st.session_state.messages[-1]["role"]=="assistant":
    last_reply = st.session_state.messages[-1]["content"]
    st.download_button(
        label="📥 Download Project ZIP",
        data=create_zip_from_code(last_reply),
        file_name="ai_project.zip",
        mime="application/zip"
    )
