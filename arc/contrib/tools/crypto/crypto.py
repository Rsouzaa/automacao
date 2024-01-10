# -*- coding: utf-8 -*-
"""
Module for crypto data in TalosBDD.
"""
import base64
import logging
import os
from colorama import Fore

from arc.contrib.tools.crypto.cypher import Cypher
from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled

logger = logging.getLogger(__name__)


def encode(data, passphrase=os.environ.get('PASSPHRASE')):
    """
    This function encrypt and return the passed string.
    Default passphrase is retrieved from environment variables.
    You can use any passphrase if it has 16 characters length
    :param data:
    :param passphrase:
    """
    logger.debug('Encoding data')
    if data == '' or passphrase is None or passphrase == '' or len(passphrase) != 16:
        msg = "PASSPHRASE is none or blank"
        print(Fore.YELLOW + msg)
        logger.warning(msg)
        return data
    encryptor = Cypher(passphrase=passphrase)
    return encryptor.encrypt(data)


def decode(data, passphrase=os.environ.get('PASSPHRASE')):
    """
    This function decrypt and return the passed string.
    Default passphrase is retrieved from environment variables.
    You can use any passphrase if it has 16 characters length
    :param data:
    :param passphrase:
    """
    logger.debug('Decoding data')
    if data == '' or passphrase is None or passphrase == '' or len(passphrase) != 16:
        msg = "PASSPHRASE is none or blank"
        print(Fore.YELLOW + msg)
        logger.warning(msg)
        return data
    encryptor = Cypher(passphrase=passphrase)
    return encryptor.decrypt(data)


def encode_base64(data):
    """
    Given a string, return a base64 encoded
    :param data:
    """
    logger.debug('Encoding base64 data')
    return base64.b64encode(data)


def decode_base64(data):
    """
    Given a base64 string, return the decoded string.
    :param data:
    """
    logger.debug('Decoding base64 data')
    return base64.b64decode(data)


def encode_jwt(payload: dict, algorithm='HS256', private_key='', headers=None):
    """
    Given a payload, return a jwt token.
    The default algorithm is HS256 but the user can pass another algorithm.
    The user can pass if needed a private_key or secret and headers
    :param payload:
    :param algorithm:
    :param private_key:
    :param headers:
    """
    logger.debug('Encoding jwt data')
    try:
        import jwt  # noqa
        return jwt.encode(payload=payload, algorithm=algorithm, key=private_key, headers=headers)
    except ImportError:
        msg = "PyJWT module is not installed. Go to requirements.txt, " \
              "uncomment the PyJWT module and run pip install -r requirements.txt"
        logger.error(msg)
        raise TalosNotThirdPartyAppInstalled(msg)


def decode_jwt(jwt_token, algorithm='HS256', private_key='', headers=None):
    """
    Given a jwt token, decode a jwt token.
    The default algorithm is HS256 but the user can pass another algorithm.
    The user can pass if needed a private_key or secret and headers
    :param jwt_token:
    :param algorithm:
    :param private_key:
    :param headers:
    """
    logger.debug('Decoding jwt data')
    try:
        import jwt  # noqa
        return jwt.decode(jwt=jwt_token, algorithm=algorithm, key=private_key, headers=headers)
    except ImportError:
        msg = "PyJWT module is not installed. Go to requirements.txt, " \
              "uncomment the PyJWT module and run pip install -r requirements.txt"
        logger.error(msg)
        raise TalosNotThirdPartyAppInstalled(msg)
