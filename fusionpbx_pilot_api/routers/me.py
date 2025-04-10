from fastapi import APIRouter, Depends
from fief_client import FiefAccessTokenInfo

from fusionpbx_pilot_api.security import auth

router_v1 = APIRouter(prefix='/v1', tags=['User'])


@router_v1.get('/me')
async def get_me(
    access_token_info: FiefAccessTokenInfo = Depends(auth.authenticated()),
):
    return access_token_info
