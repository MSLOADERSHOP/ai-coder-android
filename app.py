import streamlit as st
import openai
from PIL import Image
import io
import base64
from datetime import datetime

st.set_page_config(page_title="🤖 AI Coder Pro", layout="wide")
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

st.markdown("""
<style>
.pro-title {font-size:3rem;color:#ff6b6b;text-align:center;}
.code-box {background:#1e1e1e;color:#f8f8f2;padding:1.5rem;border-radius:10px;font-family:monospace;height:500px;overflow:auto;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="pro-title">🤖 AI Code Generator PRO</h1>', unsafe_allow_html=True)
st.info("📱 Upload **screenshot/photo/file** → Get **complete code instantly**!")

col1, col2 = st.columns([3,1])

with col1:
    uploaded = st.file_uploader("📁 Upload Image/File", type=['png','jpg','jpeg','txt','pdf','py','js'])
    idea = st.text_area("💡 Your idea:", height=120, 
        placeholder="React app from screenshot, Discord bot, FastAPI from PDF spec...")

with col2:
    st.markdown("### 🚀 Examples")
    st.markdown("""
    - 📱 **App screenshot** → React Native
    - 🎨 **Figma** → HTML/Tailwind
    - 📄 **API spec** → Backend
    - 💡 **"ecommerce site"** → Fullstack
    """)

if st.button("🎯 GENERATE FULL CODE", use_container_width=True) and idea:
    with st.spinner("🤖 AI building your app..."):
        messages = [{"role": "user", "content": f"Create COMPLETE production code for: {idea}"}]
        
        if uploaded:
            if 'image' in uploaded.type:
                img = Image.open(uploaded)
                st.image(img, caption="🎨 Vision Analysis", width=300)
                b64 = base64.b64encode(uploaded.read()).decode()
                messages[0]["content"] = [{"type": "text", "text": f"Exact code for this design: {idea}"},
                                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
            else:
                content = uploaded.read().decode('utf-8', errors='ignore')
                messages[0]["content"] += f"\n\nFile {uploaded.name}:\n{content}"
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=6000
        )
        
        code = response.choices[0].message.content
        st.markdown('<div class="code-box">' + code.replace('```', '') + '</div>', unsafe_allow_html=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.download_button(f"💾 Download Project {timestamp}", 
                          code, 
                          f"ai-project-{timestamp.replace(':','-')}.md")
        
        st.success(f"✅ Project saved! {timestamp}")

st.markdown("---")
st.caption("🚀 MSLOADERSHOP AI Coder Pro | Made for Android")
