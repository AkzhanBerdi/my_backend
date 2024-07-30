import json
from channels.generic.websocket import AsyncWebsocketConsumer
from llm import LlmClient

class LlmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.call_id = self.scope['url_route']['kwargs']['call_id']
        self.llm_client = LlmClient()  # Define llm_client as an instance variable
        await self.accept()

        response_id = 0
        first_event = self.llm_client.draft_begin_messsage()
        await self.send(text_data=json.dumps(first_event))

    async def receive(self, text_data):
        request = json.loads(text_data)
        response_id = request.get('response_id', 0)

        if 'response_id' in request:
            async for event in self.llm_client.draft_response(request):
                await self.send(text_data=json.dumps(event))

    async def disconnect(self, close_code):
        print(f"LLM WebSocket disconnected for {self.call_id}")
