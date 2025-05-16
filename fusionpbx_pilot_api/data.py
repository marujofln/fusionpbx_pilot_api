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
options.add_argument('--headless')  # Run in headless mode

if config.redis_username and config.redispassword:
    redis = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=0,
        username=config.redis.username,
        password=config.redis.password,
    )
else:
    redis = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=0)


def get_fusionpbx():
    driver = webdriver.Remote(
        command_executor=config.selenium_grid_url,
        options=options,
    )

    fpbx = FusionPBX(
        driver,
        config.fusionpbx_url,
        config.fusionpbx_user,
        config.fusionpbx_password,
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
    user_id: str, domain: str, extension: str
) -> SIPProvisioning | ExtensionNotFound | DomainNotFound:
    """Retrieves FusionPBX provisioning details for a given user, domain, and extension,
    sets the data in the cache, and returns the SIP provisioning information.
    Args:
        user_id (int): The ID of the user requesting the provisioning details.
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
    r = SIPProvisioning(user=e.name, password=e.password, domain=d.name)
    # set cached data
    set_cached_provisioning(
        user_id,
        {
            'pbx_domain': d.name,
            'pbx_extension': e.name,
            'pbx_secret': e.password,
        },
    )
    pbx.browser.quit()

    return r
