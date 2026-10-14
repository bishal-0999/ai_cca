"""
EcoAwareness AI - Environmental Awareness Poster & Content Generator
====================================================================
This application uses Google Gemini AI to generate environmental awareness
content (headlines, messages, tips, slogans) and creates a downloadable poster.

How it works (for beginners):
1. User enters a topic (e.g., "Save Trees")
2. User picks a language (English, Hindi, or Kannada)
3. The app sends the topic to Gemini AI and gets back awareness content
4. The app draws a poster using Pillow (Python image library)
5. User can download the poster as a PNG image
"""

import streamlit as st          # For building the web UI
import os                       # For reading environment variables (API key)
import json                     # For parsing AI response
import io                       # For handling image in memory
from dotenv import load_dotenv  # For loading .env file

# Load API key from .env file (if it exists)
load_dotenv()

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoAwareness AI",
    page_icon="🌿",
    layout="centered"
)

# ─── Import our helper modules ────────────────────────────────────────────────
from content_generator import generate_awareness_content
from poster_creator import create_poster

# ─── Custom CSS Styling ───────────────────────────────────────────────────────
# This block styles the page with a clean green-and-white environmental theme
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* ── General Page ── */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #ffffff 100%);
    min-height: 100vh;
}

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 40%, #388e3c 100%);
    border-radius: 20px;
    padding: 40px 30px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(27, 94, 32, 0.25);
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.hero-emoji {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 10px;
}

.hero-description {
    font-size: 1.05rem;
    color: #c8e6c9;
    margin-top: 12px;
    max-width: 560px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

/* ── Input Card ── */
.input-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 24px;
    border: 1px solid #e8f5e9;
}

.section-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #2e7d32;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input {
    border: 2px solid #a5d6a7 !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    color: #1b5e20 !important;
    background: #f9fbe7 !important;
    transition: border-color 0.2s;
}

.stTextInput > div > div > input:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important;
}

.stSelectbox > div > div {
    border: 2px solid #a5d6a7 !important;
    border-radius: 10px !important;
    background: #f9fbe7 !important;
    color: #1b5e20 !important;
}

/* ── Generate Button ── */
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    padding: 14px 36px !important;
    border: none !important;
    border-radius: 12px !important;
    width: 100% !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(46,125,50,0.35) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    box-shadow: 0 6px 20px rgba(46,125,50,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Content Result Cards ── */
.result-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    margin-bottom: 20px;
    border-left: 5px solid #4caf50;
}

.result-card h3 {
    color: #1b5e20;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.result-card .headline-text {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2e7d32;
    line-height: 1.4;
}

.result-card .message-text {
    font-size: 1rem;
    color: #424242;
    line-height: 1.7;
}

.result-card .slogan-text {
    font-size: 1.2rem;
    font-weight: 600;
    color: #388e3c;
    font-style: italic;
    text-align: center;
}

/* ── Tips list ── */
.tip-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid #f1f8e9;
    font-size: 0.97rem;
    color: #37474f;
    line-height: 1.6;
}
.tip-item:last-child { border-bottom: none; }
.tip-emoji { font-size: 1.2rem; flex-shrink: 0; }

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #00695c, #00897b) !important;
    color: white !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 30px !important;
    border: none !important;
    border-radius: 12px !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(0,105,92,0.35) !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #004d40, #00695c) !important;
}

/* ── Divider ── */
.eco-divider {
    text-align: center;
    color: #a5d6a7;
    font-size: 1.5rem;
    margin: 10px 0;
    letter-spacing: 4px;
}

