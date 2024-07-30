from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.twiml.voice_response import VoiceResponse
from llm import LlmClient
from twilio_service import TwilioClient
import json
import asyncio

twilio_client = TwilioClient()

@csrf_exempt
def handle_twilio_voice_webhook(request, agent_id_path):
    try:
        post_data = request.POST
        if 'AnsweredBy' in post_data and post_data['AnsweredBy'] == "machine_start":
            twilio_client.end_call(post_data['CallSid'])
            return HttpResponse("")
        elif 'AnsweredBy' in post_data:
            return HttpResponse("")

        call_response = twilio_client.retell.register_call(agent_id_path)
        if call_response.call_detail:
            response = VoiceResponse()
            start = response.connect()
            start.stream(url=f"wss://api.retellai.com/audio-websocket/{call_response.call_detail.call_id}")
            return HttpResponse(str(response), content_type='text/xml')
    except Exception as err:
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

# WebSocket handling will be done using Django Channels
