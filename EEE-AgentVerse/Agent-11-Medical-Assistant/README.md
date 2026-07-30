# 💊 AI Medical Prescription Assistant

> **Agent-11 · ElderCare AI · AgentVerse Hackathon**
> Production-ready · 100% Local · No API Keys · No Quota Limits

---

## 🏗️ Architecture

```
app.py  ←  ui/pages/  ←  agents/  ←  ai/ + ocr/ + translation/ + voice/
                                  ↓
                             database/ (SQLite + SQLAlchemy)
```

---

## ⚡ Quick Start

### 1. Install Ollama and pull models
```bash
# Install Ollama: https://ollama.com
ollama pull qwen3          # Primary model
ollama pull deepseek-r1    # Fallback 1
ollama pull llama3.1       # Fallback 2
```

### 2. Install Tesseract OCR (optional but recommended)
```bash
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# macOS:   brew install tesseract
# Linux:   sudo apt install tesseract-ocr
```

### 3. Install Python dependencies
```bash
cd Agent-11-Medical-Assistant
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

---

## 🤖 AI Models (All Local — No API Keys)

| Priority | Model       | Purpose                    |
|----------|-------------|----------------------------|
| Primary  | Qwen3       | Prescription extraction, Q&A |
| Fallback | DeepSeek-R1 | Auto-switch on failure     |
| Fallback | Llama 3.1   | Second auto-switch         |

The LLM Router automatically switches models if one fails.

---

## 🔍 OCR Pipeline

```
Image → Preprocess → EasyOCR → confidence ≥ 0.65? → Done
                              ↓ No
                    Enhanced Preprocess → EasyOCR retry
                              ↓ Still low
                         Tesseract fallback
                              ↓ Still low
                    Ask user for clearer image
```

---

## 🗄️ Database Tables

| Table                | Purpose                        |
|----------------------|--------------------------------|
| users                | Authentication + profile       |
| prescriptions        | OCR + AI extracted data        |
| medicines            | Per-medicine details           |
| reminders            | Scheduled dose reminders       |
| reminder_logs        | Taken/missed/snoozed history   |
| appointments         | Booked doctor appointments     |
| conversation_history | Multi-turn chat memory         |

---

## 🌍 Supported Languages

English, Tamil, Hindi, Telugu, Malayalam, Kannada, Marathi, Bengali,
Gujarati, Punjabi, Urdu, French, German, Spanish, Arabic, Chinese,
Japanese, Korean, Portuguese, Russian — and all NLLB-200 languages.

---

## 📁 Project Structure

```
Agent-11-Medical-Assistant/
├── app.py              # Streamlit entry point
├── config.py           # All constants
├── requirements.txt
├── database/           # SQLAlchemy ORM + repository
├── agents/             # PrescriptionAgent, AppointmentAgent, etc.
├── ai/                 # LLM router + Ollama client + prompts
├── ocr/                # EasyOCR + Tesseract + pipeline
├── translation/        # NLLB-200 + language detection
├── voice/              # Whisper STT + Coqui TTS
├── reminder/           # APScheduler + reminder service
├── appointment/        # Doctor registry + booking service
├── utils/              # Logger, validators, schemas, error handler
└── ui/                 # Streamlit pages + theme + components
```

---

## 🏆 Hackathon Highlights

- ✅ 100% local — no paid APIs, no quota limits
- ✅ Auto-switching AI (Qwen3 → DeepSeek → Llama)
- ✅ Handwritten prescription OCR
- ✅ Multi-language support (20+ languages)
- ✅ Voice input (Whisper) + Voice output (Coqui TTS)
- ✅ Smart medicine reminders with APScheduler
- ✅ FSM-based appointment booking agent
- ✅ SQLite persistence with SQLAlchemy ORM
- ✅ SOLID architecture, Pydantic validation, structured logging
- ✅ Never crashes — safe_execute decorator on all critical paths
