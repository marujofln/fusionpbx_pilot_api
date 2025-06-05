from http import HTTPStatus

import requests
from fastapi import APIRouter, Depends, HTTPException
from fief_client import FiefAccessTokenInfo
from fusionpbx_pilot.page_objects.apps.extension import ExtensionNotFound
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound

from fusionpbx_pilot_api.data import (
    get_cached_provisioning,
    get_fusionpbx_provisioning_and_set_cache,
    get_sip_uri,
)
from fusionpbx_pilot_api.schemas import SIPProvisioning
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
        },
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Attributes sip domain or sip user not found on authenticated user.',
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
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
        config.fief.base_url + config.fief.userinfo_path,
        headers={'Authorization': f'Bearer {access_token_info["access_token"]}'},
    )

    userinfo = userinfo.json()

    try:
        domain = userinfo['fields']['pbx_domain']
        extension = userinfo['fields']['pbx_extension']
        transport = userinfo['fields']['pbx_transport']
    except KeyError as error:
        raise HTTPException(
            status_code=HTTPStatus.EXPECTATION_FAILED,
            detail={'message': f"User don't has expected attribute: {error}"},
        )
    cached_provision = get_cached_provisioning(userinfo['sub'])
    if (
        cached_provision
        and cached_provision['pbx_domain'] == domain
        and cached_provision['pbx_extension'] == extension
    ):
        return SIPProvisioning(
            display_name=cached_provision['pbx_display_name'],
            user=cached_provision['pbx_extension'],
            password=cached_provision['pbx_secret'],
            domain=cached_provision['pbx_domain'],
            uri=get_sip_uri(transport, domain),
        )
    else:
        try:
            r = get_fusionpbx_provisioning_and_set_cache(
                userinfo['sub'],
                domain,
                extension,
                transport,
            )
        except DomainNotFound as error:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=str(error),
            )
        except ExtensionNotFound as error:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f'{error} for domain {domain}'
            )
        return r
