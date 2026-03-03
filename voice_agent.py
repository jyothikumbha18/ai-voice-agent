"""
AI-Powered Enterprise Voice Agent
- Twilio for telephony (inbound/outbound calls)
- OpenAI Whisper for speech-to-text transcription
- OpenAI GPT for natural language understanding & intent detection
- Intelligent call routing based on AI-detected intent
- Full call logging and analytics
"""

from flask import Flask, request, Response, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial
from openai import OpenAI
import logging
import json
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

call_logs = []

DEPARTMENT_ROUTING = {
    "sales":     {"number": "+15550001111", "label": "Sales"},
    "support":   {"number": "+15550002222", "label": "Technical Support"},
    "billing":   {"number": "+15550003333", "label": "Billing"},
    "general":   {"number": "+15550004444", "label": "General Enquiries"},
}


# ─────────────────────────────────────────────
# INBOUND CALL — Greet & Capture Speech
# ─────────────────────────────────────────────
@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    call_sid = request.form.get("CallSid")
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speechTimeout="auto",
        language="en-US"
    )
    gather.say(
        "Hello, welcome to Enterprise Support. "
        "Please tell me how I can help you today.",
        voice="alice"
    )
    response.append(gather)
    response.say("Sorry, I didn't catch that. Please call back and try again.")

    log_call(call_sid, "inbound", "greeted")
    return Response(str(response), mimetype="text/xml")


# ─────────────────────────────────────────────
# PROCESS SPEECH — Transcribe & Detect Intent
# ─────────────────────────────────────────────
@app.route("/process-speech", methods=["POST"])
def process_speech():
    call_sid = request.form.get("CallSid")
    speech_result = request.form.get("SpeechResult", "")
    response = VoiceResponse()

    logging.info(f"[{call_sid}] Speech: {speech_result}")

    if not speech_result:
        response.say("I couldn't hear you clearly. Let me transfer you to our team.")
        response.dial(DEPARTMENT_ROUTING["general"]["number"])
        return Response(str(response), mimetype="text/xml")

    intent = detect_intent(speech_result)
    department = DEPARTMENT_ROUTING.get(intent, DEPARTMENT_ROUTING["general"])

    response.say(
        f"Got it. I'm connecting you to our {department['label']} team now. Please hold.",
        voice="alice"
    )
    response.dial(department["number"])

    log_call(call_sid, "routed", department["label"], extra={"speech": speech_result, "intent": intent})
    return Response(str(response), mimetype="text/xml")


# ─────────────────────────────────────────────
# AI INTENT DETECTION using GPT
# ─────────────────────────────────────────────
def detect_intent(speech_text: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an enterprise call center router. "
                        "Based on the caller's message, return ONLY one word: "
                        "sales, support, billing, or general. "
                        "No explanation, just the single word."
                    )
                },
                {"role": "user", "content": speech_text}
            ],
            max_tokens=5,
            temperature=0
        )
        intent = completion.choices[0].message.content.strip().lower()
        if intent not in DEPARTMENT_ROUTING:
            intent = "general"
        logging.info(f"Detected intent: {intent}")
        return intent
    except Exception as e:
        logging.error(f"Intent detection failed: {e}")
        return "general"


# ─────────────────────────────────────────────
# OUTBOUND CALL — AI Generated Message
# ─────────────────────────────────────────────
@app.route("/outbound-call", methods=["POST"])
def outbound_call():
    call_sid = request.form.get("CallSid")
    customer_name = request.form.get("customer_name", "Valued Customer")
    reason = request.form.get("reason", "follow-up")

    message = generate_outbound_message(customer_name, reason)

    response = VoiceResponse()
    response.say(message, voice="alice")

    log_call(call_sid, "outbound", reason, extra={"message": message})
    return Response(str(response), mimetype="text/xml")


def generate_outbound_message(name: str, reason: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional enterprise voice agent. Generate a short, friendly outbound call message under 40 words."
                },
                {
                    "role": "user",
                    "content": f"Customer name: {name}. Reason for call: {reason}."
                }
            ],
            max_tokens=60,
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Message generation failed: {e}")
        return f"Hello {name}, this is a call from Enterprise Support regarding your {reason}. Please call us back."


# ─────────────────────────────────────────────
# CALL STATUS WEBHOOK
# ─────────────────────────────────────────────
@app.route("/call-status", methods=["POST"])
def call_status():
    call_sid = request.form.get("CallSid")
    status = request.form.get("CallStatus")
    duration = request.form.get("CallDuration", 0)
    log_call(call_sid, "status_update", status, duration=duration)
    logging.info(f"[{call_sid}] Status: {status} | Duration: {duration}s")
    return "", 204


# ─────────────────────────────────────────────
# CALL LOGS API
# ─────────────────────────────────────────────
@app.route("/call-logs", methods=["GET"])
def get_call_logs():
    return jsonify(call_logs), 200


@app.route("/call-logs/summary", methods=["GET"])
def get_summary():
    summary = {}
    for log in call_logs:
        dept = log.get("detail", "unknown")
        summary[dept] = summary.get(dept, 0) + 1
    return jsonify(summary), 200


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def log_call(call_sid, event_type, detail, duration=None, extra=None):
    entry = {
        "call_sid": call_sid,
        "event_type": event_type,
        "detail": detail,
        "duration": duration,
        "extra": extra or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    call_logs.append(entry)
    logging.info(f"Log: {json.dumps(entry)}")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
