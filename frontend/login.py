import streamlit as st
import io, wave, math, struct, time, html as html_lib
from datetime import datetime

# ------------------------ CONFIG ------------------------
st.set_page_config(page_title="AI Voice Generator", layout="wide")

# ------------------------ FUNCTIONS ------------------------
def generate_beep(duration_ms=900, freq=440):
    """Generate a placeholder beep sound."""
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

# ------------------------ STATE ------------------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "page" not in st.session_state:
    st.session_state.page = "signup"
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------ GLOBAL CSS ------------------------
st.markdown("""
<style>
header[data-testid="stHeader"], footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp {
    background: linear-gradient(120deg,#1d2671,#c33764,#ff9a9e,#a1c4fd);
    background-size: 400% 400%;
    animation: gradientBG 18s ease infinite;
    font-family: 'Poppins', sans-serif;
    color: white !important;
}
*, p, label, h1, h2, h3, h4, h5, h6, span, div {
    color: white !important;
}
textarea, input, select {
    background: rgba(0,0,0,0.35) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
}
.stButton > button {
    background: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
}
.stButton > button:hover {
    background: #1e4ed8 !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------ SIGN UP PAGE ------------------------
def signup_page():
    st.title("📝 Create an Account")
    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not new_user or not new_pass:
            st.error("Username and password cannot be empty.")
        elif new_user in st.session_state.users:
            st.error("Username already exists.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("✅ Account created! Redirecting to login...")
            time.sleep(1)
            st.session_state.page = "login"
            st.rerun()  # <-- FIXED HERE

# ------------------------ LOGIN PAGE ------------------------
def login_page():
    st.title("🔐 Login to AI Voice Generator")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.page = "home"
            st.session_state.current_user = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ------------------------ HOME PAGE ------------------------
def home_page():
    st.title(f"🎤 AI Voice Generator - Welcome {st.session_state.current_user}")
    st.caption("Upload a file or paste text, choose a tone and voice, and generate speech. (This demo produces a simple beep as a placeholder.)")
    
    if st.button("🚪 Logout"):
        st.session_state.page = "login"
        st.rerun()

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

    st.markdown("### Past Narrations")
    if not st.session_state.history:
        st.write("No past narrations yet.")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(
                f"<div><b>{item['time']}</b><br>{html_lib.escape(item['text'][:180])}{'…' if len(item['text'])>180 else ''}</div>",
                unsafe_allow_html=True
            )

# ------------------------ PAGE ROUTING ------------------------
if st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "home":
    home_page()