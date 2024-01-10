# -*- coding: utf-8 -*-
"""
Functions for automatic installation of selenium browser drivers.
"""
import logging
import os
import shutil

from arc.core.test_method.exceptions import TalosRunError
from settings import settings
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from arc.core import constants

logger = logging.getLogger(__name__)


def _disabled_proxy():
    """
    This function disables the proxy configured when installing the drivers if the proxy option is enabled in
    the settings
    :return:
    """
    if settings.PYTALOS_GENERAL['update_driver']['enable_proxy']:
        logger.debug(f"Disabling existed proxy for installing driver")
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""


def _enabled_proxy():
    """
    This function disables the proxy configured when installing the drivers if the proxy option is disabled in
    the settings
    :return:
    """
    if settings.PYTALOS_GENERAL['update_driver']['enable_proxy']:
        http = settings.PYTALOS_GENERAL['update_driver']['proxy']['http_proxy']
        https = settings.PYTALOS_GENERAL['update_driver']['proxy']['https_proxy']
        logger.debug(f"http: {http}")
        logger.debug(f"https: {https}")
        logger.debug(f"settings.PYTALOS_GENERAL['update_driver']['proxy']['http_proxy']")
        os.environ["HTTP_PROXY"] = http
        os.environ["HTTPS_PROXY"] = https


class InstallDriver:
    """
    Selenium driver automatic installation class.
    """
    temp_path = 'settings/temp_drivers'
    drivers_path = 'settings/drivers/'

    def __init__(self, driver_name):
        logger.debug(f"Initializing {driver_name} installation")
        self.driver_name = driver_name

    def _create_temp_folder(self):
        if not os.path.exists(self.temp_path):
            logger.debug(f"Creating temp folder in: {self.temp_path}")
            os.mkdir(self.temp_path)

    def _delete_temp_folder(self):
        if os.path.exists(self.temp_path):
            logger.debug(f"Deleting temp folder: {self.temp_path}")
            shutil.rmtree(self.temp_path)

    def _move_driver(self, driver_path):
        logger.debug(f"Moving driver into: {driver_path}")
        shutil.move(driver_path, self.drivers_path + self.driver_name)

    def _download_driver(self, driver):
        logger.debug(f"Downloading driver: {driver}")
        driver_path = ''
        if driver == constants.IEXPLORER:
            driver_path = IEDriverManager(path=self.temp_path).install()
        elif driver == constants.CHROME:
            driver_path = ChromeDriverManager(path=self.temp_path).install()
        elif driver == constants.EDGE:
            driver_path = EdgeChromiumDriverManager(path=self.temp_path).install()
        elif driver == constants.FIREFOX:
            driver_path = GeckoDriverManager(path=self.temp_path).install()
        logger.debug(f"Successful driver download in: {driver_path}")
        return driver_path

    def install_driver(self, driver):
        """
        This method start the driver installation..
        :param driver:
        :return:
        """
        try:
            _enabled_proxy()
            self._create_temp_folder()
            driver_path = self._download_driver(driver)
            self._move_driver(driver_path)
            self._delete_temp_folder()
            _disabled_proxy()
        except (Exception,):
            self._delete_temp_folder()
            msg = 'Impossible to update ' + driver + ' driver.'
            logger.exception(msg)
            raise TalosRunError(msg)
