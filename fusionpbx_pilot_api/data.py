from fusionpbx_pilot.page_objects import FusionPBX
from selenium.webdriver import Firefox

from fusionpbx_pilot_api.settings import Settings

config = Settings()

browser = Firefox()
fusionpbx = FusionPBX(
    browser,
    config.fusionpbx_url,
    config.fusionpbx_user,
    config.fusionpbx_password,
)
