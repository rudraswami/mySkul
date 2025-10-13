"""
Direct Google OAuth integration
"""
import os
from authlib.integrations.starlette_client import OAuth

# Initialize OAuth
oauth = OAuth()

# Get credentials from environment
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

if not google_client_id or not google_client_secret:
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")

print(f"🔐 Google OAuth initialized with client_id: {google_client_id[:20]}...")

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=google_client_id,
    client_secret=google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

