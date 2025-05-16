from http import HTTPStatus

import requests
from fastapi import APIRouter, Depends, HTTPException
from fief_client import FiefAccessTokenInfo
from fusionpbx_pilot.page_objects.apps.extension import ExtensionNotFound
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound

from fusionpbx_pilot_api.data import (
    get_cached_provisioning,
    get_fusionpbx_provisioning_and_set_cache,
)
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
def provisioning(
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read', 'pbx:extension:read'])
    ),
):
    # get user info from auth api
    userinfo = requests.get(
        config.fief_base_url + '/api/userinfo',
        headers={'Authorization': f'Bearer {access_token_info["access_token"]}'},
    )

    userinfo = userinfo.json()

    try:
        domain = userinfo['fields']['pbx_domain']
        extension = userinfo['fields']['pbx_extension']
    except KeyError as error:
        msg = DetailMessage(
            f"User don't has domain or extensions attrs. Error: {error}"
        )
        raise HTTPException(
            status_code=HTTPStatus.EXPECTATION_FAILED,
            detail=msg,
        )
    cp = get_cached_provisioning(userinfo['sub'])
    if cp and cp['pbx_domain'] == domain and cp['pbx_extension'] == extension:
        return SIPProvisioning(
            user=cp['pbx_extension'],
            password=cp['pbx_secret'],
            domain=cp['pbx_domain'],
        )
    else:
        try:
            r = get_fusionpbx_provisioning_and_set_cache(
                userinfo['sub'],
                domain,
                extension,
            )
        except DomainNotFound as error:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=DetailMessage(str(error)),
            )
        except ExtensionNotFound as error:
            msg = DetailMessage(f'{error} for domain {domain}')
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=msg)
        return r
