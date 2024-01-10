# -*- coding: utf-8 -*-
"""
Classes and functionalities of utilities used in the environment.
"""
import datetime
import json
import logging
import os
import time
import traceback
import warnings

import yaml
from pkg_resources import parse_version

from arc.contrib.accessibility.axe_utils import write_results
from arc.contrib.accessibility.axe_wrapper import AxeWrapper
from arc.contrib.tools.formatters import replace_chars
from arc.contrib.tools.repository import Repository
from arc.contrib.utilities import get_valid_filename
from jinja2 import Environment, FileSystemLoader, select_autoescape

from arc.core.behave.template_var import replace_template_var
from arc.core.test_method.exceptions import TalosConfigurationError, TalosGenerationReportError
from arc.reports.html.utils import (
    BASE_DIR, get_datetime_from_timestamp,
    get_duration, json_pretty, parse_content_type,
    transform_image_to_webp, get_short_name
)
from settings import settings
from arc.contrib.utilities import load_translation
from arc.contrib.host import host
from arc.contrib.host.utils import get_host_screenshot
from arc.core import constants
from arc.core.config_manager import ConfigFiles
from arc.core.behave.context_utils import PyTalosContext
from arc.core.driver.driver_manager import DriverManager
from arc.integrations.jira import Jira
from arc.integrations.elasticsearch import Elasticsearch
from arc.page_elements import PageElement
from arc.core.test_method.visual_test import VisualTest
from arc.reports import log_generation, html_reporter
from arc.reports import generate_json
from test.helpers import hooks
from arc.reports.doc.create_report import CreateDOC
from arc.reports.pdf.create_report import CreatePDF
from arc.talos_virtual.core.contrib.mountebank.mountebank import MountebankWrapper
from arc.talos_virtual.core.context import TalosVirtual
from arc.talos_virtual.core.env_utils import create_dict_imposter
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from arc.contrib.tools.files import get_files_to_edit

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DynamicEnvironment:
    """
    Module of actions to dynamize the environment.
    """
    actions = None

    def __init__(self, **kwargs):
        self.show = kwargs.get("show", True)
        self.init_actions()
        self.scenario_counter = 0
        self.feature_error = False
        self.scenario_error = False

    def init_actions(self):
        """
        Initialization of environmental actions.
        """
        self.actions = {
            constants.ACTIONS_BEFORE_FEATURE: [],
            constants.ACTIONS_BEFORE_SCENARIO: [],
            constants.ACTIONS_AFTER_SCENARIO: [],
            constants.ACTIONS_AFTER_FEATURE: []
        }

    def get_label_from_description(self, row, label):
        """
        Return label from description of the actions
        """
        for action_label in self.actions:
            if row.lower().find(action_label) >= 0:
                label = action_label
        logger.debug(f"Getting label from description: {label}")
        return label

    def get_steps_from_feature_description(self, description):  # noqa
        """
        Get steps from the description of the features.
        """
        self.init_actions()
        label = constants.EMPTY
        for row in description:
            if label != constants.EMPTY:
                if "#" in row:
                    row = row[0:row.find("#")].strip()

                if any(row.startswith(x) for x in constants.KEYWORDS):
                    self.actions[label].append(row)
                elif row.find(constants.TABLE_SEPARATOR) >= 0:
                    self.actions[label][-1] = "%s\n      %s" % (self.actions[label][-1], row)
                else:
                    label = constants.EMPTY
            label = self.get_label_from_description(row, label)
            logger.debug(f"Get steps from the description of the features: {label}")

    @staticmethod
    def __remove_prefix(step):
        step_length = len(step)
        for k in constants.KEYWORDS:
            step = step.lstrip(k)
            if len(step) < step_length:
                break
        logger.debug(f"Step prefix removed: {step}")
        return step

    @staticmethod
    def __print_step(step):
        step_list = step.split(u'\n')
        for s in step_list:
            logger.info(u'    %s' % repr(s).replace("u'", "").replace("'", ""))

    def __execute_steps_by_action(self, context, action):
        if len(self.actions[action]) > 0:
            if action in [constants.ACTIONS_BEFORE_FEATURE, constants.ACTIONS_BEFORE_SCENARIO,
                          constants.ACTIONS_AFTER_FEATURE]:
                logger.info('\n')
                if action == constants.ACTIONS_BEFORE_SCENARIO:
                    self.scenario_counter += 1
                    logger.info(
                        f"  ------------------ Scenario Number: {self.scenario_counter} ------------------")
                logger.info('  %s:' % action)
            for item in self.actions[action]:
                self.scenario_error = False
                try:
                    self.__print_step(item)
                    context.execute_steps(u'''%s%s''' % (constants.GIVEN_PREFIX, self.__remove_prefix(item)))
                    logger.debug(u'step defined in pre-actions: %s' % repr(item))
                except Exception as exc:
                    if action in [constants.ACTIONS_BEFORE_FEATURE]:
                        self.feature_error = True
                    elif action in [constants.ACTIONS_BEFORE_SCENARIO]:
                        self.scenario_error = True
                    logger.error(exc)
                    self.error_exception = exc
                    break

    def reset_error_status(self):
        """
        Method of resetting the error status of the features and scenario.
        """
        try:
            return self.feature_error or self.scenario_error
        finally:
            self.feature_error = False
            self.scenario_error = False

    def execute_before_feature_steps(self, context):
        """
        Execution of before feature hooks.
        :param context:
        """
        self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_FEATURE)

        if context.pytalos.dyn_env.feature_error:
            context.feature.mark_skipped()

    def execute_before_scenario_steps(self, context):
        """
        Execution of before scenario hooks.
        :param context:
        """
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_SCENARIO)

        if context.pytalos.dyn_env.scenario_error:
            context.scenario.mark_skipped()

    def execute_after_scenario_steps(self, context):
        """
        Execution of after scenario hooks.
        :param context:
        """
        if not self.feature_error and not self.scenario_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_SCENARIO)

        if self.reset_error_status():
            context.scenario.reset()
            context.pytalos.dyn_env.fail_first_step_precondition_exception(context.scenario)

    def execute_after_feature_steps(self, context):
        """
        Execution of after feature hooks.
        :param context:
        """
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_FEATURE)

        if self.reset_error_status():
            context.feature.reset()
            for scenario in context.feature.walk_scenarios():
                context.pytalos.dyn_env.fail_first_step_precondition_exception(scenario)

    def fail_first_step_precondition_exception(self, scenario):
        """
        Method that fails the precondition in the first step.
        :param scenario:
        :return:
        """
        try:
            import behave
            if parse_version(behave.__version__) < parse_version('1.2.6'):
                status = 'failed'
            else:
                status = behave.model_core.Status.failed  # noqa
        except ImportError as exc:
            logger.error(exc)
            raise

        scenario.steps[0].status = status
        scenario.steps[0].exception = Exception("Preconditions failed")
        scenario.steps[0].error_message = self.error_exception.message  # noqa


