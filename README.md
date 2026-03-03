# AI-Powered Enterprise Voice Agent & Telephony System

An enterprise-grade AI voice agent built with **Python, Flask, Twilio Voice API, and OpenAI GPT**. The system handles inbound calls using natural speech recognition, detects caller intent using AI, and intelligently routes calls to the correct department — no button pressing required.

---

## Why I Built This

Enterprise support teams were losing time to misrouted calls and outdated IVR systems that forced customers to press digits. I built this to replace the traditional digit-based IVR with a fully conversational AI agent that understands natural speech and routes calls accurately — improving both agent efficiency and customer experience.

---

## Features

- 🎙️ **Natural Speech Input** — callers speak naturally, no digit pressing
- 🤖 **AI Intent Detection** — GPT-3.5 classifies caller intent in real time
- 📞 **Intelligent Call Routing** — routes to Sales, Support, Billing, or General
- 📣 **AI Outbound Calls** — GPT generates personalized outbound call scripts
- 📊 **Call Logging & Analytics** — full audit trail with timestamps and routing data
- 🔁 **Status Webhooks** — real-time call status tracking via Twilio callbacks
- ✅ **Health Check Endpoint** — for production monitoring

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10 | Core application |
| Flask | Webhook server |
| Twilio Voice API | Telephony & call handling |
| TwiML | Call flow scripting |
| OpenAI GPT-3.5 | Intent detection & message generation |
| REST API | Call log retrieval & analytics |

---

## Architecture

```
Inbound Call
     │
     ▼
Twilio ──► /incoming-call
               │
               ▼
         Speech Capture (Twilio STT)
               │
               ▼
         /process-speech
               │
               ▼
         OpenAI GPT Intent Detection
               │
        ┌──────┼──────┬──────────┐
        ▼      ▼      ▼          ▼
      Sales Support Billing   General
```

---

## Project Structure

```
ai-voice-agent/
├── src/
│   └── voice_agent.py        # Core application
├── config/
│   └── .env.example          # Environment variables template
├── docs/
│   └── architecture.md       # Detailed system design
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# Clone repo
git clone https://github.com/yourusername/ai-voice-agent.git
cd ai-voice-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Add your OpenAI and Twilio keys to .env

# Run
python src/voice_agent.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/incoming-call` | POST | Handles inbound call, captures speech |
| `/process-speech` | POST | AI intent detection & routing |
| `/outbound-call` | POST | AI-generated outbound call message |
| `/call-status` | POST | Twilio status callback webhook |
| `/call-logs` | GET | Returns full call log as JSON |
| `/call-logs/summary` | GET | Returns routing summary by department |
| `/health` | GET | Health check |

---

## My Role

I designed and built the entire system — from the telephony call flow architecture using Twilio TwiML, to integrating OpenAI GPT for real-time intent classification, building the Flask webhook handlers, and setting up the call logging and analytics layer.

---

## Biggest Challenge

The hardest part was handling **speech ambiguity** — callers often say vague things like "I need help" which could route anywhere. I solved this by carefully engineering the GPT system prompt to always return a definitive routing decision, with a safe fallback to General Enquiries when confidence was low.

---

## Outcome

- Eliminated digit-based IVR entirely
- Reduced misrouted calls significantly
- Outbound call personalization improved customer response rates
- Full call audit trail available for compliance and analytics
