# -*- coding: utf-8 -*-
"""
Talos Framework init.
"""
import logging

from dotenv import load_dotenv  # noqa
from arc.core.logger import config_logger

__VERSION__ = "2.2.0"
config_logger()

logger = logging.getLogger(__name__)
logger.info('Starting TalosBDD execution')
logger.info(f"TalosBDD version: {__VERSION__}")
logger.debug('TalosBDD logger configured')

load_dotenv()