/* ── Footer ── */
.eco-footer {
    text-align: center;
    color: #81c784;
    font-size: 0.82rem;
    margin-top: 40px;
    padding-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <span class="hero-emoji">🌍</span>
    <h1 class="hero-title">EcoAwareness AI</h1>
    <p class="hero-description">
        Enter any environmental topic and let AI generate a beautiful
        awareness poster with a headline, message, tips, and slogan —
        ready to download and share! 🌱
    </p>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

# Topic examples shown as hint
TOPIC_EXAMPLES = [
    "Save Trees", "Save Water", "Reduce Plastic Pollution",
    "Climate Change", "Renewable Energy", "Air Pollution",
    "Wildlife Conservation", "Ocean Pollution"
]

st.markdown('<p class="section-label">🌿 Environmental Topic</p>', unsafe_allow_html=True)
topic = st.text_input(
    label="topic_input",
    label_visibility="collapsed",
    placeholder="e.g. Save Trees, Save Water, Reduce Plastic Pollution...",
    max_chars=100
)

# Show clickable example chips using columns
st.markdown('<p style="font-size:0.8rem; color:#81c784; margin-top:6px;">Quick examples:</p>', unsafe_allow_html=True)
example_cols = st.columns(4)
for idx, example in enumerate(TOPIC_EXAMPLES):
    with example_cols[idx % 4]:
        if st.button(example, key=f"ex_{idx}", use_container_width=True):
            # When example button clicked, store it in session state
            st.session_state["selected_topic"] = example
            st.rerun()

# Use session state topic if an example was clicked
if "selected_topic" in st.session_state and not topic:
    topic = st.session_state["selected_topic"]

st.markdown("<br>", unsafe_allow_html=True)

# Language selection
st.markdown('<p class="section-label">🌐 Select Language</p>', unsafe_allow_html=True)
LANGUAGES = {
    "English 🇬🇧": "English",
    "Hindi 🇮🇳 (हिंदी)": "Hindi",
    "Kannada 🇮🇳 (ಕನ್ನಡ)": "Kannada",
}
selected_display = st.selectbox(
    label="language_selector",
    label_visibility="collapsed",
    options=list(LANGUAGES.keys())
)
selected_language = LANGUAGES[selected_display]

st.markdown("<br>", unsafe_allow_html=True)

# Generate button
generate_clicked = st.button("🌱 Generate Awareness Content", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)  # close input-card


# ─── Main Generation Logic ────────────────────────────────────────────────────
if generate_clicked:
    # Validate that user typed something
    if not topic or topic.strip() == "":
        st.warning("⚠️ Please enter an environmental topic before generating content.")
        st.stop()

    # ── Step 1: Generate content with local Ollama AI ──
    with st.spinner("🤖 Local AI is generating awareness content... Please wait (this may take ~20 seconds)!"):
        content, error = generate_awareness_content(
            topic=topic.strip(),
            language=selected_language
        )

    if error:
        st.error(f"❌ **Content Generation Failed:** {error}\n\nPlease check your API key and try again.")
        st.stop()

    # ── Step 2: Display the generated content ──
    st.markdown('<div class="eco-divider">🌿 🌍 🌿</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Headline
    st.markdown(f"""
    <div class="result-card">
        <h3>📢 Headline</h3>
        <p class="headline-text">{content['headline']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Awareness Message
    st.markdown(f"""
    <div class="result-card">
        <h3>💬 Awareness Message</h3>
        <p class="message-text">{content['message']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Tips
    tip_emojis = ["🌱", "♻️", "💧"]
    tips_html = ""
    for i, tip in enumerate(content["tips"]):
        emoji = tip_emojis[i] if i < len(tip_emojis) else "✅"
        tips_html += f'<div class="tip-item"><span class="tip-emoji">{emoji}</span><span>{tip}</span></div>'

    st.markdown(f"""
    <div class="result-card">
        <h3>💡 3 Simple Tips</h3>
        {tips_html}
    </div>
    """, unsafe_allow_html=True)

    # Slogan
    st.markdown(f"""
    <div class="result-card">
        <h3>✨ Catchy Slogan</h3>
        <p class="slogan-text">"{content['slogan']}"</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Step 3: Generate the poster image ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🖼️ Your Environmental Awareness Poster")

    with st.spinner("🎨 Creating your poster..."):
        poster_image = create_poster(
            topic=topic.strip(),
            headline=content["headline"],
            message=content["message"],
            tips=content["tips"],
            slogan=content["slogan"],
            language=selected_language
        )

    # Convert PIL image to bytes for display & download
    img_bytes = io.BytesIO()
    poster_image.save(img_bytes, format="PNG", dpi=(150, 150))
    img_bytes.seek(0)

    # Display the poster
    st.image(img_bytes, use_container_width=True, caption="🌍 Your Generated Awareness Poster")

    # ── Step 4: Download button ──
    st.markdown("<br>", unsafe_allow_html=True)

    # Reset BytesIO pointer for download
    img_bytes.seek(0)
    file_name = f"EcoAwareness_{topic.strip().replace(' ', '_')}.png"

    st.download_button(
        label="⬇️ Download Poster as Image",
        data=img_bytes,
        file_name=file_name,
        mime="image/png",
        use_container_width=True
    )

    st.success(f"✅ Poster generated successfully for **'{topic}'** in **{selected_language}**!")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="eco-footer">
    🌿 EcoAwareness AI &nbsp;|&nbsp; Powered by Google Gemini AI &nbsp;|&nbsp;
    Together, let's protect our planet 🌍
</div>
""", unsafe_allow_html=True)
