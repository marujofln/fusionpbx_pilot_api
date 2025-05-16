import os

from dotenv import load_dotenv
from fief_client import Fief

# Load environment variables from .env file
load_dotenv()

FIEF_URL = os.getenv('FIEF_URL')
FIEF_CLIENT_ID = os.getenv('FIEF_CLIENT_ID')
FIEF_CLIENT_SECRET = os.getenv('FIEF_CLIENT_SECRET')

fief = Fief(
    FIEF_URL,
    FIEF_CLIENT_ID,
    FIEF_CLIENT_SECRET,
)

redirect_url = 'http://localhost:8000/callback'

auth_url = fief.auth_url(redirect_url, scope=['openid'])
print(f'Open this URL in your browser: {auth_url}')

code = input('Paste the callback code: ')

tokens, userinfo = fief.auth_callback(code, redirect_url)
print(f'Tokens: {tokens}')
print(f'Userinfo: {userinfo}')
