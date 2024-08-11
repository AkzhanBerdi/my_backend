from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TwilioClient:
    def __init__(self):
        try:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.client.incoming_phone_numbers.list(limit=1)
        except TwilioRestException as e:
            logger.error(f"Twilio configuration error: {str(e)}")
            self.client = None

    def create_phone_call(self, to_number, from_number, agent_id):
        if not self.client:
            raise ValueError("Twilio client is not properly configured")
        
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=f"https://{settings.NGROK_IP_ADDRESS}/demo/twilio-voice-webhook/{agent_id}/",
                status_callback='https://{settings.NGROK_IP_ADDRESS}/api/demo/call-status-callback/',
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            return call.sid
        except TwilioRestException as e:
            logger.error(f"Error creating phone call: {str(e)}")
            raise

    def end_call(self, call_sid):
        if not self.client:
            raise ValueError("Twilio client is not properly configured")
        
        try:
            call = self.client.calls(call_sid).update(status='completed')
            return call.status
        except TwilioRestException as e:
            logger.error(f"Error ending call: {str(e)}")
            raise

    def register_phone_agent(self, phone_number, agent_id):
        if not self.client:
            raise ValueError("Twilio client is not properly configured")
        
        try:
            phone_number_objects = self.client.incoming_phone_numbers.list(limit=200)
            number_sid = None
            for phone_number_object in phone_number_objects:
                if phone_number_object.phone_number == phone_number:
                    number_sid = phone_number_object.sid
                    break
            
            if number_sid is None:
                logger.error("Unable to locate this number in your Twilio account. Is the number you used in BCP 47 format?")
                return None
            
            # Fix: Remove the extra 'https://' from the URL
            voice_url = f"https://{settings.NGROK_IP_ADDRESS}/demo/twilio-voice-webhook/{agent_id}"
            if not voice_url.startswith('http'):
                voice_url = f"https://{voice_url}"
            
            phone_number_object = self.client.incoming_phone_numbers(number_sid).update(
                voice_url=voice_url
            )
            
            logger.info(f"Registered phone agent: {vars(phone_number_object)}")
            return phone_number_object
        
        except TwilioRestException as e:
            logger.error(f"Error registering phone agent: {str(e)}")
            raise
        except Exception as err:
            logger.error(f"Unexpected error registering phone agent: {str(err)}")
            raise

twilio_client = TwilioClient()