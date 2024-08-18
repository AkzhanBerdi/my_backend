from django.db import models

class RetellAgent(models.Model):
    name = models.CharField(max_length=100)
    accent = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    speech_style = models.CharField(max_length=50)
    retell_agent_id = models.CharField(max_length=100, unique=True)