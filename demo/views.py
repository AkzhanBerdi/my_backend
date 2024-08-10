from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.twiml.voice_response import VoiceResponse
from .llm import LlmClient
from .twilio_service import TwilioClient
import json
import asyncio
from django.http import HttpResponse, JsonResponse
import os
from twilio.rest import Client
from django.shortcuts import render
import logging
import json
from django.middleware.csrf import get_token

def home_page(request):
    return render(request, 'demo/home.html')


twilio_client = TwilioClient()
twilio_client.register_phone_agent('+1234567890', os.environ['RETELL_AGENT_ID'])#put your phone number
# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def handle_twilio_voice_webhook(request, agent_id_path=os.getenv('RETELL_AGENT_ID')):
    try:
        logger.info("Webhook received")
        post_data = request.POST
        logger.info(f"POST data: {post_data}")

        # Check if the call was answered by a machine
        if 'AnsweredBy' in post_data and post_data['AnsweredBy'] == "machine_start":
            logger.info("Answered by machine, ending call")
            twilio_client.end_call(post_data['CallSid'])
            return HttpResponse("")

        # Check if the call was answered by a person
        elif 'AnsweredBy' in post_data:
            logger.info("Call answered by a person")
            return HttpResponse("")

        # Register the call with retell
        logger.info("Registering call with retell")
        call_response = twilio_client.retell.register_call(agent_id_path)
        logger.info(f"Raw call response: {call_response}")

        # Attempt to parse the response as JSON
        try:
            if isinstance(call_response, str):
                call_response = json.loads(call_response)
            elif isinstance(call_response, bytes):
                call_response = json.loads(call_response.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return JsonResponse({'message': 'Invalid response format from Retell API'}, status=500)

        # Ensure the call_response contains the expected data
        if call_response and 'call_detail' in call_response:
            response = VoiceResponse()
            start = response.connect()
            websocket_url = f"wss://api.retellai.com/audio-websocket/{call_response['call_detail']['call_id']}"
            logger.info(f"Streaming to WebSocket URL: {websocket_url}")
            start.stream(url=websocket_url)

            return HttpResponse(str(response), content_type='text/xml')

        logger.warning("No call_detail found in the response")
        return JsonResponse({'message': 'No call detail found'}, status=400)

    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

# WebSocket handling will be done using Django Channels

@csrf_exempt
def initiate_call(request):
    if request.method == 'GET':
        # Twilio credentials (secure these with environment variables)
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        # Define the call parameters
        to_phone_number = '+1234567890'  # Replace with the destination phone number
        from_phone_number = '+77713974173'  # Replace with your Twilio number
        twiml_url = 'https://d7ec-2a03-32c0-2-23b3-2349-6e1f-28a9-c227.ngrok-free.app/demo/twilio-voice-webhook/'  # TwiML URL for call instructions

        # Initiate the phone call
        call = client.calls.create(
            to=to_phone_number,
            from_=from_phone_number,
            url=twiml_url
        )

        return JsonResponse({'status': 'Call initiated', 'call_sid': call.sid})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def call_myself(request):
    try:
        # Your Twilio call logic here
        twilio_client.create_phone_call(
            "+12298294419",  # Replace with your Twilio number
            "+77713974173",  # Replace with the destination phone number            
            agent_id=os.environ['RETELL_AGENT_ID']
        )
        return JsonResponse({'status': 'Call initiated successfully'})

    except Exception as e:
        # Log the exception (optional)
        logger.error(f"Error in call_myself: {e}")
        return JsonResponse({'error': 'Failed to initiate call'}, status=500)
    

def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})