import os
import json

import requests
import streamlit as st
from bs4 import BeautifulSoup
from openai import OpenAI

# --- 1. INITIALIZE AI (OpenRouter) ---
def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except (KeyError, FileNotFoundError, AttributeError):
        return None

api_key = get_api_key()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key) if api_key else None

st.set_page_config(page_title="IPO Scoring Engine 2.1", layout="wide", page_icon="💰")

# --- 2. AI DATA EXTRACTION FUNCTION ---
def extract_data_with_ai(raw_text):
    """Parses text to find specific values required for the 100-point rubric."""
    prompt = f"""
    Extract the following IPO metrics. Return ONLY a JSON object with these keys: 
    "qib_x", "nii_x", "retail_x", "gmp_pct", "financial_growth", "valuation_status", "sentiment".
    
    Rules:
    - qib_x, nii_x, retail_x: Subscription multiples (numbers only).
    - gmp_pct: Percentage premium (number only).
    - financial_growth: "Strong", "Moderate", "Weak", or "Loss-making".
    - valuation_status: "Undervalued", "Fair", or "Overpriced".
    - sentiment: "Bullish", "Neutral", or "Bearish".

    TEXT: {raw_text[:5000]}
    """
    if not client:
        st.error("Missing OpenRouter API key. Add OPENROUTER_API_KEY to `.streamlit/secrets.toml`.")
        return None

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- 3. THE 100-POINT SCORING BRAIN ---
def calculate_100_point_score(data):
    """Applies the exact Step 2 logic provided in the prompt."""
    try:
        # Convert to floats to ensure numeric safety
        qib = float(data.get('qib_x', 0))
        nii = float(data.get('nii_x', 0))
        ret = float(data.get('retail_x', 0))
        gmp = float(data.get('gmp_pct', 0))
    except:
        qib = nii = ret = gmp = 0

    # 🔷 QIB Scoring (Max 20)
    if qib > 20: qib_score = 20
    elif qib >= 10: qib_score = 15
    elif qib >= 5: qib_score = 10
    elif qib >= 1: qib_score = 5
    else: qib_score = 0

    # 🔷 NII Scoring (Max 10)
    if nii > 15: nii_score = 10
    elif nii >= 5: nii_score = 7
    elif nii >= 1: nii_score = 4
    else: nii_score = 0

    # 🔷 Retail Scoring (Max 10)
    if ret > 10: ret_score = 10
    elif ret >= 5: ret_score = 7
    elif ret >= 2: ret_score = 4
    else: ret_score = 0

    # 🔷 GMP Scoring (Max 25)
    if gmp > 50: gmp_score = 25
    elif gmp >= 30: gmp_score = 20
    elif gmp >= 15: gmp_score = 15
    elif gmp >= 5: gmp_score = 10
    else: gmp_score = 0

    # 🔷 Financials (Max 20)
    fin_status = data.get('financial_growth', 'Weak')
    if fin_status == "Strong": fin_score = 20
    elif fin_status == "Moderate": fin_score = 14 # Average of 12-15
    elif fin_status == "Weak": fin_score = 8 # Average of 5-10
    else: fin_score = 0 # Loss-making

    # 🔷 Valuation (Max 10)
    val_status = data.get('valuation_status', 'Fair')
    if val_status == "Undervalued": val_score = 10
    elif val_status == "Fair": val_score = 5
    else: val_score = 0

    # 🔷 Market Sentiment (Max 5)
    sent_status = data.get('sentiment', 'Neutral')
    if sent_status == "Bullish": sent_score = 5
    elif sent_status == "Neutral": sent_score = 3
    else: sent_score = 0

    total = qib_score + nii_score + ret_score + gmp_score + fin_score + val_score + sent_score
    return total, {
        "QIB": qib_score, "NII": nii_score, "Retail": ret_score, 
        "GMP": gmp_score, "Financials": fin_score, 
        "Valuation": val_score, "Sentiment": sent_score
    }

# --- 4. WEB INTERFACE ---
st.title("🛡️ IPO Analyzer 2.1 (100-Point Rubric)")
st.markdown("Your custom logic is now live. Paste IPO news or a URL below.")

target_url = st.text_input("Paste IPO Detail URL (Chittorgarh/News)")

if st.button("🚀 Analyze & Generate Decision"):
    if target_url:
        with st.spinner("AI is applying your scoring rules..."):
            # Fetch and Parse
            resp = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"})
            raw_text = BeautifulSoup(resp.text, 'html.parser').get_text()
            
            # AI Extraction
            ai_data = extract_data_with_ai(raw_text)
            if ai_data:
                parsed_data = json.loads(ai_data)
                final_score, breakdowns = calculate_100_point_score(parsed_data)
                
                # --- Decision Output (Step 3) ---
                st.divider()
                if final_score >= 80:
                    st.header(f"Score: {final_score} - Strong Apply 💰")
                    st.balloons()
                elif final_score >= 60:
                    st.header(f"Score: {final_score} - Apply 👍")
                elif final_score >= 40:
                    st.header(f"Score: {final_score} - Risky ⚠️")
                else:
                    st.header(f"Score: {final_score} - Avoid ❌")

                # Visual Breakdown
                cols = st.columns(7)
                for i, (metric, val) in enumerate(breakdowns.items()):
                    cols[i].metric(metric, val)
                
                st.json(parsed_data)
    else:
        st.warning("Please provide a URL to fetch data.")
