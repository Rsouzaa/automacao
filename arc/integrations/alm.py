# -*- coding: utf-8 -*-
"""
Integration module with MF ALM.
It contains all the necessary functions for run the ALM connector.
"""
import logging
import os
import shutil
from subprocess import call

from settings import settings
from arc.settings import settings as arc_settings
from zipfile import ZipFile


ALM3_PROP_PATH = os.path.abspath("resources")
JSON_INPUT_PATH = os.path.abspath("output") + os.sep + 'json' + os.sep + 'input' + os.sep

logger = logging.getLogger(__name__)


def alm3_properties(flag):
    """
    Check if alm3 properties is enabled. Then, copy alm.properties to json input folder.
    :param flag:
    :return:
    """
    alm_file = 'alm.properties'
    if flag:
        logger.info('ALM3 properties is enabled')
        alm_prop = os.path.join(arc_settings.RESOURCES_PATH, alm_file)
        shutil.copy(alm_prop, JSON_INPUT_PATH)
    else:
        alm_json_path = os.path.join(JSON_INPUT_PATH, alm_file)
        if os.path.isfile(alm_json_path):
            os.remove(alm_json_path)


def run_alm_connect(attach_files):
    """
    Run ALM connect process.
    :return:
    """
    if settings.PYTALOS_ALM['post_to_alm']:
        zip_name = None
        if settings.PYTALOS_ALM['attachments']['html']:
            zip_name = compress_html_report(attach_files)
        logger.info('Running ALM connect')
        jar_path = 'arc/resources/'
        json_path = 'output/json/'
        alm3_properties(settings.PYTALOS_ALM['alm3_properties'])
        call(['java', '-jar', jar_path + 'talos-alm-connect-5.1.1.jar', json_path])
        delete_zip_report(zip_name)


def compress_html_report(attach_files):
    for key, value in attach_files.items():
        name = f"output{key.split('output')[1]}"

        zip_name = name.replace('.html', '.zip').replace('reports/html/', '')

        with ZipFile(zip_name, mode="w") as archive:
            archive.write(
                name,
                arcname=name
            )
            for screenshot in value:
                screenshot_path = f"output{screenshot.split('output')[1]}"
                if settings.PYTALOS_REPORTS['compress_screenshot']:
                    screenshot_path = screenshot_path.replace('screenshots', 'reports\\html\\assets\\imgs')
                    index = screenshot_path.rfind(os.sep)
                    img_name = screenshot_path[index:]
                    screenshot_path = f"{screenshot_path.split('imgs')[0]}imgs{img_name}"
                    screenshot_path = screenshot_path.replace('.png', '.webp')
                archive.write(
                    screenshot_path,
                    arcname=screenshot_path
                )
    return zip_name


def delete_zip_report(zip_name):
    if zip_name is not None:
        os.remove(zip_name)
