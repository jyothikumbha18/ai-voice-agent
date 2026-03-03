# System Architecture

## Overview
The AI Voice Agent acts as intelligent middleware between Twilio's telephony infrastructure and internal department lines. All call events are handled via webhooks processed by Flask, with OpenAI GPT handling real-time intent classification.

## Call Flow (Inbound)
1. Customer calls the enterprise Twilio number
2. Twilio fires POST to `/incoming-call`
3. Flask responds with TwiML to capture speech
4. Twilio transcribes speech and fires POST to `/process-speech`
5. Flask sends transcribed text to OpenAI GPT for intent detection
6. GPT returns intent: sales / support / billing / general
7. Flask returns TwiML to dial the appropriate department
8. Status callbacks update call logs throughout

## Call Flow (Outbound)
1. Internal trigger fires POST to `/outbound-call` with customer name and reason
2. GPT generates a personalized message
3. Twilio reads the message to the customer via TTS

## Scalability Notes
- Stateless handlers allow horizontal scaling behind a load balancer
- Call logs can be migrated to PostgreSQL or Azure SQL for production
- GPT calls are async-friendly — can be moved to a queue for high volume
- Twilio handles all SIP/PSTN infrastructure
