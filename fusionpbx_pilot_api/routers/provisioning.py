import requests
from fastapi import APIRouter, Depends
from fief_client import FiefAccessTokenInfo

from fusionpbx_pilot_api.data import fusionpbx
from fusionpbx_pilot_api.security import auth
from fusionpbx_pilot_api.settings import config

router_v1 = APIRouter(prefix='/v1', tags=['Provisioning'])


@router_v1.get('/provisioning')
async def provisioning(
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read', 'pbx:extension:read'])
    ),
):
    # get user info from auth api
    userinfo = requests.get(
        config.fief_base_url + '/api/userinfo',
        headers={'Authorization': f'Bearer {access_token_info["access_token"]}'},
    )
    try:
        userinfo.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return {
            'error': 'Unable to get user info from auth api',
            'message': str(e),
        }
    try:
        domain = userinfo.json()['fields']['pbx_domain']
        extension = userinfo.json()['fields']['pbx_extension']
    except KeyError as e:
        return {
            'error': 'Unable to get domain or extension from user info',
            'message': str(e),
        }

    d = fusionpbx.domain(domain)
    e = d.extension(extension)

    return {
        'domain': d.name,
        'extension': e.name,
        'password': e.password,
    }
