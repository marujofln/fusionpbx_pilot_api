from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fief_client import FiefAccessTokenInfo
from fusionpbx_pilot.page_objects.apps.extension import ExtensionNotFound
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound

from fusionpbx_pilot_api.data import get_fusionpbx
from fusionpbx_pilot_api.schemas import Extension as ExtensionSchema
from fusionpbx_pilot_api.security import auth

router_v1 = APIRouter(prefix='/v1', tags=['Extensions'])


@router_v1.get(
    '/domain/{domain}/extensions',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain found on fusionpbx',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
    },
)
def extensions_list(
    domain: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:read'])
    ),
) -> list:
    # list extensions
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
    except DomainNotFound as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))
    return d.extensions.list()


@router_v1.get(
    '/domain/{domain}/extension/{extension}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
    },
)
def extension_get(
    domain: str,
    extension: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:read'])
    ),
):
    # get extension
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)
        return e.__dict__()
    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))


@router_v1.put(
    '/domain/{domain}/extension/{extension}',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Domain not created.',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def extension_create(
    domain: str,
    extension: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # create extension
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
    except DomainNotFound as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))

    e = d.extension(extension, create=True)
    if e.name == extension:
        return e.__dict__()
    else:
        raise HTTPException(
            HTTPStatus.EXPECTATION_FAILED, detail='Extension not created'
        )


@router_v1.patch(
    '/domain/{domain}/extension/{extension}/name/{new_name}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Extension not updated',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def extension_rename(
    domain: str,
    extension: str,
    new_name: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # rename extension
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)
        e.name = new_name
    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))
    if e.name == new_name:
        return e.__dict__()
    else:
        raise HTTPException(
            HTTPStatus.EXPECTATION_FAILED, detail='Extension not renamed'
        )


@router_v1.delete(
    '/domain/{domain}/extension/{extension}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Extension not deleted',
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def extension_delete(
    domain: str,
    extension: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # delete extension
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)
    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(
            status_code=HTTPStatus.EXPECTATION_FAILED, detail=str(error)
        )
    del e.name
    return {'detail': 'Extension deleted'}


@router_v1.put(
    '/domain/{domain}/extension/{extension}/voicemail',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Unable to update voicemail setting',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def extension_voicemail_enable_toggle(
    domain: str,
    extension: str,
    voicemail_enabled: bool,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # enable/disable voicemail
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)

    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))
    e.voicemail_enabled = voicemail_enabled
    if e.voicemail_enabled == voicemail_enabled:
        return e.__dict__()
    else:
        raise HTTPException(
            HTTPStatus.EXPECTATION_FAILED, detail='Unable to update voicemail setting'
        )


@router_v1.put(
    '/domain/{domain}/extension/{extension}/voicemail/mail_to/{mail_to}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Unable to update voicemail setting',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def set_extension_voicemail_mail_to(
    domain: str,
    extension: str,
    mail_to: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # set voicemail mail to
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)
    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))

    e.voicemail_mail_to = mail_to
    if e.voicemail_mail_to == mail_to:
        return e.__dict__()
    else:
        raise HTTPException(
            HTTPStatus.EXPECTATION_FAILED, detail='Unable to update voicemail setting'
        )


@router_v1.patch(
    '/domain/{domain}/extension/{extension}/password/{new_password}',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.EXPECTATION_FAILED: {
            'description': 'Extension not updated',
        },
        HTTPStatus.OK: {
            'description': 'Returns the extension',
            'model': ExtensionSchema,
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Domain or extension not found on fusionpbx',
        },
    },
)
def set_extension_password(
    domain: str,
    extension: str,
    new_password: str,
    access_token_info: FiefAccessTokenInfo = Depends(
        auth.authenticated(permissions=['pbx:extension:write'])
    ),
):
    # set extension password
    fusionpbx = get_fusionpbx()
    try:
        d = fusionpbx.domain(domain)
        e = d.extension(extension)
    except (ExtensionNotFound, DomainNotFound) as error:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(error))

    e.password = new_password

    if e.password == new_password:
        return e.__dict__()
    else:
        raise HTTPException(
            HTTPStatus.EXPECTATION_FAILED, detail='Extension not updated'
        )
