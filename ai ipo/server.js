import express from 'express';
import cors from 'cors';
import * as cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Helper to retrieve API key from env or .streamlit/secrets.toml
function getApiKey() {
  let apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    try {
      const secretsPath = path.join(__dirname, '.streamlit', 'secrets.toml');
      if (fs.existsSync(secretsPath)) {
        const secretsText = fs.readFileSync(secretsPath, 'utf-8');
        const match = secretsText.match(/OPENROUTER_API_KEY\s*=\s*["']([^"']+)["']/);
        if (match && match[1]) {
          apiKey = match[1];
        }
      }
    } catch (err) {
      console.error("Error reading secrets.toml:", err);
    }
  }
  return apiKey;
}

// Calculate the 100-point rubric score
function calculateScore(data) {
  let qib = parseFloat(data.qib_x) || 0;
  let nii = parseFloat(data.nii_x) || 0;
  let ret = parseFloat(data.retail_x) || 0;
  let gmp = parseFloat(data.gmp_pct) || 0;

  // QIB Scoring (Max 20)
  let qib_score = 0;
  if (qib > 20) qib_score = 20;
  else if (qib >= 10) qib_score = 15;
  else if (qib >= 5) qib_score = 10;
  else if (qib >= 1) qib_score = 5;

  // NII Scoring (Max 10)
  let nii_score = 0;
  if (nii > 15) nii_score = 10;
  else if (nii >= 5) nii_score = 7;
  else if (nii >= 1) nii_score = 4;

  // Retail Scoring (Max 10)
  let ret_score = 0;
  if (ret > 10) ret_score = 10;
  else if (ret >= 5) ret_score = 7;
  else if (ret >= 2) ret_score = 4;

  // GMP Scoring (Max 25)
  let gmp_score = 0;
  if (gmp > 50) gmp_score = 25;
  else if (gmp >= 30) gmp_score = 20;
  else if (gmp >= 15) gmp_score = 15;
  else if (gmp >= 5) gmp_score = 10;

  // Financials (Max 20)
  const fin_status = data.financial_growth || 'Weak';
  let fin_score = 0;
  if (fin_status === "Strong") fin_score = 20;
  else if (fin_status === "Moderate") fin_score = 14;
  else if (fin_status === "Weak") fin_score = 8;
  else fin_score = 0; // Loss-making

  // Valuation (Max 10)
  const val_status = data.valuation_status || 'Fair';
  let val_score = 5;
  if (val_status === "Undervalued") val_score = 10;
  else if (val_status === "Fair") val_score = 5;
  else if (val_status === "Overpriced") val_score = 0;

  // Market Sentiment (Max 5)
  const sent_status = data.sentiment || 'Neutral';
  let sent_score = 3;
  if (sent_status === "Bullish") sent_score = 5;
  else if (sent_status === "Neutral") sent_score = 3;
  else if (sent_status === "Bearish") sent_score = 0;

  const total = qib_score + nii_score + ret_score + gmp_score + fin_score + val_score + sent_score;

  // Determine decision recommendations
  let decision = "Avoid";
  let badge = "❌";
  if (total >= 80) {
    decision = "Strong Apply";
    badge = "💰";
  } else if (total >= 60) {
    decision = "Apply";
    badge = "👍";
  } else if (total >= 40) {
    decision = "Risky";
    badge = "⚠️";
  }

  return {
    total,
    decision,
    badge,
    breakdown: {
      QIB: { score: qib_score, max: 20, value: `${qib}x` },
      NII: { score: nii_score, max: 10, value: `${nii}x` },
      Retail: { score: ret_score, max: 10, value: `${ret}x` },
      GMP: { score: gmp_score, max: 25, value: `${gmp}%` },
      Financials: { score: fin_score, max: 20, value: fin_status },
      Valuation: { score: val_score, max: 10, value: val_status },
      Sentiment: { score: sent_score, max: 5, value: sent_status }
    }
  };
}

