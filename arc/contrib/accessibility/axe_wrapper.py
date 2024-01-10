# -*- coding: utf-8 -*-
"""
Control for the management and call of accessibility tests with Axe.
This module makes use of Axe Core JS to perform the analysis of Accessibility tests.
To perform the requirements and run the analysis, use the axe.min library.js located at resources/modules/axe-core.

Its operation is done by JS script executions of the library mentioned above to the browser through the execute_script
function of Selenium.
"""
import logging
import os
from io import open

from arc.settings.settings import RESOURCES_PATH

logger = logging.getLogger(__name__)

_DEFAULT_SCRIPT = os.path.join(
    RESOURCES_PATH, "modules", "axe-core", "axe.min.js"
)


class AxeWrapper(object):
    """
    Wrapper de Axe Core JS. Functions for the execution of JS scripts and report generation.
    """

    def __init__(self, driver, script_url=_DEFAULT_SCRIPT):
        self.script_url = script_url
        self.driver = driver

    def inject(self):
        """
        Reading the axe-core.js and obtaining the functions.
        """
        with open(self.script_url, "r", encoding="utf8") as f:
            self.driver.execute_script(f.read())
            logger.debug(f'Axe script injected: {self.script_url}')

    def run(self, context=None, options=None):
        """
        Function of execution of the scripts according to the configuration of the context and the
        options passed by parameter.

        :param context:
        :param options:
        """
        template = (
                "var callback = arguments[arguments.length - 1];"
                + "axe.run(%s).then(results => callback(results))"
        )
        args = ""

        # If context parameter is passed, add to args
        if context is not None:
            args += "%r" % context
        # Add comma delimiter only if both parameters are passed
        if context is not None and options is not None:
            args += ","
        # If options parameter is passed, add to args
        if options is not None:
            args += "%s" % options

        command = template % args
        logger.info(f'Execution Axe with commands: {command}')
        response = self.driver.execute_async_script(command)
        logger.debug(f'Response from Axe execution received')
        return response

    def get_rules(self, rule='None'):
        """
        Returns Axe Core rules to be used in script execution options.
        :param rule:
        """
        if rule is None:
            rule = []

        if type(rule) is str:
            command = f"return axe.getRules(['{rule}']);"
        elif type(rule) is list:
            command = f"return axe.getRules({rule});"
        else:
            return
        response = self.driver.execute_script(command)
        logger.debug(f"Accessibility rules obtained: {response}")
        return response
