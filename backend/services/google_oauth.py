"""
Direct Google OAuth integration
"""
import os
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Load config
config = Config(os.path.join(os.path.dirname(__file__), '../.env'))

# Initialize OAuth
oauth = OAuth(config)

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'  # Always show account selection
    }
)
