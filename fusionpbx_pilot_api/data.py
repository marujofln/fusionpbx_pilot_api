from fusionpbx_pilot.page_objects import FusionPBX
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from fusionpbx_pilot_api.settings import Settings

config = Settings()

options = Options()
options.add_argument('--headless')  # Run in headless mode

service = FirefoxService(GeckoDriverManager().install())

driver = webdriver.Firefox(service=service, options=options)
fusionpbx = FusionPBX(
    driver,
    config.fusionpbx_url,
    config.fusionpbx_user,
    config.fusionpbx_password,
)
