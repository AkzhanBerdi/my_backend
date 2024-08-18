from rest_framework import serializers
from .models import RetellAgent

class RetellAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetellAgent
        fields = ['id', 'name', 'accent', 'gender', 'speech_style', 'retell_agent_id']
        read_only_fields = ['id', 'retell_agent_id']