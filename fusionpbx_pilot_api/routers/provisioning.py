from http import HTTPStatus

import requests
from fastapi import APIRouter, Depends, HTTPException
from fief_client import FiefAccessTokenInfo
from fusionpbx_pilot.page_objects.apps.extension import ExtensionNotFound
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound

from fusionpbx_pilot_api.data import fusionpbx
from fusionpbx_pilot_api.schemas import DetailMessage, SIPProvisioning
from fusionpbx_pilot_api.security import auth
from fusionpbx_pilot_api.settings import config

router_v1 = APIRouter(prefix='/v1', tags=['Provisioning'])


@router_v1.get(
    '/provisioning',
    status_code=HTTPStatus.OK,
    response_model=SIPProvisioning,
    responses={
        HTTPStatus.UNAUTHORIZED: {
            'description': 'Unauthorized',
            'model': DetailMessage,
        },
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Attributes sip domain or sip user not found on authenticated user.',
            'model': DetailMessage,
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
            'model': DetailMessage,
        },
    },
    summary='Get SIP provisioning data',
    description='Get SIP provisioning data for the authenticated user',
)
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
        domain = userinfo.json()['fields']['pbx_domain']
        extension = userinfo.json()['fields']['pbx_extension']
    except KeyError as error:
        msg = DetailMessage(
            f"User don't has domain or extensions attrs. Error: {error}"
        )
        raise HTTPException(
            status_code=HTTPStatus.EXPECTATION_FAILED,
            detail=msg,
        )

    try:
        d = fusionpbx.domain(domain)
        error = d.extension(extension)
    except DomainNotFound as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=DetailMessage(str(error)),
        )
    except ExtensionNotFound as error:
        msg = DetailMessage(f'{error} for domain {domain}')
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=msg)
    return SIPProvisioning(user=error.name, password=error.password, domain=d.name)
