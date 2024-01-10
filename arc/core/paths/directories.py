# -*- coding: utf-8 -*-
"""
In this file you will find the necessary functions for the creation of default folders that Talos needs to work,
as well as other useful functionalities to manage the folder structure of the framework.
"""
import logging
import os
import shutil

from arc.settings import settings as pytalos_settings
from settings import settings
from datetime import datetime

logger = logging.getLogger(__name__)

OUTPUT_BASEDIR = pytalos_settings.OUTPUT_PATH
SETTINGS_BASEDIR = pytalos_settings.SETTINGS_PATH
PROJECT_BASEDIR = pytalos_settings.BASE_PATH


def generate_needed_dir(current_driver):
    """
    This function create all dir needed for Talos execution.
    :param current_driver:
    :return:
    """
    try:
        logger.debug("Generating default folders:")
        if settings.PYTALOS_GENERAL['auto_generate_output_dir']:
            dir_json = os.path.join(OUTPUT_BASEDIR, 'json')
            dir_logs = os.path.join(OUTPUT_BASEDIR, 'logs')
            dir_reports = os.path.join(OUTPUT_BASEDIR, 'reports')
            dir_screenshots = os.path.join(OUTPUT_BASEDIR, 'screenshots')
            dir_info = os.path.join(OUTPUT_BASEDIR, 'info')

            dir_json_input = os.path.join(dir_json, 'input')
            dir_json_output = os.path.join(dir_json, 'output')
            dir_reports_html = os.path.join(dir_reports, 'html')
            dir_reports_doc = os.path.join(dir_reports, 'doc')
            dir_reports_pdf = os.path.join(dir_reports, 'pdf')

            if not os.path.isdir(OUTPUT_BASEDIR):
                os.mkdir(OUTPUT_BASEDIR)
                logger.debug(f"{OUTPUT_BASEDIR}")
            if not os.path.isdir(dir_json):
                os.mkdir(dir_json)
                logger.debug(f"{dir_json}")
            if not os.path.isdir(dir_logs):
                os.mkdir(dir_logs)
                logger.debug(f"{dir_logs}")
            if not os.path.isdir(dir_reports):
                os.mkdir(dir_reports)
                logger.debug(f"{dir_reports}")
            if not os.path.isdir(dir_screenshots):
                os.mkdir(dir_screenshots)
                logger.debug(f"{dir_screenshots}")
            if not os.path.isdir(dir_json_input):
                os.mkdir(dir_json_input)
                logger.debug(f"{dir_json_input}")
            if not os.path.isdir(dir_info):
                os.mkdir(dir_info)
                logger.debug(f"{dir_info}")
            if not os.path.isdir(dir_json_output):
                os.mkdir(dir_json_output)
                logger.debug(f"{dir_json_output}")

            if not os.path.isdir(SETTINGS_BASEDIR):
                os.mkdir(SETTINGS_BASEDIR)
                logger.debug(f"{SETTINGS_BASEDIR}")

            if not os.path.isdir(dir_reports_html):
                os.mkdir(dir_reports_html)
                os.mkdir(f"{dir_reports_html}/assets")
                os.mkdir(f"{dir_reports_html}/assets/imgs")
                logger.debug(f"{dir_reports_html}")
            if not os.path.isdir(dir_reports_doc):
                os.mkdir(dir_reports_doc)
                logger.debug(f"{dir_reports_doc}")
            if not os.path.isdir(dir_reports_pdf):
                os.mkdir(dir_reports_pdf)
                logger.debug(f"{dir_reports_pdf}")

        if settings.PYTALOS_GENERAL['auto_generate_test_dir']:
            dir_test = pytalos_settings.TEST_PATH
            if not os.path.isdir(dir_test):
                os.mkdir(dir_test)
                logger.debug(f"{dir_test}")

            dir_steps = os.path.join(pytalos_settings.TEST_PATH, 'steps')
            dir_features = os.path.join(pytalos_settings.TEST_PATH, 'features')
            dir_helpers = os.path.join(pytalos_settings.TEST_PATH, 'helpers')
            dir_resources = os.path.join(dir_helpers, 'resources')

            if not os.path.isdir(dir_steps):
                os.mkdir(dir_steps)
                logger.debug(f"{dir_steps}")
            if not os.path.isdir(dir_features):
                os.mkdir(dir_features)
                logger.debug(f"{dir_features}")
            if not os.path.isdir(dir_helpers):
                os.mkdir(dir_helpers)
                logger.debug(f"{dir_helpers}")
            if not os.path.isdir(dir_resources):
                os.mkdir(dir_resources)
                logger.debug(f"{dir_resources}")

            if str(current_driver).lower() not in ['api', 'backend', 'service']:
                dir_helpers_page_objects = os.path.join(pytalos_settings.TEST_PATH, 'helpers/page_objects')
                if not os.path.isdir(dir_helpers_page_objects):
                    os.mkdir(dir_helpers_page_objects)
                    logger.debug(f"{dir_helpers_page_objects}")

            if str(current_driver).lower() in ['api', 'backend', 'service']:
                dir_helpers_api_objects = os.path.join(pytalos_settings.TEST_PATH, 'helpers/api_objects')
                if not os.path.isdir(dir_helpers_api_objects):
                    os.mkdir(dir_helpers_api_objects)
                    logger.debug(f"{dir_helpers_api_objects}")
    except (Exception,) as ex:
        logger.warning(ex)


def delete_old_reports():
    """
    This functions remove all files and dir in the output folder.
    :return:
    """
    logger.info(f"Removing output directory: {OUTPUT_BASEDIR}")
    shutil.rmtree(OUTPUT_BASEDIR, ignore_errors=True)


def enable_delete_old_reports(activate):
    """
    Execute delete old report function if enabled.
    :param activate:
    :return:
    """
    if activate:
        logger.debug("delete old reports enabled")
        delete_old_reports()


def save_old_reports(output_path, file_format):
    """
    This function generates a compressed (zip) file from the output folder to save the reports in a temp folder if
    this setting is enabled.
    :param output_path:
    :param file_format:
    :return:
    """
    if not output_path:
        output_path = os.path.join(PROJECT_BASEDIR, 'temp')
    if os.path.exists(output_path) is False:
        os.makedirs(output_path, exist_ok=True)
        logger.debug(f"Temp folder created: {output_path}")
    if not str(output_path).endswith(os.sep):
        output_path = f"{output_path}{os.sep}"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = os.path.join(output_path, f"output_{timestamp}")
    shutil.make_archive(file_name, file_format, OUTPUT_BASEDIR)
    logger.debug(f"Output zip created with file name: {file_name}")


def enable_save_old_reports(save_reports):
    """
    This function execute save old report function if enabled
    :param save_reports:
    :return:
    """
    if save_reports['enabled'] and os.path.exists(OUTPUT_BASEDIR):
        logger.debug("save old report enabled")
        save_old_reports(save_reports['output_path'], save_reports['format'])
