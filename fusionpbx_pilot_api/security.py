from fastapi.security import OAuth2AuthorizationCodeBearer
from fief_client import FiefAsync
from fief_client.integrations.fastapi import FiefAuth

from fusionpbx_pilot_api.settings import config

fief = FiefAsync(config.fief.base_url, config.fief.client_id, config.fief.client_secret)

scheme = OAuth2AuthorizationCodeBearer(
    config.fief.base_url + config.fief.authorize_path,
    config.fief.base_url + config.fief.token_path,
    scopes={'openid': 'openid'},
)

auth = FiefAuth(fief, scheme)
