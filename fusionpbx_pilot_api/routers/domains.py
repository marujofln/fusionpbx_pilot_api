from fastapi import APIRouter, Depends
from fief_client import FiefAccessTokenInfo

from fusionpbx_pilot_api.data import fusionpbx
from fusionpbx_pilot_api.security import auth

router_v1 = APIRouter(prefix='/v1', tags=['Domains'])


@router_v1.get('/domains')
async def domains_list(
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read'])
    ),
):
    return fusionpbx.domains.list()


@router_v1.put('/domain/{domain}')
async def domain_create(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read'])
    ),
):
    d = fusionpbx.domain.name = domain
    return d


# @router_v1.patch('/domain/{domain}/name/{new_name}')
# async def domain_rename(
#     domain: str,
#     new_name: str,
#     access_token_info: FiefAccessTokenInfo = Depends(
#         auth.authenticated(permissions=['pbx:domain:write'])
#     ),
# ):
#     # rename domain
#     d = fusionpbx.domain(domain)
#     d.name = new_name
#     return d


@router_v1.delete('/v1/domain/{domain}')
async def domain_delete(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:write'])
    ),
):
    # delete domain
    d = fusionpbx.domain(domain)
    del d.name
    return d.name
