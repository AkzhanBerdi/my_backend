import json
import logging
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.twiml.voice_response import VoiceResponse
from .twilio_service import twilio_client
from django.middleware.csrf import get_token

logger = logging.getLogger(__name__)

@csrf_exempt
def handle_twilio_voice_webhook(request, agent_id_path=settings.RETELL_AGENT_ID):
    try:
        logger.info("Webhook received")
        post_data = request.POST
        get_data = request.GET
        
        logger.info(f"POST data: {json.dumps(dict(post_data))}")
        logger.info(f"GET data: {json.dumps(dict(get_data))}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {json.dumps(dict(request.headers))}")

        if not post_data and not get_data:
            logger.warning("Received empty webhook data")
            return HttpResponse("Webhook received", status=200)

        if 'CallSid' in post_data and 'CallStatus' in post_data:
            logger.info(f"Call status: {post_data['CallStatus']} for CallSid: {post_data['CallSid']}")

            if post_data['CallStatus'] == 'in-progress':
                logger.info("Call in progress. WebSocket connection should be established.")
                return HttpResponse("In progress", status=200)
            else:
                logger.info(f"Handling call status: {post_data['CallStatus']}")
                # Add any specific handling for other call statuses here
                return HttpResponse("Status received", status=200)
        
        logger.warning(f"Unhandled webhook data: {json.dumps(dict(post_data))}")
        return HttpResponse("Webhook received", status=200)

    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}", exc_info=True)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def initiate_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        to_number = data.get('to_number')
        
        if not to_number:
            return JsonResponse({'error': 'Missing to_number in request'}, status=400)

        from_number = settings.PHONE_NUM_OUT
        agent_id = settings.RETELL_AGENT_ID

        logger.info(f"Initiating call to {to_number} from {from_number}")
       
        retell_response = register_call_with_retell(agent_id, {
            'To': to_number,
            'From': from_number,
        })
        
        if not retell_response or 'call_id' not in retell_response:
            logger.error(f"Failed to register call with Retell: {retell_response}")
            return JsonResponse({'error': 'Failed to register call with Retell'}, status=500)

        retell_call_id = retell_response['call_id']
        
        twiml = VoiceResponse()
        twiml.connect().stream(url=f"wss://api.retellai.com/audio-websocket/{retell_call_id}/")
       
        call = twilio_client.client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=str(twiml)
        )
        
        logger.info(f"Call initiated with SID: {call.sid}")
        logger.info(f"TwiML used: {str(twiml)}")

        return JsonResponse({
            'status': 'Call initiated',
            'call_sid': call.sid,
            'retell_call_id': retell_call_id
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Error in initiate_call: {e}", exc_info=True)
        return JsonResponse({'error': f'Failed to initiate call: {str(e)}'}, status=500)

def register_call_with_retell(agent_id_path, twilio_data):
    try:
        url = "https://api.retellai.com/register-call"
        headers = {
            "Authorization": f"Bearer {settings.RETELL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "agent_id": agent_id_path,
            "audio_websocket_protocol": "twilio",
            "audio_encoding": "mulaw",
            "sample_rate": 8000,
            "customer_number": twilio_data.get('To'),
            "agent_number": twilio_data.get('From')
        }
        
        logger.info(f"Calling Retell API with URL: {url}")
        logger.info(f"Headers: {json.dumps(headers)}")
        logger.info(f"Data: {json.dumps(data)}")
        
        response = requests.post(url, headers=headers, json=data)
        
        logger.info(f"Retell API Status Code: {response.status_code}")
        logger.info(f"Retell API Response: {response.text}")
        
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling Retell API: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from Retell API: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in register_call_with_retell: {str(e)}", exc_info=True)
        return None

def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})

@csrf_exempt
def call_status_callback(request):
    status = request.POST.get('CallStatus')
    call_sid = request.POST.get('CallSid')
    call_duration = request.POST.get('CallDuration')
    error_code = request.POST.get('ErrorCode')
    error_message = request.POST.get('ErrorMessage')
    logger.info(f"Call {call_sid} status update: {status}, Duration: {call_duration}")
    if error_code or error_message:
        logger.error(f"Call error: Code {error_code}, Message: {error_message}")
    logger.debug(f"Full callback data: {request.POST}")
    return HttpResponse(status=200)