from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fief_client import FiefAccessTokenInfo
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound

from fusionpbx_pilot_api.data import get_fusionpbx
from fusionpbx_pilot_api.schemas import DetailMessage as DetailMessageSchema
from fusionpbx_pilot_api.schemas import Domain as DomainSchema
from fusionpbx_pilot_api.security import auth

router_v1 = APIRouter(prefix='/v1', tags=['Domains'])


@router_v1.get('/domains', status_code=HTTPStatus.OK, response_model=list)
def domains_list(
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read'])
    ),
):
    fusionpbx = get_fusionpbx()
    return fusionpbx.domains.list()


@router_v1.get(
    '/domain/{domain}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {'description': 'Domain found', 'model': DomainSchema},
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
            'model': DetailMessageSchema,
        },
    },
)
def domain_get(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:read'])
    ),
):
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        return d.__dict__()

    except DomainNotFound as error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=error,
        )


@router_v1.put(
    '/domain/{domain}',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.OK: {'description': 'Domain created', 'model': DomainSchema},
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Domain not created',
            'model': DetailMessageSchema,
        },
    },
)
def domain_create(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:write'])
    ),
) -> bool:
    fusionpbx = get_fusionpbx()
    d = fusionpbx.domain(domain, create=True)
    if d.name == domain:
        return d.__dict__()
    else:
        raise HTTPException(HTTPStatus.EXPECTATION_FAILED, detail='Domain not created')


@router_v1.patch(
    '/domain/{domain}/name/{new_name}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {'description': 'Domain renamed', 'model': DomainSchema},
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Domain not renamed',
            'model': DetailMessageSchema,
        },
    },
)
def domain_rename(
    domain: str,
    new_name: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:write'])
    ),
) -> bool:
    fusionpbx = get_fusionpbx()
    # rename domain
    d = fusionpbx.domain(domain)
    d.name = new_name
    if d.name == new_name:
        return d.__dict__()
    else:
        return HTTPException(
            HTTPStatus.EXPECTATION_FAILED,
            detail='Fail on rename domain',
        )


@router_v1.delete('/v1/domain/{domain}', status_code=HTTPStatus.OK)
async def domain_delete(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:domain:write'])
    ),
):
    fusionpbx = get_fusionpbx()
    # delete domain
    d = fusionpbx.domain(domain)
    del d.name
    return d.name
