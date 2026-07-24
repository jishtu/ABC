import base64
import io
import os
import qrcode
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from streamlit_mic_recorder import speech_to_text

# Safe import for gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ------------------------
# LOAD API
# ------------------------
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# Session State Initializations
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------
# PAGE SETTINGS
# ------------------------
st.set_page_config(
    page_title="GoCode AI",
    page_icon="⚡",
    layout="wide"
)

# ------------------------
# HELPER: LOAD IMAGES AS BASE64
# ------------------------
def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

logo_b64 = get_image_base64("logo.png")
dev1_b64 = get_image_base64("dev1.jpg")

# ------------------------
# GITHUB-STYLE COSMIC DARK CSS WITH ENHANCED ANIMATIONS
# ------------------------
st.markdown("""
<style>
/* GitHub Hero Ambient Background */
.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, rgba(90, 40, 160, 0.28) 0%, rgba(13, 17, 23, 0) 70%),
        radial-gradient(circle at 50% 100%, rgba(0, 242, 254, 0.15) 0%, rgba(13, 17, 23, 0) 60%),
        #0d1117;
    color: #f0f6fc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Glassmorphism Sidebar */
[data-testid="stSidebar"] {
    background: rgba(13, 17, 23, 0.88) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(48, 54, 61, 0.6) !important;
}

/* Advanced Keyframe Animations */
@keyframes fadeInSlide {
    0% { opacity: 0; transform: translateY(20px) scale(0.98); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 12px rgba(0, 242, 254, 0.25); border-color: rgba(56, 139, 253, 0.4); }
    50% { box-shadow: 0 0 28px rgba(168, 85, 247, 0.55); border-color: rgba(188, 140, 255, 0.8); }
    100% { box-shadow: 0 0 12px rgba(0, 242, 254, 0.25); border-color: rgba(56, 139, 253, 0.4); }
}

@keyframes logoFloat {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(1deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}

@keyframes logoGlow {
    0% { filter: drop-shadow(0 0 12px rgba(0, 242, 254, 0.5)); }
    50% { filter: drop-shadow(0 0 32px rgba(168, 85, 247, 0.85)); }
    100% { filter: drop-shadow(0 0 12px rgba(0, 242, 254, 0.5)); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes waveBar {
    0%, 100% { height: 8px; }
    50% { height: 32px; }
}

@keyframes borderGlowPulse {
    0% { border-color: rgba(56, 139, 253, 0.3); }
    50% { border-color: rgba(188, 140, 255, 0.6); }
    100% { border-color: rgba(56, 139, 253, 0.3); }
}

/* Transparent Logo Container */
.animated-logo-container {
    text-align: center;
    padding: 10px 0;
    animation: logoFloat 4s ease-in-out infinite;
}

.animated-logo {
    max-width: 170px;
    height: auto;
    background: transparent !important;
    animation: logoGlow 3.5s infinite ease-in-out;
}

/* Custom Components & Iframes Clean Styling */
[data-testid="stCustomComponentV1"],
div[data-testid="stCustomComponentV1"] iframe {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stCustomComponentV1"] {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}

/* Sidebar Radio Options */
div[data-testid="stRadio"] > div {
    gap: 8px;
}

div[data-testid="stRadio"] label {
    background: rgba(22, 27, 34, 0.7) !important;
    border: 1px solid rgba(48, 54, 61, 0.6) !important;
    border-radius: 12px !important;
    padding: 12px 18px !important;
    color: #c9d1d9 !important;
    font-weight: 500 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    cursor: pointer !important;
}

div[data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

div[data-testid="stRadio"] label:hover {
    background: rgba(33, 38, 45, 0.95) !important;
    border-color: #58a6ff !important;
    transform: translateX(6px) scale(1.01);
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(88, 166, 255, 0.25);
}

div[data-testid="stRadio"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.3), rgba(168, 85, 247, 0.3)) !important;
    border: 1.5px solid #58a6ff !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 0 22px rgba(56, 139, 253, 0.4) !important;
}

/* Hero Title Styling */
.big-title {
    font-size: 64px;
    font-weight: 800;
    text-align: center;
    letter-spacing: -1.5px;
    background: linear-gradient(90deg, #ffffff, #a5d6ff, #d2a8ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 5s linear infinite, fadeInSlide 0.8s ease-out;
}

.subtitle {
    font-size: 22px;
    text-align: center;
    color: #8b949e;
    margin-bottom: 8px;
    font-weight: 400;
    letter-spacing: -0.3px;
    animation: fadeInSlide 1s ease-out;
}

.developer-subheading {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 25px;
    animation: fadeInSlide 1.1s ease-out;
}

.developer-badge-head {
    background: rgba(56, 139, 253, 0.1);
    border: 1px solid rgba(56, 139, 253, 0.4);
    color: #58a6ff;
    padding: 6px 22px;
    border-radius: 20px;
    display: inline-block;
    box-shadow: 0 0 16px rgba(56, 139, 253, 0.2);
    animation: pulseGlow 3s infinite ease-in-out;
}

/* Glassmorphism Info Cards */
.info-card {
    background: rgba(22, 27, 34, 0.85);
    border: 1.5px solid rgba(56, 139, 253, 0.35);
    border-radius: 20px;
    padding: 30px;
    margin: 20px auto;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(16px);
    animation: fadeInSlide 0.7s ease-out, borderGlowPulse 4s infinite ease-in-out;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(56, 139, 253, 0.22);
}

/* Compact Profile Photo Frame */
.dev-photo-small {
    width: 210px;
    height: 210px;
    object-fit: cover;
    border-radius: 50%;
    border: 3px solid rgba(56, 139, 253, 0.6);
    box-shadow: 0 0 25px rgba(56, 139, 253, 0.3);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    animation: logoFloat 5s ease-in-out infinite;
}

.dev-photo-small:hover {
    transform: scale(1.08) rotate(2deg);
    box-shadow: 0 0 40px rgba(188, 140, 255, 0.6);
}

.dev-logo-card {
    max-width: 190px;
    height: auto;
    animation: logoGlow 3s infinite ease-in-out, logoFloat 4s ease-in-out infinite;
}

.live-speech-card {
    background: rgba(22, 27, 34, 0.85);
    border: 1px solid rgba(56, 139, 253, 0.4);
    border-radius: 18px;
    padding: 22px 28px;
    text-align: center;
    margin: 15px auto 25px auto;
    max-width: 740px;
    box-shadow: 0 0 35px rgba(56, 139, 253, 0.2);
    backdrop-filter: blur(14px);
    animation: fadeInSlide 0.5s ease-out;
}

/* Sound Wave Equalizer */
.equalizer-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    height: 35px;
    margin-top: 12px;
}

.equalizer-bar {
    width: 5px;
    background: linear-gradient(180deg, #58a6ff, #bc8cff);
    border-radius: 4px;
    animation: waveBar 1.2s infinite ease-in-out;
}

/* Chat Bubbles */
.chat-box-user {
    background: rgba(22, 27, 34, 0.8);
    border-left: 4px solid #58a6ff;
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 14px;
    animation: fadeInSlide 0.4s ease-out;
}

.chat-box-ai {
    background: rgba(13, 17, 23, 0.9);
    border-left: 4px solid #bc8cff;
    padding: 18px 22px;
    border-radius: 12px;
    margin-bottom: 22px;
    box-shadow: 0 4px 22px rgba(188, 140, 255, 0.15);
    animation: fadeInSlide 0.4s ease-out;
}

.developer-footer {
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    color: #8b949e;
    padding: 12px;
}

.developer-badge {
    background: rgba(56, 139, 253, 0.15);
    border: 1px solid rgba(56, 139, 253, 0.4);
    color: #58a6ff;
    padding: 6px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 6px;
    animation: pulseGlow 3s infinite ease-in-out;
}

.tech-tag {
    background: rgba(56, 139, 253, 0.15);
    border: 1px solid #58a6ff;
    color: #58a6ff;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    display: inline-block;
    transition: all 0.3s ease;
}

.tech-tag:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px rgba(88, 166, 255, 0.5);
}

.tech-tag-purple {
    background: rgba(188, 140, 255, 0.15);
    border: 1px solid #bc8cff;
    color: #bc8cff;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    display: inline-block;
    transition: all 0.3s ease;
}

.tech-tag-purple:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 15px rgba(188, 140, 255, 0.5);
}

.qr-container {
    background: rgba(22, 27, 34, 0.7);
    border: 1px solid rgba(48, 54, 61, 0.6);
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# GLOBAL BRANDING SUBHEADING HELPER
# ------------------------
def render_developer_badge():
    st.markdown("""<div class='developer-subheading'><div class='developer-badge-head'>⚡ Developed by Yeshus Verma</div></div>""", unsafe_allow_html=True)

# ------------------------
# GROQ AI HELPER FUNCTION
# ------------------------
def ask_ai(prompt: str) -> str:
    if not client:
        return "❌ Error: GROQ_API_KEY environment variable is not set."
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# ------------------------
# SAFE REAL HUMAN VOICE GENERATOR
# ------------------------
def speak_text_neural(text_to_speak: str, accent_code: str = "en"):
    short_text = text_to_speak[:280].replace("\n", " ").replace('"', "'")

    if GTTS_AVAILABLE:
        try:
            tts = gTTS(text=short_text, lang=accent_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            b64_audio = base64.b64encode(fp.read()).decode()
            md_audio = f"""<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>"""
            st.markdown(md_audio, unsafe_allow_html=True)
            return
        except Exception:
            pass

    # Browser Speech Synthesis Fallback
    tts_fallback_html = f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{short_text}");
        msg.rate = 1.0;
        msg.pitch = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(tts_fallback_html, height=0)

# ------------------------
# DYNAMIC FLUID 3D SPHERE GLOBE COMPONENT
# ------------------------
def render_3d_sphere():
    sphere_html = """
    <div style="text-align: center; background: transparent; padding: 5px 0;">
        <canvas id="sphereCanvas" width="340" height="340"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('sphereCanvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const numPoints = 380;
        const baseRadius = 95;
        let time = 0;

        const points = [];
        for (let i = 0; i < numPoints; i++) {
            const theta = Math.acos(-1 + (2 * i) / numPoints);
            const phi = Math.sqrt(numPoints * Math.PI) * theta;
            points.push({
                baseX: baseRadius * Math.cos(phi) * Math.sin(theta),
                baseY: baseRadius * Math.sin(phi) * Math.sin(theta),
                baseZ: baseRadius * Math.cos(theta),
                theta: theta,
                phi: phi
            });
        }

        function draw() {
            ctx.clearRect(0, 0, width, height);
            time += 0.03;

            let angleX = 0.005;
            let angleY = 0.008;

            for (let i = 0; i < points.length; i++) {
                let p = points[i];

                let waveDeform = Math.sin(p.theta * 4 + time) * Math.cos(p.phi * 3 + time) * 14;
                let currentRadius = baseRadius + waveDeform;

                let x = currentRadius * Math.cos(p.phi) * Math.sin(p.theta);
                let y = currentRadius * Math.sin(p.phi) * Math.sin(p.theta);
                let z = currentRadius * Math.cos(p.theta);

                let cosY = Math.cos(angleY * time * 10);
                let sinY = Math.sin(angleY * time * 10);
                let x1 = x * cosY - z * sinY;
                let z1 = z * cosY + x * sinY;

                let cosX = Math.cos(angleX * time * 10);
                let sinX = Math.sin(angleX * time * 10);
                let y1 = y * cosX - z1 * sinX;
                let z2 = z1 * cosX + y * sinX;

                let scale = 270 / (270 + z2);
                let projX = x1 * scale + width / 2;
                let projY = y1 * scale + height / 2;

                let alpha = (z2 + baseRadius) / (2 * baseRadius);

                ctx.beginPath();
                ctx.arc(projX, projY, Math.max(1, 2.5 * scale), 0, Math.PI * 2);

                if (i % 2 === 0) {
                    ctx.fillStyle = `rgba(88, 166, 255, ${Math.max(0.25, alpha)})`;
                    ctx.shadowColor = "#58a6ff";
                } else {
                    ctx.fillStyle = `rgba(188, 140, 255, ${Math.max(0.25, alpha)})`;
                    ctx.shadowColor = "#bc8cff";
                }
                ctx.shadowBlur = 12;
                ctx.fill();
            }

            requestAnimationFrame(draw);
        }
        draw();
    </script>
    """
    components.html(sphere_html, height=350)

# ------------------------
# SIDEBAR WITH ANIMATED LOGO
# ------------------------
with st.sidebar:
    if logo_b64:
        st.markdown(f"""<div class='animated-logo-container'><img src='data:image/png;base64,{logo_b64}' class='animated-logo' style='max-width: 140px;' alt='GoCode AI Logo'/></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='text-align: center; padding-bottom: 10px;'><h1 style='color: #58a6ff; margin-bottom: 0; font-size: 32px; font-weight: 800;'>⚡ GoCode AI</h1><p style='color: #8b949e; font-size: 12px;'>Your AI Powered Coding Assistant</p></div>""", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🤖 About GoCode AI",
            "👨‍💻 About Developer",
            "💬 GoCode Voice AI",
            "📄 Universal Document & Health AI",
            "🛡️ Security Vulnerability Scanner",
            "🎯 AI Tech Interviewer",
            "⚡ SQL & Database AI",
            "🧠 Time & Space Complexity (Big-O)",
            "🐞 Regex Pattern Wizard",
            "🌐 API & JSON Generator",
            "📝 Git Commit Generator",
            "🎨 CSS & Glassmorphism Generator",
            "🐞 Code Analyzer & Diff",
            "🔄 Code Translator",
            "📊 Flowchart Generator",
            "📚 Explain Code",
            "⚡ Optimize Code",
            "📄 README Generator",
            "🧪 Unit Tests",
            "📊 Code Review"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    APP_URL = "http://192.168.31.37:8501"
    qr_img = qrcode.make(APP_URL)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.markdown("""<div class='qr-container'><p style='color: #58a6ff; font-weight: 600; font-size: 13px; margin-bottom: 8px;'>📱 Scan for Mobile Access</p></div>""", unsafe_allow_html=True)
    st.image(byte_im, use_container_width=True)

    st.markdown("---")

    st.markdown("""<div class='developer-footer'>Crafted with ❤️<br><div class='developer-badge'>Developed by Yeshus Verma</div></div>""", unsafe_allow_html=True)

# ------------------------
# HELPER FUNCTION FOR CLEAN RENDER OF ABOUT CARD
# ------------------------
def render_about_card():
    st.markdown("""
<div class='info-card'>
<h2 style='color: #58a6ff; margin-top: 0;'>⚡ Next-Gen Developer Productivity Platform</h2>
<p style='color: #c9d1d9; font-size: 16px; line-height: 1.7;'>
<b>GoCode AI</b> is an advanced AI-powered software engineering suite engineered to eliminate repetitive coding bottlenecks, conduct full security audits, generate architectural diagrams, and provide real-time voice guidance.
</p>
<hr style='border-color: rgba(48, 54, 61, 0.6); margin: 20px 0;'>

<h3 style='color: #bc8cff;'>🧠 Core Capabilities Overview</h3>
<ul style='color: #c9d1d9; line-height: 1.9; font-size: 15px;'>
<li><b>🎙️ Voice AI Assistant:</b> Natural voice interaction with neural text-to-speech feedback.</li>
<li><b>🛡️ Cybersecurity Auditor:</b> Detects memory leaks, SQL injections, and security exploits in real-time.</li>
<li><b>🧠 Big-O Complexity Analyzer:</b> Evaluates exact Time & Space algorithmic complexity.</li>
<li><b>📐 Architecture Diagrams:</b> Generates Mermaid.js flowcharts directly from source code execution flows.</li>
<li><b>⚡ Database & API Suite:</b> Automated SQL query building, mock API generation, and Regex pattern crafting.</li>
</ul>

<h3 style='color: #bc8cff; margin-top: 25px;'>⚙️ Underlying Engine</h3>
<p style='color: #c9d1d9; font-size: 15px;'>
Powered by the state-of-the-art <b>Llama 3.3 70B Versatile Engine</b> via ultra-low latency Groq processing pipelines for instant streaming outputs.
</p>
</div>
""", unsafe_allow_html=True)

# ------------------------
# HOME PAGE
# ------------------------
if page == "🏠 Home":
    if logo_b64:
        st.markdown(f"""<div class='animated-logo-container' style='margin-bottom: 10px;'><img src='data:image/png;base64,{logo_b64}' style='max-width: 220px;' class='animated-logo' alt='GoCode AI Logo'/></div>""", unsafe_allow_html=True)

    st.markdown("<div class='big-title'>The future of building happens together</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>GoCode AI — Your Multi-Modal Intelligent Coding & Engineering Ecosystem</div>", unsafe_allow_html=True)
    render_developer_badge()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capabilities", "18+ Tools")
    c2.metric("AI Engine", "Llama 3.3 70B")
    c3.metric("Response", "⚡ Ultra Fast")
    c4.metric("Status", "Online")

    st.markdown("---")

    # Render Clean Card
    render_about_card()

    st.markdown("<h3 style='text-align: center; color: #58a6ff;'>🌐 Interactive 3D Voice Sphere</h3>", unsafe_allow_html=True)
    render_3d_sphere()

# ------------------------
# ABOUT GOCODE AI PAGE
# ------------------------
elif page == "🤖 About GoCode AI":
    st.markdown("<div class='big-title'>About GoCode AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Universal Multi-Modal AI Engineering Platform</div>", unsafe_allow_html=True)
    render_developer_badge()
    render_about_card()

# ------------------------
# ABOUT DEVELOPER PAGE
# ------------------------
elif page == "👨‍💻 About Developer":
    st.markdown("<div class='big-title'>About the Developer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Creator & Visionary Behind GoCode AI</div>", unsafe_allow_html=True)
    render_developer_badge()

    # Profile Photo & Brand Logo Gallery
    col1, col2 = st.columns(2)
    with col1:
        if dev1_b64:
            st.markdown(f"""<div style='text-align: center; padding: 10px;'><img src='data:image/jpeg;base64,{dev1_b64}' class='dev-photo-small' alt='Developer View'/></div>""", unsafe_allow_html=True)
        else:
            st.info("💡 Place 'dev1.jpg' in project folder to display your profile picture")

    with col2:
        if logo_b64:
            st.markdown(f"""<div style='text-align: center; padding: 20px;'><img src='data:image/png;base64,{logo_b64}' class='dev-logo-card' alt='GoCode Emblem'/></div>""", unsafe_allow_html=True)

    st.markdown("""
<div class='info-card'>
<div style='text-align: center;'>
<h1 style='color: #58a6ff; margin: 0; font-size: 38px;'>Yeshus Verma</h1>
<p style='color: #bc8cff; font-size: 18px; font-weight: 600; margin-top: 6px;'>
AI Engineer & Full-Stack Developer
</p>
<p style='color: #8b949e; font-size: 14px;'>
Class 11 PCM Student | DAV Public School, Kumarsain (Shimla District, H.P.)
</p>
</div>

<hr style='border-color: rgba(48, 54, 61, 0.6); margin: 25px 0;'>

<h3 style='color: #58a6ff;'>🚀 Background & Engineering Vision</h3>
<p style='color: #c9d1d9; line-height: 1.7; font-size: 15px;'>
I am a passionate software developer and AI engineer dedicated to building real-time artificial intelligence tools, glassmorphic web applications, and multi-modal software ecosystems. My primary focus is designing high-performance tools that automate coding workflows and make cutting-edge AI accessible to creators.
</p>

<h3 style='color: #bc8cff; margin-top: 25px;'>🛠️ Tech Stack & Expertise</h3>
<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
<span class='tech-tag'>Python</span>
<span class='tech-tag'>C++</span>
<span class='tech-tag'>AI Engineering</span>
<span class='tech-tag-purple'>Streamlit / UI Engineering</span>
<span class='tech-tag-purple'>Groq / LLM Integration</span>
<span class='tech-tag-purple'>Glassmorphic Design</span>
</div>

<h3 style='color: #58a6ff; margin-top: 25px;'>🌟 Creative Pursuits</h3>
<p style='color: #c9d1d9; line-height: 1.7; font-size: 15px;'>
In addition to coding and technological development, I actively engage in sports like badminton, music vocalization, and traditional <b>Pahadi Nati</b> folk dance performances celebrating Himachali heritage.
</p>
</div>
""", unsafe_allow_html=True)

# ------------------------
# VOICE AI
# ------------------------
elif page == "💬 GoCode Voice AI":
    st.markdown("<div class='big-title'>GoCode Voice AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Speak with your AI Mentor in Real-Time</div>", unsafe_allow_html=True)
    render_developer_badge()

    render_3d_sphere()

    raw_speech = speech_to_text(
        language='en',
        start_prompt="🔴 Click & Start Speaking",
        stop_prompt="🟩 Listening... Click when Done",
        just_once=True,
        key='voice_recorder'
    )

    if raw_speech:
        st.session_state.spoken_text = raw_speech

    current_speech = st.session_state.spoken_text
    display_text = current_speech if current_speech else "Click the mic above and speak... Your live words will appear here!"

    st.markdown(f"""
<div class='live-speech-card'>
<p style='color: #8b949e; font-size: 11px; letter-spacing: 1px; font-weight: 700; margin-bottom: 6px;'>LIVE VOICE SPECTRUM & TRANSCRIPTION</p>
<h4 style='color: #58a6ff; margin: 0; font-size: 20px;'>"{display_text}"</h4>
<div class='equalizer-container'>
<div class='equalizer-bar' style='animation-delay: 0.1s;'></div>
<div class='equalizer-bar' style='animation-delay: 0.4s;'></div>
<div class='equalizer-bar' style='animation-delay: 0.2s;'></div>
<div class='equalizer-bar' style='animation-delay: 0.6s;'></div>
<div class='equalizer-bar' style='animation-delay: 0.3s;'></div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    accent_option = st.selectbox(
        "🎙️ Choose Voice Accent:",
        ["English (US - Natural)", "English (UK - Professional)", "English (India - Clear)"],
        index=0
    )

    accent_map = {
        "English (US - Natural)": "en",
        "English (UK - Professional)": "co.uk",
        "English (India - Clear)": "co.in"
    }

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 💬 Your Question:")
        user_input = st.text_input("Edit or Type Question:", value=st.session_state.spoken_text)
        ask_button = st.button("🚀 Send to GoCode AI", use_container_width=True)

    with col2:
        st.markdown("### 💬 Real-Time Conversation")

        if ask_button or (raw_speech and user_input):
            query = user_input.strip()
            if query:
                with st.spinner("⚡ GoCode AI is processing..."):
                    ai_response = ask_ai(query)
                    st.session_state.chat_history.insert(0, {"user": query, "ai": ai_response})

                    speak_text_neural(ai_response, accent_code=accent_map.get(accent_option, "en"))
            else:
                st.warning("Please record your voice or type a message first.")

        if st.session_state.chat_history:
            for item in st.session_state.chat_history:
                st.markdown(f"""
<div class='chat-box-user'>
<b>🗣️ You Said:</b><br>{item['user']}
</div>
<div class='chat-box-ai'>
<b>⚡ GoCode AI:</b><br>{item['ai']}
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Click the mic button above to start talking!")

# ------------------------
# TOOL 1: SQL & DATABASE AI
# ------------------------
elif page == "⚡ SQL & Database AI":
    st.markdown("<div class='big-title'>SQL & Database AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Convert Natural Text to Complex Queries & Optimize Schemas</div>", unsafe_allow_html=True)
    render_developer_badge()

    sql_prompt = st.text_area("Describe the database query or schema you need in plain English:", height=160)
    db_type = st.selectbox("Database Engine:", ["PostgreSQL", "MySQL", "SQLite", "MongoDB", "Oracle"])

    if st.button("🚀 Generate SQL Query"):
        if not sql_prompt.strip():
            st.warning("Please enter a query description first.")
        else:
            prompt = f"Write an optimized {db_type} query for: '{sql_prompt}'. Provide the code block followed by a brief step-by-step breakdown."
            with st.spinner("Generating database query..."):
                query_res = ask_ai(prompt)
            st.markdown("### 🗄️ Generated Database Solution")
            st.markdown(query_res)

# ------------------------
# TOOL 2: REGEX PATTERN WIZARD
# ------------------------
elif page == "🐞 Regex Pattern Wizard":
    st.markdown("<div class='big-title'>Regex Pattern Wizard</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Build & Explain Complex Regular Expressions Effortlessly</div>", unsafe_allow_html=True)
    render_developer_badge()

    regex_req = st.text_input("What pattern do you want to match? (e.g., 'Validate phone number format'):")
    target_lang = st.selectbox("Programming Language:", ["Python", "JavaScript", "Java", "C++", "PHP"])

    if st.button("⚡ Generate Regex Pattern"):
        if not regex_req.strip():
            st.warning("Please describe the pattern requirement.")
        else:
            prompt = f"Provide a clean Regular Expression (Regex) for: '{regex_req}'. Include the regex pattern, explanation of symbols, and a working code snippet in {target_lang}."
            with st.spinner("Generating Regex..."):
                regex_res = ask_ai(prompt)
            st.markdown("### 🔍 Regex Solution")
            st.markdown(regex_res)

# ------------------------
# TOOL 3: API & JSON GENERATOR
# ------------------------
elif page == "🌐 API & JSON Generator":
    st.markdown("<div class='big-title'>API & JSON Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Generate Mock API Data, REST Endpoints & cURL Commands</div>", unsafe_allow_html=True)
    render_developer_badge()

    api_desc = st.text_area("Describe the API endpoint or JSON structure needed:", height=150)
    framework = st.selectbox("Framework:", ["FastAPI (Python)", "Express.js (Node)", "Flask", "Raw JSON Mock Data"])

    if st.button("🚀 Build API Endpoint"):
        if not api_desc.strip():
            st.warning("Please enter your API requirements.")
        else:
            prompt = f"Create a production-ready API endpoint for: '{api_desc}' using {framework}. Provide code, sample payload, and cURL command."
            with st.spinner("Building API structure..."):
                api_res = ask_ai(prompt)
            st.markdown("### 🌐 API Endpoint Code")
            st.markdown(api_res)

# ------------------------
# TOOL 4: GIT COMMIT GENERATOR
# ------------------------
elif page == "📝 Git Commit Generator":
    st.markdown("<div class='big-title'>Git Commit Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Convert Code Changes into Conventional Commits & Pull Requests</div>", unsafe_allow_html=True)
    render_developer_badge()

    git_diff = st.text_area("Paste your code changes or diff summary here:", height=200)

    if st.button("📝 Generate Commit Message"):
        if not git_diff.strip():
            st.warning("Please paste changes or diff text.")
        else:
            prompt = f"Generate 3 clear Conventional Commit messages (feat:, fix:, docs:, refactor:) and a detailed GitHub PR summary for these code changes:\n{git_diff}"
            with st.spinner("Analyzing changes..."):
                commit_res = ask_ai(prompt)
            st.markdown("### 📌 Git Commit & PR Summary")
            st.markdown(commit_res)

# ------------------------
# TOOL 5: CSS & GLASSMORPHISM GENERATOR
# ------------------------
elif page == "🎨 CSS & Glassmorphism Generator":
    st.markdown("<div class='big-title'>CSS & UI Style Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Create Modern Glassmorphism Cards, Neon Effects & Animations</div>", unsafe_allow_html=True)
    render_developer_badge()

    ui_req = st.text_input("Describe the UI element (e.g., 'Glow button with purple gradient hover effect'):")

    if st.button("✨ Generate CSS"):
        if not ui_req.strip():
            st.warning("Please describe the UI element.")
        else:
            prompt = f"Generate modern HTML & CSS code for: '{ui_req}'. Include CSS variables, hover effects, and glassmorphism backdrop-filter if applicable."
            with st.spinner("Crafting CSS styles..."):
                css_res = ask_ai(prompt)
            st.markdown("### 🎨 Rendered Code & CSS")
            st.markdown(css_res)

# ------------------------
# FEATURE: UNIVERSAL DOCUMENT & HEALTH REPORT AI
# ------------------------
elif page == "📄 Universal Document & Health AI":
    st.markdown("<div class='big-title'>Document & Health AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Analyze Medical Lab Reports, Health Metrics, or Academic Documents</div>", unsafe_allow_html=True)
    render_developer_badge()

    doc_file = st.file_uploader("Upload Medical Report / Text Document", type=["txt", "csv", "log"])
    doc_text_input = st.text_area("Or Paste Report Text directly:", height=180)

    if doc_file:
        doc_text = doc_file.read().decode("utf-8")
    else:
        doc_text = doc_text_input

    if st.button("🔬 Analyze Document Metrics"):
        if not doc_text.strip():
            st.warning("Please upload a file or paste document text first.")
        else:
            prompt = f"""
You are an advanced Multi-Modal AI Document & Health Analyst.
Analyze the following text or report:

1. Executive Summary & Overview
2. Key Findings & Identified Metrics
3. Highlighted Abnormalities / Flags (if health or lab report)
4. Simplified Plain-Language Explanation
5. Recommended Next Steps or Follow-up Considerations

Document Content:
{doc_text}
"""
            with st.spinner("Analyzing document metrics..."):
                analysis_res = ask_ai(prompt)
            st.markdown("### 📋 GoCode AI Analysis Report")
            st.markdown(analysis_res)

# ------------------------
# FEATURE: SECURITY VULNERABILITY SCANNER
# ------------------------
elif page == "🛡️ Security Vulnerability Scanner":
    st.markdown("<div class='big-title'>Cyber Security Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Detect Security Vulnerabilities & Code Exploits</div>", unsafe_allow_html=True)
    render_developer_badge()

    code_sec = st.text_area("Paste Code to Scan for Security Vulnerabilities", height=220)
    lang_sec = st.selectbox("Language", ["Python", "Java", "C++", "JavaScript", "C", "HTML", "Rust"])

    if st.button("🔍 Run Security Audit"):
        if not code_sec.strip():
            st.warning("Please paste code first.")
        else:
            prompt = f"Perform a cybersecurity audit on this {lang_sec} code. Output in Markdown format:\n1. Threat Level (LOW, MEDIUM, CRITICAL)\n2. Vulnerabilities Found (SQL injection, hardcoded secrets, memory leaks, etc.)\n3. Attack Vectors\n4. Patched / Secure Version of the code:\n\nCode:\n{code_sec}"
            with st.spinner("Auditing codebase for security threats..."):
                audit_res = ask_ai(prompt)
            st.markdown("### 🛡️ Cybersecurity Audit Report")
            st.markdown(audit_res)

# ------------------------
# FEATURE: AI TECH INTERVIEWER
# ------------------------
elif page == "🎯 AI Tech Interviewer":
    st.markdown("<div class='big-title'>AI Tech Interviewer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Interactive Coding & Technical Practice</div>", unsafe_allow_html=True)
    render_developer_badge()

    target_role = st.selectbox("Target Role / Topic:", ["Python Developer", "Data Structures & Algorithms", "Full-Stack Web Dev", "AI Engineering"])
    user_ans = st.text_area("Your Answer / Code Solution:", height=150)

    if st.button("🚀 Submit to Interviewer"):
        if not user_ans.strip():
            st.warning("Please enter your response to start the interview evaluation.")
        else:
            prompt = f"You are a Senior Tech Interviewer evaluating a candidate for {target_role}. Review this candidate's response: '{user_ans}'. Give:\n1. Score /10\n2. Correctness & Quality\n3. Follow-up Technical Question"
            with st.spinner("Evaluating response..."):
                feedback = ask_ai(prompt)
            st.markdown("### 📋 GoCode Interviewer Feedback")
            st.markdown(feedback)

# ------------------------
# COMMON CODE INPUT FOR CODE-BASED TOOLS
# ------------------------
code = ""
language = "Python"

if page in [
    "🧠 Time & Space Complexity (Big-O)",
    "🐞 Code Analyzer & Diff",
    "🔄 Code Translator",
    "📊 Flowchart Generator",
    "📚 Explain Code",
    "⚡ Optimize Code",
    "📄 README Generator",
    "🧪 Unit Tests",
    "📊 Code Review"
]:
    st.markdown(f"<div class='big-title'>{page}</div>", unsafe_allow_html=True)
    render_developer_badge()

    if page != "📄 README Generator":
        uploaded = st.file_uploader("Upload Code File", type=["py", "cpp", "java", "js", "html", "css", "rs"])
        if uploaded:
            code = uploaded.read().decode("utf-8")
        else:
            code = st.text_area("Paste Code", height=220)

        language = st.selectbox("Language", ["Python", "Java", "C++", "JavaScript", "C", "HTML", "CSS", "Rust"])

# ------------------------
# TOOL 6: BIG-O COMPLEXITY ANALYZER
# ------------------------
if page == "🧠 Time & Space Complexity (Big-O)":
    if st.button("📊 Calculate Complexity"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Analyze the Time Complexity and Space Complexity of this {language} code. Output the Big-O notation clearly ($O(N)$, $O(\\log N)$, etc.), explain why, and list performance bottlenecks:\n{code}"
            with st.spinner("Analyzing algorithmic complexity..."):
                complexity_res = ask_ai(prompt)
            st.markdown("### 📈 Big-O Analysis Report")
            st.markdown(complexity_res)

# ------------------------
# FEATURE: CODE ANALYZER & DIFF VIEWER
# ------------------------
elif page == "🐞 Code Analyzer & Diff":
    if st.button("🚀 Analyze & Fix Code"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Analyze this {language} code. First provide a Markdown explanation of errors and complexity. Then provide ONLY the complete fixed code inside a markdown block:\n{code}"
            with st.spinner("Analyzing code..."):
                answer = ask_ai(prompt)
            st.success("Analysis & Bug Fix Complete!")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔴 Original Code")
                st.code(code, language=language.lower())
            with c2:
                st.markdown("#### 🟢 AI Explanation & Fix")
                st.markdown(answer)

# ------------------------
# FEATURE: CODE TRANSLATOR
# ------------------------
elif page == "🔄 Code Translator":
    target_lang = st.selectbox("Convert Code To:", ["C++", "Java", "Python", "JavaScript", "Rust", "Go"])
    if st.button("⚡ Convert Code"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Convert this {language} code accurately into {target_lang}. Preserve all logic and add brief inline comments explaining key changes:\n{code}"
            with st.spinner(f"Converting to {target_lang}..."):
                converted = ask_ai(prompt)
            st.markdown(f"### 🚀 Translated Code ({target_lang})")
            st.markdown(converted)

# ------------------------
# FEATURE: FLOWCHART GENERATOR
# ------------------------
elif page == "📊 Flowchart Generator":
    if st.button("Generate Architecture Diagram"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Generate a valid Mermaid.js flowchart block (```mermaid ... ```) depicting the execution flow of this {language} code:\n{code}"
            with st.spinner("Building Flowchart..."):
                chart_response = ask_ai(prompt)
            st.markdown("### 📐 Code Logic Architecture")
            st.markdown(chart_response)

# ------------------------
# FEATURE: EXPLAIN CODE
# ------------------------
elif page == "📚 Explain Code":
    if st.button("Explain Code"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Explain every key line of this {language} code clearly for beginners:\n{code}"
            with st.spinner("Explaining code..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

# ------------------------
# FEATURE: OPTIMIZE CODE
# ------------------------
elif page == "⚡ Optimize Code":
    if st.button("Optimize Code"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Optimize this {language} code without changing functionality:\n{code}"
            with st.spinner("Optimizing code..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

    if code.strip():
        st.download_button(label="⬇ Download Current Code", data=code, file_name="optimized_code.py")

# ------------------------
# FEATURE: README GENERATOR
# ------------------------
elif page == "📄 README Generator":
    project_name = st.text_input("Project Name")

    if st.button("Generate README"):
        if not project_name.strip():
            st.warning("Please specify a project name.")
        else:
            prompt = f"Generate a complete markdown GitHub README.md for project: {project_name}"
            with st.spinner("Generating README..."):
                readme_content = ask_ai(prompt)
            st.markdown(readme_content)
            st.download_button(label="⬇ Download README.md", data=readme_content, file_name="README.md")

# ------------------------
# FEATURE: UNIT TESTS
# ------------------------
elif page == "🧪 Unit Tests":
    if st.button("Generate Unit Tests"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Generate unit tests for this {language} code:\n{code}"
            with st.spinner("Generating unit tests..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

# ------------------------
# FEATURE: CODE REVIEW
# ------------------------
elif page == "📊 Code Review":
    if st.button("Review Code"):
        if not code.strip():
            st.warning("Please paste or upload code first.")
        else:
            prompt = f"Perform a comprehensive code review for this {language} code:\n{code}"
            with st.spinner("Reviewing code..."):
                answer = ask_ai(prompt)
            st.markdown(answer)
