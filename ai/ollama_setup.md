# Ollama Setup Guide (Windows)

## What is Ollama?
Ollama lets you run AI language models locally on your PC — completely free, no internet needed, no API keys. Your banking data never leaves your machine.

---

## Step 1 — Install Ollama

1. Go to **https://ollama.com/download**
2. Click **Download for Windows**
3. Run the installer (it installs like any normal app)
4. Ollama will appear in your system tray after install

---

## Step 2 — Pull a Model

Open Command Prompt and run one of these (pick based on your RAM):

### Option A — Llama 3.1 8B (recommended, needs 8GB RAM)
```
ollama pull llama3.1:8b
```

### Option B — Phi-3 Mini (lighter, works on 4GB RAM)
```
ollama pull phi3:mini
```

### Option C — Mistral 7B (good balance)
```
ollama pull mistral:7b
```

The download is 4–8 GB. Run it once, stored forever.

---

## Step 3 — Verify Ollama is Running

```
ollama list
```
You should see your downloaded model listed.

Also verify the API is accessible:
```
curl http://localhost:11434/api/tags
```

---

## Step 4 — Start the FraudSense AI Agent

Open a **second** Command Prompt (keep your Node.js server running in the first):

```
cd C:\Users\YourName\Desktop\fundtrace\ai
python agent.py --http
```

You should see:
```
🤖 FraudSense Agent HTTP server running on http://localhost:5002
   POST /analyze  {"task": "...", "entity_code": "FT-...", ...}
   GET  /health
```

Also start the DB tool:
```
python tools\db_tool.py --http
```

---

## Step 5 — Test It

In a third terminal, test the agent:
```
python agent.py --entity-code FT-67GMY9 --pattern circular --verbose
```

Or test the DB tool directly:
```
python tools\db_tool.py "SELECT * FROM users LIMIT 5"
```

---

## Model Comparison

| Model | RAM Needed | Speed | Quality |
|-------|-----------|-------|---------|
| llama3.1:8b | 8 GB | Medium | ★★★★ |
| mistral:7b | 8 GB | Fast | ★★★★ |
| phi3:mini | 4 GB | Fast | ★★★ |
| llama3.1:70b | 40+ GB | Slow | ★★★★★ |

For fraud analysis, `llama3.1:8b` or `mistral:7b` are the best choices for most PCs.

---

## Changing the Model

Edit `ai/core/llm_client.py` line 20:
```python
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
```
Or set environment variable:
```
set OLLAMA_MODEL=mistral:7b
python agent.py --http
```

---

## Using Groq Instead (free cloud, no GPU needed)

1. Get free API key at **https://console.groq.com**
2. Set environment variable:
   ```
   set GROQ_API_KEY=your_key_here
   set FRAUDSENSE_BACKEND=groq
   python agent.py --http
   ```
3. This runs Llama 3 70B on Groq's servers — much more capable than local 8B

---

## Troubleshooting

**"ollama is not recognized"**
→ Restart Command Prompt after installation, or add to PATH manually

**"connection refused" when running agent**
→ Ollama server isn't running. Click the Ollama icon in system tray, or run `ollama serve`

**"model not found"**
→ Run `ollama pull llama3.1:8b` first

**Out of memory**
→ Use `phi3:mini` (smaller model, needs only 4GB RAM)

**Very slow responses**
→ Normal without a GPU. Llama 8B takes ~30-60 seconds per response on CPU.
→ Groq is instant even on free tier — switch to that if speed matters.
