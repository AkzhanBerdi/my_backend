import environ

env = environ.Env()
environ.Env.read_env()

# Secret key and other settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Twilio and OpenAI configurations
TWILIO_ACCOUNT_ID = env('TWILIO_ACCOUNT_ID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
OPENAI_ORGANIZATION_ID = env('OPENAI_ORGANIZATION_ID')
OPENAI_API_KEY = env('OPENAI_API_KEY')
RETELL_API_KEY = env('RETELL_API_KEY')
NGROK_IP_ADDRESS = env('NGROK_IP_ADDRESS')

ASGI_APPLICATION = 'demo.asgi.application'

# channels settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

INSTALLED_APPS = [
    'channels',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # This can be empty or include additional directories
        'APP_DIRS': True,  # This should be True
        'OPTIONS': {
            'context_processors': [
                ...
            ],
        },
    },
]