def configure_properties_from_tags(context, scenario):
    """
    Configuration of properties according to labels that have the scenario in execution.
    :param context:
    :param scenario:
    """
    if 'no_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'true'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
        logger.debug(f"Found the no_reset_app tag in the scenario")
    elif 'reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
        logger.debug(f"Found the reset_app tag in the scenario")

    elif 'full_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'true'
        logger.debug(f"Found the full_reset_app tag in the scenario")

    if 'reset_driver' in scenario.tags:
        DriverManager.stop_drivers()
        DriverManager.download_videos('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.save_all_ggr_logs('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.remove_drivers()
        context.pytalos.global_status['test_passed'] = True
        logger.debug(f"Found the reset_driver tag in the scenario")

    if 'android_only' in scenario.tags and context.pytalos.driver_wrapper.is_ios_test():
        scenario.skip('Android scenario')
        logger.debug(f"Found the android_only tag in the scenario")
    elif 'ios_only' in scenario.tags and context.pytalos.driver_wrapper.is_android_test():
        scenario.skip('iOS scenario')
        logger.debug(f"Found the ios_only tag in the scenario")


def utils_before_execution():
    """
    Useful functions that are executed before the execution of the tests.
    """
    dev_mode = False
    if hasattr(settings, 'DEV_MODE'):
        dev_mode = settings.DEV_MODE
    if dev_mode is False:
        valid_parameter("application", 2)
        valid_parameter("business_area", 2)
        valid_parameter("entity", 2)
        valid_parameter("user_code", 2)


def valid_parameter(parameter, length):
    """
    Parameter validation function of Talos configurations.
    :param parameter:
    :param length:
    """
    valid = False
    msg_error = "Fields: application, business_area, entity, user_code which are in settings in PROJECT_INFO " \
                "section are required. "
    if parameter in settings.PROJECT_INFO:
        if isinstance(settings.PROJECT_INFO.get(parameter), str):
            if len(settings.PROJECT_INFO.get(parameter)) >= length:
                if not str(settings.PROJECT_INFO.get(parameter)).startswith(" "):
                    valid = True
                else:
                    msg_error += f"{parameter} starts with a space. "
            else:
                msg_error += f"{parameter} has a length less than {length} characters. "
        else:
            msg_error += f"{parameter} is not type string. "
    else:
        msg_error += f"{parameter} was not found in PROJECT_INFO section. "

    if not valid:
        msg_error += "\nFor more details see " \
                     "https://confluence.alm.europe.cloudcenter.corp/display/QUASER/Project+info+fields"
        logger.exception(msg_error, exc_info=False)
        raise TalosConfigurationError(msg_error)


from arc.core.behave.config_data import get_profile_data
from arc.core.behave.template_var import get_global


def save_profile_dict(repository):
    final_dict = {}
    files_profiles = get_profile_data()
    files_repositories = repository.data
    files_repositories['elements'] = repository.elements
    files_repositories['literals'] = repository.literals
    final_dict['profiles'] = files_profiles
    final_dict['repositories'] = files_repositories
    template_var = get_global()
    template_var.update(final_dict)


def utils_before_all(context):
    """
    Useful functions that are executed before all of the tests.
    :param context:
    """
    env = context.config.userdata.get('Config_environment')
    context.pytalos = PyTalosContext(context)

    if env:
        os.environ['Config_environment'] = env

    if not hasattr(context, 'config_files'):
        logger.debug(f"Adding config_files instance to context.pytalos")
        context.pytalos.config_files = ConfigFiles()
    logger.debug(f"Initializing configuration files")
    context.pytalos.config_files = DriverManager.initialize_config_files(context.pytalos.config_files)

    if not context.pytalos.config_files.config_directory:
        logger.debug(f"Setting directory settings")
        context.pytalos.config_files.set_config_directory(DriverManager.get_default_config_directory())

    if settings.PYTALOS_PROFILES['repositories'] is True:
        logger.debug(f"Setting repository data")
        context.repositories = Repository()

    save_profile_dict(context.repositories)

    logger.debug(f"Creating core wrapper")
    context.pytalos.global_status = {'test_passed': True}
    create_wrapper(context)
    logger.debug(f"Creating dynamic environment")
    context.pytalos.dyn_env = DynamicEnvironment()


def utils_before_feature(context, feature):
    """
    Useful functions that are executed before features.
    :param context:
    :param feature:
    """
    context.pytalos.global_status = {'test_passed': True}
    no_driver = 'no_driver' in feature.tags
    context.pytalos.reuse_driver_from_tags = 'reuse_driver' in feature.tags

    if context.pytalos_config.getboolean_optional('Driver', 'reuse_driver') or context.pytalos.reuse_driver_from_tags:
        logger.info("Starting reuse driver")
        start_driver(context, no_driver)

    context.pytalos.dyn_env.get_steps_from_feature_description(feature.description)
    context.pytalos.dyn_env.execute_before_feature_steps(context)


def utils_before_scenario(context, scenario):
    """
    Useful functions that are executed before features.
    :param context:
    :param scenario:
    """
    configure_properties_from_tags(context, scenario)
    no_driver = 'no_driver' in scenario.tags or 'no_driver' in scenario.feature.tags
    logger.info("Starting driver")
    start_driver(context, no_driver)
    add_assert_screenshot_methods(context, scenario)
    logger.info(f"Running scenario: {scenario.name}")
    context.pytalos.dyn_env.execute_before_scenario_steps(context)


def utils_after_scenario(context, scenario, status):
    """
    Useful functions that are executed after scenario.
    :param context:
    :param scenario:
    :param status:
    """
    if status == 'skipped':
        logger.info(f"The scenario {scenario.name} has skipped")
        return
    elif status == 'passed':
        logger.info(f"The scenario {scenario.name} has passed")
    else:
        logger.error(f"The scenario {scenario.name} has failed")
        context.pytalos.global_status['test_passed'] = False

    logger.info("Closing driver in scope function")
    DriverManager.close_drivers(
        scope='function',
        test_name=scenario.name,
        test_passed=status == 'passed',
        context=context
    )


def utils_after_feature(context, feature):
    """
    Useful functions that are executed after feature.
    :param context:
    :param feature:
    :return:
    """
    context.pytalos.dyn_env.execute_after_feature_steps(context)
    logger.info("Closing driver in scope module")
    DriverManager.close_drivers(
        scope='module',
        test_name=feature.name,
        test_passed=context.pytalos.global_status['test_passed']
    )


def utils_after_all(context):
    """
    Useful functions that are executed after all.
    :param context:
    :return:
    """
    logger.info("Closing driver in scope session")
    DriverManager.close_drivers(
        scope='session',
        test_name='multiple_tests',
        test_passed=context.pytalos.global_status['test_passed']
    )
    update_profile_files()


def utils_after_execution():
    """
    Useful functions that are executed after execution.
    """
    dev_mode = False
    if hasattr(settings, 'DEV_MODE'):
        dev_mode = settings.DEV_MODE
    if dev_mode is False:
        try:
            logger.info('Posting information to Elastic Search')
            Elasticsearch().run()
        except (Exception,):
            logger.warning('Upload to ElasticSearch error')


def create_wrapper(context):
    """
    Method of creating the wrapper according to driver configuration.
    :param context:
    """
    context.pytalos.driver_wrapper = DriverManager.get_default_wrapper()
    context.utils = context.pytalos.driver_wrapper.utils

    try:
        behave_properties = context.config.userdata
    except AttributeError:
        behave_properties = None

    logger.debug(f"Configuring driver wrapper")
    context.pytalos.driver_wrapper.configure(context.pytalos.config_files, behave_properties=behave_properties)
    logger.debug(f"Driver wrapper configured with:")
    logger.debug(context.pytalos.config_files)
    logger.debug(behave_properties)
    context.pytalos_config = context.pytalos.driver_wrapper.config
    logger.debug(context.pytalos_config)


def connect_wrapper(context):
    """
    Connect the wrapper to the no driver session.
    :param context:
    :return:
    """
    reuse_driver_session = context.pytalos_config.getboolean_optional('Driver', 'reuse_driver_session')
    if context.pytalos.driver_wrapper.driver and reuse_driver_session:
        context.driver = context.pytalos.driver_wrapper.driver
    else:
        context.driver = context.pytalos.driver_wrapper.connect(scenario=context.scenario)

    context.pytalos.app_strings = context.pytalos.driver_wrapper.app_strings


def start_driver(context, no_driver):
    """
    Driver execution function.
    :param context:
    :param no_driver:
    """
    create_wrapper(context)
    if not no_driver:
        connect_wrapper(context)


def add_assert_screenshot_methods(context, scenario):
    """
    Function that adds assertion methods for screenshots for visual testing.
    :param context:
    :param scenario:
    """
    file_suffix = scenario.name

    def assert_screenshot(element_or_selector, filename, threshold=0, exclude_elements=None, driver_wrapper=None,
                          force=False):
        """
        Comparing a screenshot to an element or selector.
        :param element_or_selector:
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param driver_wrapper:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(
            element_or_selector,
            filename,
            file_suffix,
            threshold,
            exclude_elements
        )

    def assert_full_screenshot(filename, threshold=0, exclude_elements=None, driver_wrapper=None, force=False):
        """
        Comparison of a full screenshot.
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param driver_wrapper:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(
            None,
            filename,
            file_suffix,
            threshold,
            exclude_elements
        )

    def assert_screenshot_page_element(self, filename, threshold=0, exclude_elements=None, force=False):
        """
        Compare a screenshot to a page element.
        :param self:
        :param filename:
        :param threshold:
        :param exclude_elements:
        :param force:
        :return:
        """
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(self.driver_wrapper, force).assert_screenshot(
            self.web_element,
            filename,
            file_suffix,
            threshold,
            exclude_elements
        )

    context.assert_screenshot = assert_screenshot
    context.assert_full_screenshot = assert_full_screenshot
    PageElement.assert_screenshot = assert_screenshot_page_element


def enable_txt_report():
    """
    Enabling the report in txt format.
    :return:
    """
    if settings.PYTALOS_REPORTS['generate_txt']:
        logger.info(f"TXT report enabled")
        return log_generation.ExecutionTxtLog()


def set_alm_custom_variable(context):
    """
    Setting custom alm result variable.
    :param context:
    :return:
    """
    logger.debug('Initialising ALM custom result attributes')
    context.runtime.step.result_expected = None
    context.runtime.step.obtained_result_failed = None
    context.runtime.step.obtained_result_passed = None
    context.runtime.step.obtained_result_skipped = None


def enable_json_report(scenario):
    """
    Enabling the report in json format for ALM.
    :param scenario:
    :return:
    """
    if settings.PYTALOS_ALM['post_to_alm']:
        logger.info(f"Upload to ALM enabled")
        settings.PYTALOS_ALM['generate_json'] = True
    if settings.PYTALOS_ALM['generate_json']:
        logger.info(f"Json ALM report enabled")
        return generate_json.GenerateJson(scenario)


def enable_host(context):
    """
    Configuring default values in host executions.
    :param context:
    :return:
    """
    if context.pytalos_config.get('Driver', 'type') == 'host':
        ws_path = context.pytalos_config.get('Driver', 'ws_path')
        cscript = context.pytalos_config.get('Driver', 'cscript_path')
        context.host = host.Host(ws_path, cscript)
        logger.debug("Host properties configured:")
        logger.debug(f"WS path: {ws_path}")
        logger.debug(f"CScript path: {cscript}")


def close_host(context):
    """
    Closes the host window if the settings option is enabled.
    :param context:
    :return:
    """
    if context.pytalos_config.get('Driver', 'type') == 'host':
        if settings.PYTALOS_RUN['close_host']:
            logger.info("Closing the host window")
            context.host.close_emulator()


def config_faker():
    """
    Set faker parameters if installed.
    :return:
    """
    try:
        from faker import Faker  # noqa
        return Faker(settings.PYTALOS_PROFILES['locale_fake_data'])
    except (Exception,):
        return None


def run_hooks(context, moment, extra_info=None):
    """
    Run user custom hooks
    :param context:
    :param moment:
    :param extra_info:
    :return:
    """
    logger.info(f'Running user hook: {moment}')
    try:
        if moment == 'before_execution':
            hooks.before_execution()
        elif moment == 'before_all':
            hooks.before_all(context)
        elif moment == 'after_all':
            hooks.after_all(context)
        elif moment == 'before_feature':
            hooks.before_feature(context, extra_info)
        elif moment == 'after_feature':
            hooks.after_feature(context, extra_info)
        elif moment == 'before_scenario':
            hooks.before_scenario(context, extra_info)
        elif moment == 'after_scenario':
            hooks.after_scenario(context, extra_info)
        elif moment == 'before_step':
            hooks.before_step(context, extra_info)
        elif moment == 'after_step':
            hooks.after_step(context, extra_info)
        elif moment == 'after_execution':
            hooks.after_execution()
        elif moment == 'before_reports':
            hooks.before_reports(extra_info)
        elif moment == 'before_tag':
            hooks.before_tag(context, extra_info)
        elif moment == 'after_tag':
            hooks.after_tag(context, extra_info)
    except (Exception,) as ex:
        logger.warning(f"WARNING: there was an error in the hooks {moment}: {ex}")


def generate_simple_html_reports(generate):
    """
    Generate simple html report if enabled
    :param generate:
    :return:
    """
    if generate:
        try:
            logger.info(f"Simple html generation enabled")
            html_reporter.make_html_reports()
        except (Exception,) as ex:
            logger.warning(ex)


def generate_html_reports(json_data):
    """
    This function generates the html reports.
    :return:
    :rtype:
    """
    logger.debug('HTML generation begins')
    try:
        html_files, attach_files = _generate_html_reports(json_data)
        return html_files, attach_files

    except (Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate HTML reports, Exception error: {ex}")


def prepare_json_data(json_data):
    """
    Return prepared talos data json.
    """
    scenario_names = []
    for feature in json_data['features']:
        for scenario in feature['elements']:
            if scenario['name'] in scenario_names:
                scenario_location = str(scenario['location']).rfind(':')
                _scenario = f"{get_short_name(scenario['name'])}_{scenario['location'][scenario_location + 1:]}"
                scenario['scenario_file_name'] = _scenario
                logger.debug(f'Getting scenario data from: {_scenario}')
            else:
                _scenario = get_short_name(scenario['name'])
                scenario['scenario_file_name'] = _scenario
                logger.debug(f'Getting scenario data from report json from scenario: {_scenario}')
                scenario_names.append(scenario['name'])
    logger.debug(f"Talos json data prepared")
    return json_data


def _generate_html_reports(json_data):
    """
    This function generates the html reports.
    :return:
    :rtype:
    """
    logger.debug('Configuring Babel environment for translations of the HTML report')
    gnu_translations = load_translation('html_reports')

    env = Environment(
        extensions=['jinja2.ext.i18n'],
        loader=FileSystemLoader(f"{BASE_DIR}/arc/resources/html_templates"),
        autoescape=select_autoescape(),
    )

    env.install_gettext_translations(gnu_translations, newstyle=True)  # noqa

    _ = gnu_translations.gettext

    env.filters['format_datetime'] = get_datetime_from_timestamp
    env.filters['get_duration'] = get_duration
    env.filters['jsonpretty'] = json_pretty
    env.filters['parse_content_type'] = parse_content_type
    env.filters['transform_image_to_webp'] = transform_image_to_webp
    env.filters['replace_template_var'] = replace_template_var
    env.filters['get_short_name'] = get_short_name

    global_template = env.get_template("global_template.html")
    logger.debug(f"Translations uploaded for HTML template: {global_template}")

    css_path = f"{BASE_DIR}/arc/resources/talos_html_reports.css"
    with open(css_path) as f:
        styles = f.read()
    logger.debug(f"HTML report CSS loaded: {css_path}")

    data = {
        "style": styles,
        "page_title": f"{_('Global Report')}",
        "navbar_title": f"{_('Global Report')} - {json_data['global_data']['application']}",
        "features": json_data['features'],
        "global_data": json_data['global_data']
    }

    logger.debug(f"Data form HTML report configured")

    global_template.stream(data).dump(f"{BASE_DIR}/output/reports/html/global.html")
    feature_template = env.get_template("feature_template.html")
    scenario_template = env.get_template("scenario_template.html")
    html_files = [
        f"{BASE_DIR}/output/reports/html/global.html",
    ]

    attach_files = {}
    for feature in json_data['features']:
        feature['name'] = replace_chars(feature['name'])
        feature['short_name'] = get_short_name(feature['name'])
        feature_data = {
            "style": styles,
            "page_title": f"{_('Report for feature')} {feature['name']}",
            "navbar_title": f"{_('Report for feature')} {feature['name']}",
            "feature": feature,
            "global_data": json_data['global_data']
        }
        feature_template.stream(feature_data).dump(
            f"{BASE_DIR}/output/reports/html/feature_{feature['short_name']}.html")
        html_files.append(f"{BASE_DIR}/output/reports/html/feature_{feature['short_name']}.html")
        for scenario in feature['elements']:
            if scenario['type'] != "background":
                scenario['name'] = replace_chars(scenario['name'])
                scenario['short_name'] = get_short_name(scenario['name'])
                scenario_data = {
                    "style": styles,
                    "feature_name": feature['name'],
                    "feature_short_name": feature['short_name'],
                    "page_title": f"{_('Report for scenario')} {scenario['name']}",
                    "navbar_title": f"{_('Report for scenario')} {scenario['name']}",
                    "scenario": scenario,
                    "scenario_short_name": scenario['short_name'],
                    "global_data": json_data['global_data']
                }
                scenario_template.stream(scenario_data).dump(
                    f"{BASE_DIR}/output/reports/html/scenario_{scenario['scenario_file_name']}.html")
                file_path = f"{BASE_DIR}/output/reports/html/scenario_{scenario['scenario_file_name']}.html"
                html_files.append(file_path)
                attach_files[file_path] = []
                for step in scenario['steps']:
                    if step.get('screenshots'):
                        attach_files[file_path] += [screenshot for screenshot in step['screenshots']]


    logger.debug(f"HTML templates loaded: {html_files}")
    logger.debug(f"HTML scenario template loaded: {scenario_template}")
    return html_files, attach_files


def post_jira(reports, json_data):
    """
    This function generates the pdf reports.
    :return:
    :rtype:
    """
    try:
        logger.info(f"Jira report enabled")
        jira = Jira()
        logger.info("Starting process of publishing evidences in Jira")
        for i in range(0, len(json_data.get("features", []))):
            if reports.get('html'):
                html_files = reports.get('html')[i]
            else:
                html_files = None
            if reports.get('doc'):
                doc_files = reports.get('doc')[i]
            else:
                doc_files = None
            if reports.get('pdf'):
                pdf_files = reports.get('pdf')[i]
            else:
                pdf_files = None
            jira.post_to_jira(json_data.get("features", [])[i], html_files, pdf_files, doc_files)
        logger.info("Publishing process in Jira finished successfully")
    except(Exception,) as ex:
        logger.exception(ex)
        traceback.print_exc()


def generate_doc_reports(json_data):
    """
    This function generates the doc and pdf reports.
    :return:
    :rtype:
    """
    try:
        doc_report = CreateDOC()
        for feature in json_data.get("features", []):
            doc_files = doc_report.generate_document_report(feature, json_data.get("global_data", []))
        return doc_files
    except(Exception,) as ex:
        logger.exception(ex)
        raise TalosGenerationReportError(f"It was impossible to generate DOC reports, Exception error: {ex}")


def generate_pdf_reports(json_data):
    """
        This function generates the doc and pdf reports.
    :return:
    :rtype:
    """
    global pdf_files

    def generate_pdf_reports(json_data):
        try:
            pdf_report = CreatePDF()
            pdf_files = []
            for feature in json_data.get("features", []):
                pdf_files.extend(pdf_report.generate_document_report(feature, json_data.get("global_data", [])))
            return pdf_files
        except Exception as ex:
            logger.exception(ex)
            raise TalosGenerationReportError(f"It was impossible to generate PDF reports, Exception error: {ex}")


def validate_generate_reports():
    """
    Validation of configurations for report generation.
    :return:
    """
    logger.debug('Validating reports to be generated')
    if settings.PYTALOS_ALM.get('post_to_alm', False):
        if settings.PYTALOS_ALM.get('attachments', False).get('pdf', False):
            settings.PYTALOS_REPORTS['generate_pdf'] = True
        if settings.PYTALOS_ALM.get('attachments', False).get('docx', False):
            settings.PYTALOS_REPORTS['generate_docx'] = True
        if settings.PYTALOS_ALM.get('attachments', False).get('html', False):
            settings.PYTALOS_REPORTS['generate_html'] = True
    if settings.PYTALOS_JIRA.get('post_to_jira', False):
        if settings.PYTALOS_JIRA.get('report', False).get('upload_pdf_evidence', False):
            settings.PYTALOS_REPORTS['generate_pdf'] = True
        if settings.PYTALOS_JIRA.get('report', False).get('upload_doc_evidence', False):
            settings.PYTALOS_REPORTS['generate_docx'] = True
        if settings.PYTALOS_JIRA.get('report', False).get('upload_html_evidence', False):
            settings.PYTALOS_REPORTS['generate_html'] = True


def update_profile_files():
    files_to_edit = get_files_to_edit()
    for key, value in files_to_edit.items():
        if key.endswith(".json"):
            with open(key, 'w', encoding='utf8') as json_file:
                json.dump(value, json_file)
        elif key.endswith(".yaml"):
            with open(key, 'w', encoding='utf8') as yaml_file:
                yaml.dump(value, yaml_file)


def generate_screenshot(context, step):
    """
    Screenshot generation.
    :param context:
    :param step:
    :return:
    """
    current_driver = str(context.current_driver).lower()
    if current_driver not in ['api', 'backend', 'service']:
        if settings.PYTALOS_REPORTS['generate_screenshot']:
            if current_driver == 'host':
                program_title = context.pytalos_config.get('Driver', 'window_title')
                screenshot = get_host_screenshot(program_title)
                logger.debug(f"Screenshot for host saved: {screenshot}")
                return screenshot
            else:
                screenshot = get_step_screenshot(context, step)
                logger.debug(f"Screenshot for webdriver saved: {screenshot}")
                return screenshot
        elif settings.PYTALOS_REPORTS['generate_screenshot_if_failed'] is True and \
                step.status == 'failed' and current_driver != 'host':
            screenshot = get_step_screenshot(context, step)
            logger.debug(f"Screenshot for step failure saved: {screenshot}")
            return screenshot


def get_step_screenshot(context, step):
    """
    Gets screenshot of the step.
    :param context:
    :param step:
    :return:
    """
    try:
        return context.utilities.capture_screenshot(
            f"{str(step.keyword)}_{str(step.name)}"
        )
    except AttributeError as ex:
        logger.warning(ex)
    except (Exception,) as ex:
        logger.warning(ex)


def set_initial_step_data(step):
    """
    This function set new initial data to the step passed in order to avoid errors in the html reports generation.
    :param step:
    :type step:
    :return:
    :rtype:
    """
    step.response_content = None
    step.response_headers = None
    step.request = None
    step.screenshots = []
    step.jsons = []
    step.api_info = []
    step.unit_tables = []
    step.additional_text = []
    step.start_time = datetime.datetime.now().timestamp()
    step.end_time = None
    step.sub_steps = []
    logger.debug('Setup initial step data')
    return step


def set_initial_scenario_data(scenario):
    """
    This function set new initial data to the scenario passed in order
    to avoid errors in the html reports generation.
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    scenario.start_time = datetime.datetime.now().timestamp()
    scenario.end_time = None
    scenario.total_steps = 0
    scenario.steps_passed = 0
    scenario.steps_failed = 0
    scenario.steps_skipped = 0
    scenario.steps_passed_percent = "0"
    scenario.steps_failed_percent = "0"
    scenario.steps_skipped_percent = "0"
    scenario.sub_steps = []
    logger.debug('Setup initial scenario data')
    return scenario


def set_initial_feature_data(context, feature):
    """
    This function set new initial data to the scenario passed in order
    to avoid errors in the html reports generation.
    :param context:
    :type context:
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.start_time = datetime.datetime.now().timestamp()
    feature.end_time = None
    feature.driver = context.current_driver
    feature.passed_scenarios = 0
    feature.failed_scenarios = 0
    feature.total_scenarios = 0

    feature.total_steps = 0
    feature.steps_passed = 0
    feature.steps_failed = 0
    feature.steps_skipped = 0

    feature.passed_scenarios = 0
    feature.failed_scenarios = 0
    feature.total_scenarios = 0

    feature.scenarios_passed_percent = "0"
    feature.scenarios_failed_percent = "0"
    feature.steps_passed_percent = "0"
    feature.steps_failed_percent = "0"
    feature.steps_skipped_percent = "0"
    logger.debug('Setup initial feature data')

    return feature


def add_step_data(context, step, screenshot_path):
    """
    This function add data to the step in order to be reflected in the json file.
    :param context:
    :type context:
    :param step:
    :type step:
    :param screenshot_path:
    :type screenshot_path:
    :return:
    :rtype:
    """
    step.end_time = datetime.datetime.now().timestamp()
    try:
        if hasattr(context, "response") and len(context.runtime.api_info) > 0:
            if not hasattr(step, 'parent_step'):
                step.request = dict({
                    "url": context.runtime.api_info['url'],
                    "headers": context.runtime.api_info['headers'],
                    "body": context.runtime.api_info['body'],
                    "params": context.runtime.api_info['params']
                })
                step.response_content = context.runtime.api_info['response']
                step.response_headers = context.runtime.api_info['response_headers']
                step.api_info = context.runtime.api_info
            else:
                step.parent_step.request = dict({
                    "url": context.runtime.api_info['url'],
                    "headers": context.runtime.api_info['headers'],
                    "body": context.runtime.api_info['body'],
                    "params": context.runtime.api_info['params']
                })
                step.parent_step.api_info = context.runtime.api_info
                step.parent_step.response_content = context.runtime.api_info['response']
                step.parent_step.response_headers = context.runtime.api_info['response_headers']
    except KeyError as ex:
        logger.warning(ex)

    if not hasattr(step, 'parent_step'):
        step.jsons += context.func.evidences.jsons
        step.unit_tables += context.func.evidences.unit_tables
        step.additional_text += context.func.evidences.texts
        step.screenshots += context.func.evidences.screenshots
        step.screenshots += [screenshot_path] if screenshot_path is not None else []
    else:
        context.func.evidences.screenshots += [screenshot_path] if screenshot_path is not None else []

    logger.debug('Execution step data information added into json report')

    return step


def add_scenario_data(scenario):
    """
    This function add data to the scenario in order to be reflected in the json file.
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    if settings.PYTALOS_REPORTS.get('include_sub_steps_in_results', False):
        scenario.steps += scenario.sub_steps
    scenario.end_time = datetime.datetime.now().timestamp()
    scenario.total_steps = len(scenario.steps + scenario.background_steps)
    scenario.steps_passed, scenario.steps_failed, scenario.steps_skipped = count_scenario_passed_steps(scenario)

    scenario.steps_passed_percent = "0" if scenario.steps_passed == 0 else format_decimal(
        scenario.steps_passed * 100 / scenario.total_steps)
    scenario.steps_failed_percent = "0" if scenario.steps_failed == 0 else format_decimal(
        scenario.steps_failed * 100 / scenario.total_steps)
    scenario.steps_skipped_percent = "0" if scenario.steps_skipped == 0 else format_decimal(
        scenario.steps_skipped * 100 / scenario.total_steps
    )
    logger.debug('Execution scenario data information added into json report')
    return scenario


def add_feature_data(feature):
    """
        This function add data to the feature in order to be reflected in the json file.
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.end_time = datetime.datetime.now().timestamp()

    for scenario in feature.scenarios:
        if scenario.type == "scenario" and scenario.status != "skipped":
            if scenario.status == "passed":
                feature.passed_scenarios += 1
            elif scenario.status == "failed":
                feature.failed_scenarios += 1
            feature.total_scenarios += 1

            feature.total_steps += scenario.total_steps
            feature.steps_passed += scenario.steps_passed
            feature.steps_failed += scenario.steps_failed
            feature.steps_skipped += scenario.steps_skipped

        elif scenario.type == "scenario_outline":
            scenarios_list = [_scenario for _scenario in scenario.scenarios if _scenario.status != "skipped"]

            _passed_scenarios, _failed_scenarios, _total_scenarios = count_feature_passed_scenarios(scenarios_list)
            feature.passed_scenarios += _passed_scenarios
            feature.failed_scenarios += _failed_scenarios
            feature.total_scenarios += _total_scenarios

            for scenario_from_scenario_list in scenarios_list:
                feature.total_steps += scenario_from_scenario_list.total_steps
                feature.steps_passed += scenario_from_scenario_list.steps_passed
                feature.steps_failed += scenario_from_scenario_list.steps_failed
                feature.steps_skipped += scenario_from_scenario_list.steps_skipped

    feature.scenarios_passed_percent = "0" if feature.passed_scenarios == 0 else format_decimal(
        feature.passed_scenarios * 100 / feature.total_scenarios)
    feature.scenarios_failed_percent = "0" if feature.failed_scenarios == 0 else format_decimal(
        feature.failed_scenarios * 100 / feature.total_scenarios)

    feature.steps_passed_percent = "0" if feature.steps_passed == 0 else format_decimal(
        feature.steps_passed * 100 / feature.total_steps)
    feature.steps_failed_percent = "0" if feature.steps_failed == 0 else format_decimal(
        feature.steps_failed * 100 / feature.total_steps)
    feature.steps_skipped_percent = "0" if feature.steps_skipped == 0 else format_decimal(
        feature.steps_skipped * 100 / feature.total_steps)
    logger.debug('Execution feature data information added into json report')

    return feature


def count_scenario_passed_steps(scenario):
    """
        This function counts and return the passed, failed and skipped steps given a scenario object
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    passed_steps = 0
    failed_steps = 0
    skipped_steps = 0
    steps = scenario.steps + scenario.background_steps

    for step in steps:
        if step.status == "passed":
            passed_steps += 1
        elif step.status == "failed":
            failed_steps += 1
        elif step.status == "skipped":
            skipped_steps += 1
        elif step.status == "undefined":
            skipped_steps += 1
    logger.debug(f"Step results of the executed scenario:")
    logger.debug(f"Passed: {passed_steps}, Failed: {failed_steps}, Skipped: {skipped_steps}")
    return passed_steps, failed_steps, skipped_steps


def count_feature_passed_scenarios(scenarios):
    """
        This function counts and return the passed, failed and skipped steps given a feature object
    :param scenarios:
    :type scenarios:
    :return:
    :rtype:
    """
    passed_scenarios = 0
    failed_scenarios = 0
    total_scenarios = 0

    for scenario in scenarios:
        if scenario.status == "passed":
            passed_scenarios += 1
            total_scenarios += 1
        else:
            failed_scenarios += 1
            total_scenarios += 1
    logger.debug(f"Scenarios results of the executed feature:")
    logger.debug(f"Passed: {passed_scenarios}, Failed: {failed_scenarios}")
    return passed_scenarios, failed_scenarios, total_scenarios


def format_decimal(value):
    """
    Format value to decimal
    :param value:
    :return:
    """
    return f"{value:.2f}"


def set_accessibility_initial_data(context):
    """
    Configuring accessibility test initial data
    :param context:
    :return:
    """
    if settings.PYTALOS_ACCESSIBILITY.get('automatic_analysis'):
        logger.info('Accessibility automatic analysis enabled')
        context.runtime.current_url = 'data:,'
        settings_rules = settings.PYTALOS_ACCESSIBILITY.get('rules')
        logger.debug(f"Accessibility rules activated: {settings_rules}")

        context.runtime.rules = []
        for rule in settings_rules.keys():
            if rule == 'cat':
                for cat in settings_rules[rule].keys():
                    if settings_rules[rule][cat]:
                        context.runtime.rules.append(f"cat.{cat}")
            elif settings_rules[rule]:
                context.runtime.rules.append(rule)


def run_accessibility_test(context):
    """
    Execute accessibility test if enabled
    :param context:
    :return:
    """
    no_driver = ['backend', 'no_driver', 'service', 'api']
    if settings.PYTALOS_ACCESSIBILITY.get('automatic_analysis') and context.current_driver not in no_driver:
        if context.driver.current_url != context.runtime.current_url:
            logger.info("Analysis of accessibility running:")
            logger.info(f"URL to analyze: {context.runtime.current_url}")
            context.runtime.current_url = context.driver.current_url
            axe = AxeWrapper(context.driver)
            axe.inject()

            if not context.runtime.rules:
                options = None
            else:
                options = {
                    'runOnly': context.runtime.rules
                }

            results = axe.run(options=options)

            file_name = results['url'] \
                .replace('https://', '') \
                .replace('www', '') \
                .replace('.com', '') \
                .replace('.html', '') \
                .replace('.htm', '') \
                .replace('.asp', '') \
                .replace('.php', '')

            file_name = get_valid_filename(file_name)
            logger.debug(f"Results generated in: {file_name}")
            write_results(results, file_name)


def init_talos_virtual(context):
    """
    This function initialize talos virtual if it is enabled in settings.
    :param context:
    :return:
    """
    if settings.TALOS_VIRTUAL['mountebank']["enabled"]:
        context.talosvirtual = TalosVirtual(context)
        context.talosvirtual.mountebank = MountebankWrapper()
        context.talosvirtual.mountebank.start_process()
        create_dict_imposter(context)
        context.talosvirtual.mountebank.create_imposter(
            dict_imposter=context.talosvirtual.mountebank.dict_imposter  # noqa
        )


def init_auto_retry(feature):
    """
    This function initialize autoretry if it is enabled in settings.
    :param feature:
    :return:
    """
    if settings.PYTALOS_RUN['autoretry']['enabled']:
        attempts = settings.PYTALOS_RUN['autoretry']['attempts']
        logger.debug(f"Execution auto retry is enabled with {attempts} attempts")
        for scenario in feature.scenarios:
            patch_scenario_with_autoretry(scenario, max_attempts=attempts)
    else:
        for scenario in feature.scenarios:
            if 'autoretry' in scenario.tags:
                logger.debug(f"Autoretry tag found in scenario: {scenario.name}")
                patch_scenario_with_autoretry(scenario, max_attempts=settings.PYTALOS_RUN['autoretry']['attempts'])


def wait_seconds_autoretry(context):
    """
    This function wait in seconds a time between attempts.
    :return:
    """
    if (settings.PYTALOS_RUN['autoretry']['enabled'] or 'autoretry' in context.scenario.tags) \
            and context.scenario.status.name == 'failed':
        logger.debug('Performing auto retry wait')
        time.sleep(settings.PYTALOS_RUN['autoretry']['attempts_wait_seconds'])
