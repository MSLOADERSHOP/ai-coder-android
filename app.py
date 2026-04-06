import streamlit as st
import openai
from PIL import Image
import base64
import io
import zipfile
import json
import hashlib

# ===== CONFIG =====
openai.api_key = st.secrets.get("OPENAI_API_KEY")
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
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == USER_EMAIL and hash_pass(password) == USER_PASSWORD_HASH:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong credentials")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login()
    st.stop()

# ===== STYLE =====
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
pre {
    background-color: #f0f0f0;
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
st.title("🤖 AI Dev Studio")

# Quick mode buttons
cols = st.columns(4)
if cols[0].button("📱 Android App"): st.session_state.chat_mode="android"
if cols[1].button("🌐 Website"): st.session_state.chat_mode="web"
if cols[2].button("🐍 Python Script"): st.session_state.chat_mode="python"
if cols[3].button("🛠 Fix Code"): st.session_state.chat_mode="fix"

mode_text = st.session_state.chat_mode

# Display chat
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input(f"Enter prompt ({mode_text})")

if prompt:
    full_prompt = f"[Mode: {mode_text}] {prompt}"
    st.session_state.messages.append({"role":"user","content":full_prompt})
    with st.chat_message("user"):
        st.markdown(full_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating code..."):
            content = [{"type":"text","text":full_prompt}]
            if uploaded_files:
                for file in uploaded_files:
                    if file.type.startswith("image/"):
                        encoded = base64.b64encode(file.read()).decode()
                        content.append({
                            "type":"image_url",
                            "image_url":{"url":f"data:image/png;base64,{encoded}"}
                        })
                    else:
                        text = file.read().decode(errors="ignore")
                        content.append({"type":"text","text":f"\nFILE:\n{text}"})

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":content}
                ],
                max_tokens=5000
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role":"assistant","content":reply})

            # Copy code button
            st.download_button(
                label="📥 Download Project ZIP",
                data=create_zip_from_code(reply),
                file_name="ai_project.zip",
                mime="application/zip"
)
