from fastapi import APIRouter, Depends
from fief_client import FiefAccessTokenInfo

from fusionpbx_pilot_api.data import fusionpbx
from fusionpbx_pilot_api.security import auth

router_v1 = APIRouter(prefix='/v1', tags=['Extensions'])


@router_v1.get('/domain/{domain}/extensions')
async def extensions_list(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:read'])
    ),
):
    # list extensions
    d = fusionpbx.domain(domain)
    return d.extensions.list()
