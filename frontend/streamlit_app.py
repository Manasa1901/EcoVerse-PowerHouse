import streamlit as st
import io, wave, math, struct, time, html as html_lib
from datetime import datetime

# ------------------------ PAGE CONFIG ------------------------
st.set_page_config(page_title="AI Voice Generator", layout="wide")

# ------------------------ STATE ------------------------
if "history" not in st.session_state:
    # A list of dicts: {"time": str, "text": str}
    st.session_state.history = []

# ------------------------ MOCK AUDIO ------------------------
def generate_beep(duration_ms=900, freq=440):
    """Simple placeholder audio so the page is fully functional offline."""
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

# ------------------------ DYNAMIC SIDEBAR CONTENT ------------------------
def build_history_html():
    if not st.session_state.history:
        return '<div style="padding:10px 20px;color:#aaa;">No narrations yet.</div>'
    items = []
    for idx, item in enumerate(reversed(st.session_state.history), 1):
        snip = html_lib.escape(item["text"][:60] + ("…" if len(item["text"]) > 60 else ""))
        when = item["time"]
        items.append(f'<div class="hist-item"><div class="hist-time">{when}</div><div class="hist-text">🗣️ {snip}</div></div>')
    return "\n".join(items)

history_html = build_history_html()

# ------------------------ GLOBAL CSS + JS ------------------------
st.markdown("""
<style>
/* Remove Streamlit default header/footer */
header[data-testid="stHeader"], footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

/* Background animation */
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

/* Text color fix */
*, p, label, h1, h2, h3, h4, h5, h6, span, div {
    color: white !important;
}

/* Inputs */
textarea, input, select {
    background: rgba(0,0,0,0.35) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
}

/* Buttons */
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

/* Sidebar toggle button */
.openbtn {
    position: fixed; top: 16px; left: 20px; z-index: 1002;
    background: rgba(255,255,255,0.92); color:#111 !important;
    border: none; border-radius: 50px; padding: 10px 14px;
    font-weight: 800;
    box-shadow: 0 6px 20px rgba(0,0,0,.2);
}

/* Login button */
.login-btn {
    position: fixed; top: 16px; right: 20px; z-index: 1002;
    background: rgba(255,255,255,0.9);
    color: #111 !important;
    padding: 8px 14px; border-radius: 10px;
    font-weight: 700;
    text-decoration: none;
}

/* Custom sidebar */
#mySidebar {
    height: 100%; width: 0;
    position: fixed; top: 0; left: 0;
    background: rgba(10,10,15,0.92);
    overflow-x: hidden;
    transition: width .35s ease;
    padding-top: 64px;
    z-index: 1001;
    backdrop-filter: blur(8px);
}
#mySidebar .closebtn {
    position: absolute; top: 16px; right: 18px; font-size: 32px; color: #fff;
}
#mySidebar h3 {
    margin: 6px 0 6px 22px;
}
#mySidebar .section {
    padding: 6px 20px 10px 20px;
}
#mySidebar .hist-item {
    padding: 10px 12px; margin: 8px 14px;
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 12px;
    background: rgba(255,255,255,.05);
}
#mySidebar a.link {
    display: inline-block; margin: 6px 8px 0 0; padding: 6px 10px;
    color: #fff !important; text-decoration: none;
    border: 1px solid rgba(255,255,255,.22); border-radius: 10px;
}
</style>

<!-- Sidebar HTML -->
<div id="mySidebar">
  <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">×</a>

  <h3>📜 Previous Narrations</h3>
  <div class="section">
    <div class="hist-item"><strong>Story 1</strong><br><small>Yesterday</small></div>
    <div class="hist-item"><strong>Story 2</strong><br><small>2 days ago</small></div>
  </div>

  <h3>❓ Help</h3>
  <div class="section">
    <a class="link" href="#">How to use</a>
    <a class="link" href="#">FAQ</a>
  </div>

  <h3>🌐 Connect</h3>
  <div class="section">
    <a class="link" href="https://twitter.com" target="_blank">🐦 Twitter</a>
    <a class="link" href="https://facebook.com" target="_blank">📘 Facebook</a>
    <a class="link" href="mailto:support@example.com">📧 Email</a>
  </div>
</div>

<!-- Toggle + Login buttons -->
<button class="openbtn" onclick="openNav()">☰</button>
<a class="login-btn" href="#">Login / Sign up</a>

<script>
function openNav() {
  document.getElementById("mySidebar").style.width = "280px";
}
function closeNav() {
  document.getElementById("mySidebar").style.width = "0";
}
</script>
""", unsafe_allow_html=True)


# ------------------------ MAIN UI ------------------------
st.title("🎤 AI Voice Generator")
st.caption("Upload a file or paste text, choose a tone and voice, and generate speech. (This demo produces a simple beep as a placeholder.)")

# Upload + text
uploaded_file = st.file_uploader("Drag and drop file here", type=["txt", "pdf", "docx"])
text_default = ""
if uploaded_file and uploaded_file.type.startswith("text/"):
    text_default = uploaded_file.read().decode("utf-8", errors="ignore")

text = st.text_area("Enter your text here", value=text_default, height=140, placeholder="Type or paste text…")

# Tone & Voice
c1, c2 = st.columns(2)
with c1:
    tone = st.selectbox("Tone", ["Neutral", "Friendly", "Formal", "Excited"], index=0)
with c2:
    voice = st.selectbox("Voice", ["Allison", "Emma", "Brian", "David"], index=0)

# Generate
if st.button("Generate Audiobook"):
    if not text.strip():
        st.error("Please enter some text.")
    else:
        with st.spinner("Generating audio… 🎵"):
            time.sleep(0.7)  # simulate
            audio_buffer = generate_beep()
        st.success("Done! Preview below.")
        # Save to history
        st.session_state.history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "text": text.strip()
        })
        # Show audio + download
        st.markdown('<div class="audio-wrap">', unsafe_allow_html=True)
        st.audio(audio_buffer, format="audio/wav")
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download", data=audio_buffer, file_name="speech.wav", mime="audio/wav")

st.markdown("### Original Text")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.text_area("Original", value=text, height=160, key="orig_box")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### Rewritten Text")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.text_area("Rewritten", value="This is the rewritten version of your text.", height=160, key="rew_box")
st.markdown('</div>', unsafe_allow_html=True)

# Past narrations (from session)
st.markdown("### Past Narrations")
if not st.session_state.history:
    st.write("No past narrations yet.")
else:
    for item in reversed(st.session_state.history):
        st.markdown(
            f"<div class='card'><b>{item['time']}</b><br>{html_lib.escape(item['text'][:180])}{'…' if len(item['text'])>180 else ''}</div>",
            unsafe_allow_html=True
        )
