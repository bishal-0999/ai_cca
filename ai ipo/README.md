# 🛡️ IPO Scoring Engine & Analyzer

An AI-powered 100-point scoring engine for IPO listings. Paste any IPO detail page link (Chittorgarh, IPOWatch, etc.) and instantly get a data-driven recommendation.

## Features

- 🔍 **Auto-scrapes** the IPO page you paste — no manual copy-pasting
- 🤖 **Gemini AI** extracts QIB, NII, Retail subscription multiples, GMP, financials, valuation, and sentiment
- 📊 **100-point rubric** scores and recommends: Strong Apply 💰 / Apply 👍 / Risky ⚠️ / Avoid ❌
- 🌑 **Premium dark glassmorphic UI** built in React + Vanilla CSS
- 🕐 **Search history** saved locally in the browser

## Tech Stack

- **Frontend**: React (Vite), Vanilla CSS
- **Backend**: Node.js + Express + Cheerio (web scraping)
- **AI**: [OpenRouter](https://openrouter.ai) → Google Gemini 2.5 Flash

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/bishal-0999/ai_cca.git
cd ai_cca
```

### 2. Install dependencies

```bash
npm install
```

### 3. Add your OpenRouter API key

Create the file `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

Or export it as an environment variable:

```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys).

### 4. Run the app

```bash
npm run start
```

This starts both the Express backend (port 3001) and React frontend (port 5173) concurrently.

Open **http://localhost:5173** in your browser.

## Supported Sites

| Site | Works? |
|------|--------|
| chittorgarh.com | ✅ |
| ipowatch.in | ✅ |
| investorgain.com | ✅ |
| zerodha.com | ❌ Requires login/JS |

## Scoring Rubric

| Metric | Max Points |
|--------|-----------|
| QIB Subscription | 20 |
| NII Subscription | 10 |
| Retail Subscription | 10 |
| GMP Premium | 25 |
| Financial Growth | 20 |
| Valuation | 10 |
| Market Sentiment | 5 |
| **Total** | **100** |
