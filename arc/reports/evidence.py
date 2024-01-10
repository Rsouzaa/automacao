# -*- coding: utf-8 -*-
"""
Module of useful classes and functions for evidencing.
These functionalities aim to add additional information chosen by the user to the Talos execution reports.
"""
import json
import logging
from copy import deepcopy

from arc.contrib.host.utils import get_host_screenshot
from arc.contrib.utilities import Utils
from arc.core.test_method.exceptions import TalosReportException

logger = logging.getLogger(__name__)


class Evidence:
    """
    Class of extra evidence in the execution reports.
    """

    def __init__(self, context):
        self.context = context
        self.driver = str(context.current_driver).lower()
        self.utils = Utils()
        self.texts = []
        self.screenshots = []
        self.jsons = []
        self.unit_tables = []
        self.custom_tables = []

    def add_text(self, text):
        """
        This class adds text of type string to the report. It stores all texts from the run in a list that will
        later be seen in reports.
        :param text:
        :return:
        """
        try:
            logger.debug(f"adding text to the evidence: {text}")
            self.texts.append(str(text))
        except (Exception,) as ex:
            msg = f'Data passed by parameter is not valid: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)

    def add_screenshot(self, capture_name):
        """
        This class adds screenshot to the report. It stores all screenshot from the run in a list that will
        later be seen in reports.
        :param capture_name:
        :return:
        """
        try:
            if self.driver not in ['api', 'backend', 'service']:
                logger.debug(f"adding screenshot to the evidence: {capture_name}")
                if self.driver == 'host':
                    program_title = self.context.pytalos_config.get('Driver', 'window_title')
                    self.screenshots.append(get_host_screenshot(program_title, capture_name))
                else:
                    try:
                        self.screenshots.append(self.context.utilities.capture_screenshot(capture_name))
                    except AttributeError as ex:
                        logger.warning(ex)
                    except (Exception,) as ex:
                        logger.warning(ex)

        except (Exception,) as ex:
            msg = f'Error adding screenshot.: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)

    def add_json(self, title, data):
        """
        This class adds json format to the report. It stores all json format from the run in a list that will
        later be seen in reports.
        :param title:
        :param data:
        :return:
        """
        try:
            json_evidence = {
                'title': title,
                'content': deepcopy(data)
            }
            logger.debug(f"adding json to the evidence: {json_evidence}")
            self.jsons.append(json_evidence)
        except (Exception,) as ex:
            msg = f'Data passed by parameter is not valid: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)

    def add_unit_table(self, title, key, current_value, expected_value, result: bool, error_msg=None, **kwargs):
        """
        Add a unit table evidence to reports.
        :param title:
        :param key:
        :param current_value:
        :param expected_value:
        :param result:
        :param error_msg:
        :param kwargs:
        :return:
        """
        try:
            data = {
                'title': str(title),
                'key': str(key),
                'current value': str(current_value),
                'expected value': str(expected_value),
                **kwargs,
                'result': str(result),
            }
            logger.debug(f"adding unit table to the evidence: {data}")

            if result:
                data['result'] = 'Passed'
            else:
                data['result'] = 'Failed'

            if error_msg and result is False:
                data['error'] = error_msg

            self.unit_tables.append(data)
        except (Exception,) as ex:
            msg = f'Data passed by parameter is not valid: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)

    def add_custom_table(self, title, **kwargs):
        """
        Add a custom unit table to report depending of the kwargs passed by parameter.
        :param title:
        :param kwargs:
        :return:
        """
        try:
            data = {
                'title': title,
                **kwargs
            }
            logger.debug(f"adding custom table to the evidence: {data}")
            self.unit_tables.append(data)
        except (Exception,) as ex:
            msg = f'Data passed by parameter is not valid: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)

    def add_custom_table_from_dict(self, title, data):
        """
        Add a custom unit table evidence to report from a data dict.
        :param title:
        :param data:
        :return:
        """
        try:
            data = {
                'title': title,
                **data
            }
            logger.debug(f"adding custom table to the evidence: {data}")
            self.unit_tables.append(data)
        except (Exception,) as ex:
            msg = f'Data passed by parameter is not valid: {ex}'
            logger.error(msg)
            raise TalosReportException(msg)


def get_json_formatted(data):
    """
    Return json formatted by ident 4.
    :param data:
    :return:
    """
    return json.dumps(data, sort_keys=True, indent=4)
