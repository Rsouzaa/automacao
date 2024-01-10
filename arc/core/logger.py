# -*- coding: utf-8 -*-
"""
Talos logger configuration module.
"""
import logging.config
import os
import yaml
import shutil

from settings import settings

LOGGER_CONFIG = 'arc/settings/logging.conf'
LOGGER_OUTPUT_FILE = 'pytalos.log'
LOGGER_OUTPUT_DIR = os.path.join(settings.OUTPUT_PATH, 'logs')


def config_logger():
    """
    This function configure the logger module.
    :return:
    """
    if settings.PYTALOS_GENERAL.get('logger', None).get('clear_log', None):
        if os.path.isdir(os.path.join(settings.BASE_PATH, LOGGER_OUTPUT_DIR)):
            shutil.rmtree(os.path.join(settings.BASE_PATH, LOGGER_OUTPUT_DIR), ignore_errors=True)
    if not os.path.isdir(LOGGER_OUTPUT_FILE):
        os.makedirs(LOGGER_OUTPUT_DIR, exist_ok=True)
    config_file = get_config_dict()
    file_level = settings.PYTALOS_GENERAL.get('logger', None).get('file_level', None)
    console_level = settings.PYTALOS_GENERAL.get('logger', None).get('console_level', None)
    format_file = settings.PYTALOS_GENERAL.get('logger', None).get('format_file', None)
    format_console = settings.PYTALOS_GENERAL.get('logger', None).get('format_console', None)
    date_format = settings.PYTALOS_GENERAL.get('logger', None).get('date_format', None)
    config_file['formatters']['fileFormatter']['format'] = format_file
    config_file['formatters']['consoleFormatter']['format'] = format_console
    config_file['formatters']['fileFormatter']['datefmt'] = date_format
    config_file['formatters']['consoleFormatter']['datefmt'] = date_format
    config_file['handlers']['fileHandler']['level'] = file_level
    config_file['handlers']['consoleHandler']['level'] = console_level
    if settings.PYTALOS_GENERAL.get('logger', None).get('disable_console_log', None) is True:
        del config_file['handlers']['consoleHandler']
        del config_file['loggers']['root']['handlers'][1]
    logging.config.dictConfig(config_file)


def get_config_dict():
    """
    Return logger configuration from yaml.
    :return:
    """
    with open('arc/settings/logging.yaml', 'r') as f:
        config_dict = yaml.safe_load(f)
    return config_dict
