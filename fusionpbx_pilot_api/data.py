import json

import redis
from fusionpbx_pilot.page_objects import FusionPBX
from fusionpbx_pilot.page_objects.apps.extension import ExtensionNotFound
from fusionpbx_pilot.page_objects.core.domain import DomainNotFound
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from fusionpbx_pilot_api.schemas import SIPProvisioning
from fusionpbx_pilot_api.settings import config

options = Options()

if config.selenium.headless:
    options.add_argument('--headless')  # Run in headless mode


if config.redis.username and config.redis.password:
    redis = redis.Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        username=config.redis.username,
        password=config.redis.password,
    )
else:
    redis = redis.StrictRedis(
        host=config.redis.host, port=config.redis.port, db=config.redis.db
    )


def get_sip_uri(transport: str, domain: str) -> str:
    """
    Get the SIP URI based on the transport and domain.
    """
    if transport == 'wss':
        return f'wss://{domain}:{config.fusionpbx.wss_port}'
    elif transport == 'udp':
        return f'sip://{domain}:{config.fusionpbx.udp_port};transport=udp'
    elif transport == 'tcp':
        return f'sip:{domain}:{config.fusionpbx.tcp_port};transport=tcp'
    elif transport == 'tls':
        return f'sips:{domain}:{config.fusionpbx.tls_port};transport=tls'
    else:
        raise ValueError(f'Unsupported transport: {transport}')


def get_fusionpbx():
    driver = webdriver.Remote(
        command_executor=config.selenium.grid_url,
        options=options,
    )

    fpbx = FusionPBX(
        driver,
        config.fusionpbx.url,
        config.fusionpbx.user,
        config.fusionpbx.password,
    )
    return fpbx


def get_cached_provisioning(user_id: str):
    cached_data = redis.get(user_id)
    if cached_data:
        return json.loads(cached_data.decode('utf-8'))
    else:
        return None


def set_cached_provisioning(user_id: str, data: dict):
    redis.set(user_id, json.dumps(data))
    return


def delete_cached_provisioning(user_id: str):
    redis.delete(user_id)
    return


def get_fusionpbx_provisioning_and_set_cache(
    user_id: str, domain: str, extension: str, transport: str
) -> SIPProvisioning | ExtensionNotFound | DomainNotFound:
    """Retrieves FusionPBX provisioning details for a given user, domain, and extension,
    sets the data in the cache, and returns the SIP provisioning information.
    Args:
        user_id (str): The ID of the user requesting the provisioning details.
        domain (str): The domain name associated with the FusionPBX instance.
        extension (str): The extension number to retrieve provisioning details for.
    Returns:
        SIPProvisioning: An object containing the SIP provisioning details (user, password, domain).
        ExtensionNotFound: Raised if the specified extension does not exist.
        DomainNotFound: Raised if the specified domain does not exist.
    Side Effects:
        - Sets the retrieved provisioning details in the cache for the given user ID.
        - Closes the browser session used to interact with FusionPBX.
    Raises:
        ExtensionNotFound: If the specified extension is not found in the domain.
        DomainNotFound: If the specified domain is not found in FusionPBX.
    user_id, domain, extension
    """
    pbx = get_fusionpbx()
    d = pbx.domain(domain)
    e = d.extension(extension)
    r = SIPProvisioning(
        display_name='Display Name',
        user=e.name,
        password=e.password,
        domain=d.name,
        uri=get_sip_uri(transport, domain),
    )
    # set cached data
    set_cached_provisioning(
        user_id,
        {
            'pbx_domain': d.name,
            'pbx_extension': e.name,
            'pbx_secret': e.password,
            'pbx_display_name': 'Display Name',
        },
    )
    pbx.browser.quit()

    return r
