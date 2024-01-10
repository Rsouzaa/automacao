# -*- coding: utf-8 -*-
"""
Utility module for the generation of HTML reports.
"""
import base64
import datetime
import logging
import os
from PIL import Image
import xml.dom.minidom
import json

from arc.contrib.tools.formatters import replace_chars
from settings import settings
from settings.settings import BASE_PATH

logger = logging.getLogger(__name__)

BASE_DIR = BASE_PATH

STATUS_ICONS = {
    'passed': '<i class="status-success-icon"></i>',
    'failed': '<i class="status-failed-icon"></i>',
    'skipped': '<i class="status-skipped-icon"></i>'
}


def format_decimal(value):
    """
    This function format a float value to 2 decimal.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"


def get_duration(value):
    """
    Given the seconds its return the datetime.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return datetime.timedelta(seconds=value)


def get_datetime_from_timestamp(timestamp):
    """
    Given a timestamp return a datetime
    :param timestamp:
    :type timestamp:
    :return:
    :rtype:
    """
    return datetime.datetime.fromtimestamp(timestamp) if timestamp is not None else "-"


def get_base64_image_by_path(image_path):
    """
    Return a base64 string given an image_path.
    :param image_path:
    :type image_path:
    :return:
    :rtype:
    """
    with open(image_path, 'rb') as image:
        return base64.b64encode(image.read()).decode()


def transform_image_to_webp(image_path):
    """
    Transform any image to webp, saves it in the html/assets/img folder and return the path to the image.
    :param image_path:
    """
    img = Image.open(image_path)
    img_name = img.filename.split(os.sep)[-1].replace('.png', '')
    logger.debug(f"Converting image to webp: {img_name}")
    if settings.PYTALOS_REPORTS.get('compress_screenshot', False):
        img.save(f"{BASE_PATH}/output/reports/html/assets/imgs/{img_name}.webp", quality=50)
        return f"./assets/imgs/{img_name}.webp"
    else:
        images_folder = img.filename.split(os.sep)[-2]
        return f"../../screenshots/{images_folder}/{img_name}.png"


def parse_url_params(url, params):
    """
    Parse url params.
    """
    for idx, param in enumerate(params):
        if idx == 0:
            url += f"?{param}={params[param]}"
        else:
            url += f"&{param}={params[param]}"
    return url


def json_pretty(json_data):
    """
    Format json indent.
    """
    return json.dumps(json_data, indent=4)


def parse_content_type(content):
    """
    Return content type parsed.
    """
    if content is not None:
        if isinstance(content, (list, dict)):
            return json.dumps(content, indent=4)
        if content.startswith('<'):
            dom = xml.dom.minidom.parseString(content)
            return dom.toprettyxml()
    else:
        content = '-'
    return content


def get_short_name(text):
    """
    Return short name from text and replace spanish letter into char compatible with html.
    """
    name = '%.100s' % text
    short_name = replace_chars(name).replace('Ñ', '&Ntilde;').replace('ñ', '&#241;')
    return short_name
