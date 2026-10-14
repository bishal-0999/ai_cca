# 🌍 EcoAwareness AI

**An AI-powered Environmental Awareness Poster Generator**

> Built with Python, Streamlit, and Google Gemini AI.
> Perfect for college projects and beginners learning Python + AI!

---

## 📸 What This App Does

1. You type an environmental topic (e.g., **"Save Trees"**)
2. You pick a language (English, Hindi, or Kannada)
3. You click **"Generate Content"**
4. The AI creates a **headline, message, 3 tips, and a slogan**
5. The app draws a **beautiful green poster** with all the content
6. You **download the poster** as a PNG image

---

## 📁 Project File Structure

```
evs mini/
│
├── app.py                <- Main app (UI + logic — start here!)
├── content_generator.py  <- Calls Gemini AI to get awareness content
├── poster_creator.py     <- Draws the poster image using Pillow
├── requirements.txt      <- List of Python libraries to install
├── .env                  <- Your secret API key (never share this!)
├── .gitignore            <- Tells Git which files to ignore
└── README.md             <- This file
```

### What each file does:

| File | What it does |
|------|-------------|
| `app.py` | The brain of the app. Sets up the page, handles button clicks, and calls the other two modules |
| `content_generator.py` | Sends the topic + language to Gemini AI and gets back JSON with the awareness content |
| `poster_creator.py` | Uses Pillow to draw a green poster with the content — like a digital art canvas |
| `requirements.txt` | A shopping list of Python packages the app needs |
| `.env` | A secret file that holds your Gemini API key |

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Make Sure Python is Installed

Open your **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and type:

```bash
python --version
```

You should see something like `Python 3.10.0`. If not, download Python from https://python.org.

---

### Step 2: Navigate to the Project Folder

```bash
cd "/Users/bishalbaroi/Desktop/evs mini"
```

---

### Step 3: Create a Virtual Environment (Recommended)

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal prompt.

---

### Step 4: Install Required Libraries

```bash
pip install -r requirements.txt
```

This installs all 4 libraries: Streamlit, google-generativeai, Pillow, and python-dotenv.

---

### Step 5: Get Your Free Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (it looks like: AIzaSy...)

---

### Step 6: Add Your API Key to the .env File

Open the `.env` file and replace `your_gemini_api_key_here` with your actual key:

```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
```

Save the file. Never share this file or upload it to GitHub!

---

### Step 7: Run the App!

```bash
streamlit run app.py
```

Your browser will automatically open at http://localhost:8501

---

## 🎯 How to Use the App

1. Type an environmental topic in the text box (or click a quick example)
2. Select your language from the dropdown
3. Click "Generate Awareness Content"
4. Wait a few seconds for the AI to respond
5. Read the headline, message, tips, and slogan
6. View the generated poster below
7. Click "Download Poster as Image" to save it

---

## 🔧 Troubleshooting

**"API Key Missing" error**
-> Make sure your .env file has GEMINI_API_KEY=your_actual_key
-> Make sure the .env file is in the same folder as app.py

**"Content Generation Failed" error**
-> Check your internet connection
-> Make sure your Gemini API key is valid and not expired
-> Try again (AI services occasionally have temporary issues)

**ModuleNotFoundError when running**
-> Make sure you installed libraries: pip install -r requirements.txt
-> Make sure your virtual environment is active (you see (venv) in terminal)

**Port already in use**
-> Run on a different port: streamlit run app.py --server.port 8502

---

## 📚 Libraries Used (and Why)

| Library | Purpose | Why we use it |
|---------|---------|---------------|
| Streamlit | Web UI framework | Lets us build a full web app with just Python - no HTML/JS needed! |
| google-generativeai | Gemini AI SDK | The official library to talk to Google's Gemini AI |
| Pillow (PIL) | Image creation | Lets us draw shapes, text, and colors to create the poster |
| python-dotenv | Load .env file | Safely reads our API key from the .env file |

---

## 💡 How the Code Works (Beginner Explanation)

### app.py — The Main Controller
Think of this like the manager of the app. It:
- Sets up the visual design (colors, fonts, layout)
- Shows the input fields to the user
- Calls content_generator.py when the button is clicked
- Calls poster_creator.py to make the poster
- Shows everything to the user

### content_generator.py — The AI Communicator
Think of this as the translator between your app and the AI:
1. Takes the topic + language
2. Writes a detailed prompt (instruction) for the AI
3. Sends it to Gemini and waits for the reply
4. The reply comes back as JSON (a structured data format)
5. Cleans and returns the data

### poster_creator.py — The Digital Artist
Think of this as a painter who:
1. Creates a blank canvas (800x1100 pixels)
2. Paints a green gradient background
3. Draws decorative circles and leaf shapes
4. Writes the headline, message, and slogan in styled text boxes
5. Adds a banner, badges, and footer
6. Returns the finished image

---

## 🌐 Language Support

The app supports content generation in 3 languages:
- English (default)
- Hindi (widely spoken in India)
- Kannada (official language of Karnataka)

Note: The poster text will be in the selected language. Some fonts may not render certain Kannada or Hindi characters correctly on older systems — if characters appear as boxes, this is a font support issue on your OS.

---

*Made with love for a greener planet*
