import streamlit as st
import io, wave, math, struct, time, html as html_lib
from datetime import datetime

st.set_page_config(page_title="Signup + Login + AI Voice Generator", layout="wide")

# ------------------------ SESSION STATE ------------------------
if "page" not in st.session_state:
    st.session_state.page = "signup"  # first page is signup
if "history" not in st.session_state:
    st.session_state.history = []
if "user" not in st.session_state:
    st.session_state.user = None
if "users" not in st.session_state:
    st.session_state.users = {}  # { email: {"username":..., "password":..., "phone":...} }

# ------------------------ MOCK AUDIO ------------------------
def generate_beep(duration_ms=900, freq=440):
    framerate = 44100
    amp = 16000
    n_samples = int(framerate * duration_ms / 1000)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        for i in range(n_samples):
            value = int(amp * math.sin(2.0 * math.pi * freq * (i / framerate)))
            wav_file.writeframes(struct.pack('<h', value))
    buffer.seek(0)
    return buffer

# ------------------------ HISTORY HTML ------------------------
def build_history_html():
    if not st.session_state.history:
        return '<div style="padding:10px 20px;color:#aaa;">No narrations yet.</div>'
    items = []
    for item in reversed(st.session_state.history):
        snip = html_lib.escape(item["text"][:60] + ("…" if len(item["text"]) > 60 else ""))
        when = item["time"]
        items.append(f'<div class="hist-item"><div class="hist-time">{when}</div><div class="hist-text">🗣️ {snip}</div></div>')
    return "\n".join(items)

# ------------------------ MAIN APP ------------------------
def main_app():
    st.markdown(f"""
    <style>
    header, footer {{display: none !important;}}
    .stApp {{
        background: linear-gradient(120deg,#1d2671,#c33764,#ff9a9e,#a1c4fd);
        background-size: 400% 400%;
        animation: gradientBG 18s ease infinite;
        font-family: 'Poppins', sans-serif;
        color: white !important;
    }}
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    *, p, label, h1, h2, h3, h4, h5, h6, span, div {{
        color: white !important;
    }}
    textarea, input, select {{
        background: rgba(0,0,0,0.35) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 10px !important;
    }}
    .stButton > button {{
        background: #2563eb !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
    }}
    .stButton > button:hover {{
        background: #1e4ed8 !important;
    }}
    #mySidebar {{
        height: 100%; width: 0;
        position: fixed; top: 0; left: 0;
        background: rgba(10,10,15,0.92);
        overflow-x: hidden;
        transition: width .35s ease;
        padding-top: 64px;
        z-index: 1001;
        backdrop-filter: blur(8px);
    }}
    #mySidebar .closebtn {{
        position: absolute; top: 16px; right: 18px; font-size: 32px; color: #fff;
    }}
    #mySidebar h3 {{
        margin: 6px 0 6px 22px;
    }}
    #mySidebar .hist-item {{
        padding: 10px 12px; margin: 8px 14px;
        border: 1px solid rgba(255,255,255,.18);
        border-radius: 12px;
        background: rgba(255,255,255,.05);
    }}
    </style>

    <div id="mySidebar">
      <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">×</a>
      <h3>📜 Past Narrations</h3>
      <div>{build_history_html()}</div>
    </div>

    <button class="openbtn" onclick="toggleNav()">☰</button>

    <script>
    let sidebarOpen = false;
    function toggleNav() {{
      if(sidebarOpen) {{
        document.getElementById("mySidebar").style.width = "0";
        sidebarOpen = false;
      }} else {{
        document.getElementById("mySidebar").style.width = "280px";
        sidebarOpen = true;
      }}
    }}
    function closeNav() {{
      document.getElementById("mySidebar").style.width = "0";
      sidebarOpen = false;
    }}
    </script>
    """, unsafe_allow_html=True)

    # Logout button in top-right
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state.page = "signup"
            st.rerun()

    st.title("🎤 AI Voice Generator")
    st.caption(f"Welcome {st.session_state.user} — Upload a file or paste text, choose a tone and voice, and generate speech.")

    uploaded_file = st.file_uploader("Drag and drop file here", type=["txt", "pdf", "docx"])
    text_default = ""
    if uploaded_file and uploaded_file.type.startswith("text/"):
        text_default = uploaded_file.read().decode("utf-8", errors="ignore")

    text = st.text_area("Enter your text here", value=text_default, height=140, placeholder="Type or paste text…")

    c1, c2 = st.columns(2)
    with c1:
        tone = st.selectbox("Tone", ["Neutral", "Friendly", "Formal", "Excited"], index=0)
    with c2:
        voice = st.selectbox("Voice", ["Allison", "Emma", "Brian", "David"], index=0)

    if st.button("Generate Audiobook"):
        if not text.strip():
            st.error("Please enter some text.")
        else:
            with st.spinner("Generating audio… 🎵"):
                time.sleep(0.7)
                audio_buffer = generate_beep()
            st.success("Done! Preview below.")
            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": text.strip()
            })
            st.audio(audio_buffer, format="audio/wav")
            st.download_button("⬇️ Download", data=audio_buffer, file_name="speech.wav", mime="audio/wav")

    st.markdown("### Original Text")
    st.text_area("Original", value=text, height=160, key="orig_box")

    st.markdown("### Rewritten Text")
    st.text_area("Rewritten", value="This is the rewritten version of your text.", height=160, key="rew_box")

# ------------------------ SIGNUP PAGE ------------------------
def signup_page():
    st.title("📝 Sign Up")
    st.write("Create your account to continue.")
    username = st.text_input("Username")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if not username or not email or not phone or not password:
            st.error("Please fill in all fields.")
        elif email in st.session_state.users:
            st.error("User already exists. Please login.")
            if st.button("Go to Login"):
                st.session_state.page = "login"
                st.rerun()
        else:
            st.session_state.users[email] = {
                "username": username,
                "password": password,
                "phone": phone
            }
            st.success("Account created! Please login.")
            time.sleep(1)
            st.session_state.page = "login"
            st.rerun()

# ------------------------ LOGIN PAGE ------------------------
def login_page():
    st.title("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in st.session_state.users and st.session_state.users[email]["password"] == password:
            st.session_state.user = st.session_state.users[email]["username"]
            st.session_state.page = "app"
            st.rerun()
        else:
            st.error("Invalid credentials.")

    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()

# ------------------------ PAGE ROUTING ------------------------
if st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "login":
    login_page()
else:
    main_app()
