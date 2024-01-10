# -*- coding: utf-8 -*-
"""
Module with SQLite database control classes.
"""
import logging
from sqlite3.dbapi2 import Connection

import sqlite3

from settings import settings

logger = logging.getLogger(__name__)


def sqlite_db():
    """
    Return a SQLite connection instance.
    :return:
    """
    if settings.SQLITE['enabled']:
        logger.info('SQLite context instance is enabled')
        try:
            sqlite_home = settings.SQLITE['sqlite_home']
            logger.info(f"Creating a SQLite connection from: {sqlite_home}")
            connection: Connection = sqlite3.connect(sqlite_home)
            logger.debug(f"The sqlite db was generated correctly in the path: {sqlite_home}")
            return connection
        except (Exception,) as ex:
            logger.warning(f"There was an error initializing the sqlite db instance: {ex}")
            return None
