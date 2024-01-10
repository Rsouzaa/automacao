# -*- coding: utf-8 -*-
"""
File with useful environment variable configuration functions.
"""
import logging
import os

logger = logging.getLogger(__name__)


def enabled_proxy(http, https):
    """
    This function set proxy configuration in environment variable for http and https url passed by parameter.
    :param http:
    :param https:
    :return:
    """
    os.environ["HTTP_PROXY"] = str(http)
    os.environ["HTTPS_PROXY"] = str(https)
    logger.info(f"Environment proxy set up with: http:{http} and https:{https}")


def disabled_environment_proxy(settings):
    if settings.PYTALOS_GENERAL['environment_proxy']['enabled']:
        if os.environ.get('HTTP_PROXY'):
            del os.environ["HTTP_PROXY"]
        if os.environ.get('HTTPS_PROXY'):
            del os.environ["HTTPS_PROXY"]


def activate_environment_proxy(settings):
    """
    This function call enabled_proxy function if environment proxy configuration is enabled in settings file.
    :param settings:
    :return:
    """
    if settings.PYTALOS_GENERAL['environment_proxy']['enabled']:
        logger.info("Environment proxy is enabled.")
        http = settings.PYTALOS_GENERAL['environment_proxy']['proxy']['http_proxy']
        https = settings.PYTALOS_GENERAL['environment_proxy']['proxy']['https_proxy']
        enabled_proxy(http, https)