// Scrape URL and extract raw text content
async function scrapeUrl(targetUrl) {
  const USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  ];

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  let response;
  try {
    response = await fetch(targetUrl, {
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        'User-Agent': USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Upgrade-Insecure-Requests': '1'
      }
    });
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('The page took too long to respond (15 second timeout). Try a different URL.');
    }
    throw new Error(`Network error fetching page: ${err.message}`);
  } finally {
    clearTimeout(timeout);
  }

  if (!response.ok) {
    if (response.status === 403 || response.status === 401) {
      throw new Error(`Access denied by the website (HTTP ${response.status}). This site may block automated requests. Try a Chittorgarh or IPOWatch URL instead.`);
    }
    if (response.status === 404) {
      throw new Error(`Page not found (HTTP 404). Please check your URL and make sure it points to a valid IPO details page.`);
    }
    throw new Error(`The website returned an error: HTTP ${response.status} ${response.statusText}.`);
  }

  const html = await response.text();
  if (!html || html.length < 200) {
    throw new Error('The page returned too little content. It may require JavaScript to render. Try a static IPO details page like Chittorgarh.');
  }

  const $ = cheerio.load(html);

  // Strip scripts, styles, frames, and non-content elements
  $('script, style, iframe, noscript, svg, path, nav, footer, header, aside, [aria-hidden="true"]').remove();

  // Try to get main content first for better signal-to-noise
  const mainContent = $('main, article, .content, #content, .post, .entry, table').text();
  const bodyText = $('body').text();

  const textToUse = mainContent.length > 300 ? mainContent : bodyText;
  return textToUse.replace(/\s+/g, ' ').trim();
}

// AI extraction using OpenRouter
async function extractDataWithAI(rawText, apiKey) {
  const prompt = `
You are an expert IPO analyst. Analyze the following text from an IPO listing page and extract key metrics.
Return ONLY a valid JSON object with exactly these keys: "qib_x", "nii_x", "retail_x", "gmp_pct", "financial_growth", "valuation_status", "sentiment".

Extraction rules:
- qib_x: QIB (Qualified Institutional Buyer) subscription multiple. Look for "QIB" or "Qualified Institutional Buyers" followed by a number like "45.23x" or "45.23 times". Use 0 if not mentioned.
- nii_x: NII (Non-Institutional Investor / HNI) subscription multiple. Look for "NII", "HNI", "Non-Institutional". Use 0 if not found.
- retail_x: Retail individual investor subscription multiple. Look for "Retail" or "RII". Use 0 if not found.
- gmp_pct: Grey Market Premium as a percentage. Look for "GMP", "grey market premium", "premium" followed by a percentage or rupee amount. Convert to % relative to issue price if needed. Use 0 if not found.
- financial_growth: Overall company financial health. Choose "Strong" (profitable, growing revenue), "Moderate" (moderate profit/growth), "Weak" (low profit or stagnant), or "Loss-making" (net loss).
- valuation_status: IPO pricing attractiveness. Choose "Undervalued" (cheap relative to peers), "Fair" (reasonably priced), or "Overpriced" (expensive relative to industry P/E).
- sentiment: Overall analyst/market sentiment toward this IPO. Choose "Bullish", "Neutral", or "Bearish" based on recommendations and tone of the content.

IMPORTANT: Even if some data is missing, always return all 7 keys with your best estimate or 0.

TEXT TO ANALYZE:
${rawText.slice(0, 6000)}
  `;

  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
      "HTTP-Referer": "https://localhost:3000",
      "X-Title": "IPO Analyzer"
    },
    body: JSON.stringify({
      model: "google/gemini-2.5-flash",
      messages: [{ role: "user", content: prompt }],
      response_format: { type: "json_object" },
      max_tokens: 1000
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenRouter API error: ${response.status} - ${errorText}`);
  }

  const result = await response.json();
  const content = result.choices[0].message.content;
  
  // Clean potential markdown blocks surrounding JSON
  const cleanedContent = content.trim().replace(/^```json\s*/i, '').replace(/```$/, '').trim();
  return JSON.parse(cleanedContent);
}

// API endpoint for analyzing IPO links
app.post('/api/analyze', async (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: "URL is required" });
  }

  const apiKey = getApiKey();
  if (!apiKey) {
    return res.status(500).json({ 
      error: "Missing OpenRouter API key. Please add OPENROUTER_API_KEY to your env variables or `.streamlit/secrets.toml`." 
    });
  }

  try {
    console.log(`Starting analysis for URL: ${url}`);
    
    // Step 1: Scrape text
    const rawText = await scrapeUrl(url);
    console.log(`Scraped ${rawText.length} characters of raw text`);

    // Step 2: Use AI to extract metrics
    const parsedData = await extractDataWithAI(rawText, apiKey);
    console.log(`AI extracted data:`, parsedData);

    // Step 3: Run the scoring algorithm
    const analysis = calculateScore(parsedData);
    console.log(`Computed score: ${analysis.total}`);

    res.json({
      success: true,
      url,
      raw_metrics: parsedData,
      score: analysis.total,
      decision: analysis.decision,
      badge: analysis.badge,
      breakdown: analysis.breakdown
    });

  } catch (error) {
    console.error("Analysis failed:", error);
    res.status(500).json({ 
      error: error.message || "An unexpected error occurred during analysis." 
    });
  }
});

app.listen(PORT, () => {
  console.log(`Backend server listening at http://localhost:${PORT}`);
});
