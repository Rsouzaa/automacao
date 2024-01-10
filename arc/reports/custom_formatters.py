# -*- coding: utf-8 -*-
"""
Customised Behave compatible formatters module for customised Talos for the purpose of output.
"""
import base64
import datetime
import json
import os
import platform
import random
import traceback

from arc import __VERSION__
from behave.formatter.base import Formatter
from behave.model_core import Status
from behave.textutil import select_best_encoding, ensure_stream_with_encoder as _ensure_stream_with_encoder
from colorama import Fore
from settings import settings
from arc.core.behave.template_var import replace_template_var

from urllib3.packages import six  # noqa
import logging

logger = logging.getLogger(__name__)


def get_json_report_args_for_parallel():
    """
    Return arguments needed in order to create the json report for parallel execution.
    """
    ext = random.randrange(1000000000, 9999999999)
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    args = f" -f arc.reports.custom_formatters:CustomJSONFormatter " \
           f"-o output/reports/talos_report_{now}_{ext}.json -f arc.reports.custom_formatters:CustomParallelFormatter"
    logger.debug(f"Arguments of execution for json report generation: {args}")
    return args


def get_json_report_args():
    """
    Return arguments needed in order to create the json report for sequential execution.
    """
    args = f" -f arc.reports.custom_formatters:CustomJSONFormatter -o output/reports/talos_report.json --format pretty"
    logger.debug(f"Arguments of execution for json report generation: {args}")
    return args


def _get_obtained_result(step):
    """
    Return obtained result parsed.
    """
    if str(step.status) == 'Status.passed':
        if step.obtained_result_passed:
            obtained_result = str(step.obtained_result_passed)
        else:
            obtained_result = "Operation with correct result"
    elif str(step.status) == "Status.failed":
        if step.obtained_result_failed:
            obtained_result = str(step.obtained_result_failed)
        else:
            obtained_result = "Operation with incorrect result"
    else:
        if step.obtained_result_skipped:
            obtained_result = str(step.obtained_result_skipped)
        else:
            obtained_result = "Operation skipped"
    return obtained_result


def _get_expected_result(step):
    """
    Return expected result parsed.
    """
    if step.result_expected:
        expected_result = str(step.result_expected)
    else:
        expected_result = str(replace_template_var(step.name))
    return expected_result


class StreamOpener(object):
    """
    Provides a transport vehicle to open the formatter output stream
    when the formatter needs it.
    In addition, it provides the formatter with more control:

      * when a stream is opened
      * if a stream is opened at all
      * the name (filename/dirname) of the output stream
      * let it decide if directory mode is used instead of file mode
    """
    # FORMER: default_encoding = "UTF-8"
    default_encoding = select_best_encoding()

    def __init__(self, filename=None, stream=None, encoding=None):
        if not encoding:
            encoding = self.default_encoding
        if stream:
            stream = self.ensure_stream_with_encoder(stream, encoding)
        self.name = filename
        self.stream = stream
        self.encoding = encoding
        self.should_close_stream = not stream  # Only for not pre-opened ones.

    @staticmethod
    def ensure_dir_exists(directory):
        """
        Create directory if this does not exists.
        """
        if directory and not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except (Exception,) as ex:
                logger.warning(ex)

    @classmethod
    def ensure_stream_with_encoder(cls, stream, encoding=None):
        """
        Ensure stream execution with encoder.
        """
        return _ensure_stream_with_encoder(stream, encoding)

    def open(self):
        """
        Open and return stream.
        """
        if not self.stream or self.stream.closed:
            self.ensure_dir_exists(os.path.dirname(self.name))
            stream = open(self.name, "w", encoding=self.encoding)
            stream = self.ensure_stream_with_encoder(stream, self.encoding)
            self.stream = stream  # -- Keep stream for house-keeping.
            self.should_close_stream = True
            assert self.should_close_stream
        return self.stream

    def close(self):
        """
        Close the stream, if it was opened by this stream_opener.
        Skip closing for sys.stdout and pre-opened streams.
        :return: True, if stream was closed.
        """
        closed = False
        if self.stream and self.should_close_stream:
            closed = getattr(self.stream, "closed", False)
            if not closed:
                self.stream.close()
                closed = True
            self.stream = None
        return closed


class CustomJSONFormatter(Formatter):
    """
    This is a custom json formatter to generate the talos_report.json
    """
    name = "json"
    description = "JSON dump of test run"
    dumps_kwargs = {"ensure_ascii": False, "indent": 4}
    split_text_into_lines = True  # EXPERIMENT for better readability.

    json_number_types = six.integer_types + (float,)
    json_scalar_types = json_number_types + (six.text_type, bool, type(None))

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0
        self.features_storage = []

    def open(self):
        """
        Ensure that the output stream is open.
        Triggers the stream opener protocol (if necessary).

        :return: Output stream to use (just opened or already open).
        """
        if not self.stream:
            self.stream = self.stream_opener.open()
        return self.stream

    def reset(self):
        """
        Rest needed properties.
        """
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    # -- FORMATTER API:
    def uri(self, uri):
        """
        Called before processing a file (normally a feature file).
        :param uri:  URI or filename (as string).
        """
        pass

    def feature(self, feature):
        """
        This method generate feature data BEFORE executing it.
        So there is no way to add new data using this method.
        :param feature:
        :type feature:
        :return:
        :rtype:
        """
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": replace_template_var(feature.name),
            "tags": list(feature.tags),
            "location": six.text_type(feature.location),
            "status": None,  # Not known before feature run.
        }
        element = self.current_feature_data
        if feature.description:
            for i in range(len(feature.description)):
                feature.description[i] = replace_template_var(feature.description[i])
            element["description"] = feature.description

    def background(self, background):
        """
        This method generate background data BEFORE executing it.
        So there is no way to add new data using this method.
        :param background:
        :type background:
        :return:
        :rtype:
        """
        if os.environ['RUN_TYPE'] == 'sequential':
            element = self.add_feature_element({
                "type": "background",
                "keyword": background.keyword,
                "name": background.name,
                "location": six.text_type(background.location),
                "steps": [],
            })
            if background.name:
                element["name"] = background.name
            self._step_index = 0

            # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
            for step_ in background.steps:
                self.step(step_)

    def scenario(self, scenario):
        """
        This method generate scenario data BEFORE executing it.
        So there is no way to add new data using this method.
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        self.finish_current_scenario()
        self.current_scenario = scenario
        if '@' in scenario.name:
            scenario.name = str(scenario.name).replace('@', '')
        element = self.add_feature_element({
            "type": "scenario",
            "keyword": scenario.keyword,
            "name": replace_template_var(scenario.name),
            "tags": scenario.tags,
            "location": six.text_type(scenario.location),
            "steps": [],
            "status": None,
        })
        if scenario.description:
            for i in range(len(scenario.description)):
                scenario.description[i] = replace_template_var(scenario.description[i])
            element["description"] = scenario.description
        self._step_index = 0

    @classmethod
    def make_table(cls, table):
        """
        Create table from headers and rows.
        :param table:
        :return:
        """
        table_data = {
            "headings": table.headings,
            "rows": [list(row) for row in table.rows]
        }
        return table_data

    def step(self, step):
        """
        Set step data.
        :param step:
        :return:
        """
        s = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": six.text_type(step.location),
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            s["text"] = text
        if step.table:
            s["table"] = self.make_table(step.table)
        element = self.current_feature_element
        element["steps"].append(s)

    def match(self, match):
        """
        Match steps arguments.
        :param match:
        :return:
        """
        args = []
        for argument in match.arguments:
            argument_value = argument.value
            if not isinstance(argument_value, self.json_scalar_types):
                # -- OOPS: Avoid invalid JSON format w/ custom types.
                # Use raw string (original) instead.
                argument_value = argument.original
            assert isinstance(argument_value, self.json_scalar_types)
            arg = {
                "value": argument_value,
            }
            if argument.name:
                arg["name"] = argument.name
            if argument.original != argument_value:
                # -- REDUNDANT DATA COMPRESSION: Suppress for strings.
                arg["original"] = argument.original
            args.append(arg)

        match_data = {  # noqa
            "location": six.text_type(match.location) or "",
            "arguments": args,
        }

        if match.location:
            # -- NOTE: match.location=None occurs for undefined steps.
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["match"] = match_data

    def result(self, step):
        """
        When a step end, the result data is generated here.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        if str(step.status) != 'Status.undefined':
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["result"] = {
                "status": step.status.name,
                "duration": step.duration,
                "expected_result": _get_expected_result(step),
                "obtained_result": _get_obtained_result(step)
            }
            steps[self._step_index]['name'] = replace_template_var(step.name)
            if steps[self._step_index].get('text'):
                if isinstance(steps[self._step_index]['text'], list):
                    for i in range(len(steps[self._step_index]['text'])):
                        steps[self._step_index]['text'][i] = replace_template_var(steps[self._step_index]['text'][i])
                else:
                    steps[self._step_index]['text'] = replace_template_var(steps[self._step_index]['text'])
            # Extra data.
            steps[self._step_index]['start_time'] = step.start_time
            steps[self._step_index]['end_time'] = step.end_time
            steps[self._step_index]["screenshots"] = step.screenshots
            steps[self._step_index]["additional_text"] = step.additional_text
            steps[self._step_index]["request"] = step.request
            steps[self._step_index]["response_content"] = step.response_content
            steps[self._step_index]["response_headers"] = step.response_headers
            steps[self._step_index]["jsons"] = step.jsons
            steps[self._step_index]["api_info"] = step.api_info
            steps[self._step_index]["unit_tables"] = step.unit_tables
            steps[self._step_index]["sub_steps"] = self.get_sub_steps(step)

            if step.error_message and step.status == Status.failed:
                # -- OPTIONAL: Provided for failed steps.
                # error_message = step.error_message
                # if self.split_text_into_lines and "\n" in error_message:
                #     error_message = error_message.splitlines()
                result_element = steps[self._step_index]["result"]
                result_element["error_message"] = step.exception.__str__()
            self._step_index += 1

    def get_sub_steps(self, step):
        _sub_steps = []
        if hasattr(step, 'sub_steps'):
            for sub_step in step.sub_steps:
                if sub_step.status == 'untested':
                    _sub_steps.append({
                        'keyword': sub_step.keyword,
                        'step_type': sub_step.step_type,
                        'name': replace_template_var(sub_step.name),
                        'sub_steps': self.get_sub_steps(sub_step)
                    })
                else:
                    _sub_steps.append({
                        'keyword': sub_step.keyword,
                        'step_type': sub_step.step_type,
                        'name': replace_template_var(sub_step.name),
                        'result': {
                            "status": sub_step.status.name,
                            "duration": sub_step.duration,
                            "expected_result": _get_expected_result(sub_step),
                            "obtained_result": _get_obtained_result(sub_step)
                        },
                        'start_time': sub_step.start_time,
                        'end_time': sub_step.end_time,
                        'screenshots': sub_step.screenshots,
                        'additional_text': sub_step.additional_text,
                        'request': sub_step.request,
                        'response_content': sub_step.response_content,
                        'response_headers': sub_step.response_headers,
                        'jsons': sub_step.jsons,
                        'api_info': sub_step.api_info,
                        'unit_tables': sub_step.unit_tables,
                        'sub_steps': self.get_sub_steps(sub_step)
                    })
        return _sub_steps

    def embedding(self, mime_type, data):
        """
        Create a embeddings element into step dict.
        :param mime_type:
        :param data:
        :return:
        """
        step = self.current_feature_element["steps"][-1]
        step["embeddings"].append({
            "mime_type": mime_type,
            "data": base64.b64encode(data).replace("\n", ""),  # noqa
        })

    def eof(self):
        """
        This method writes the feature data when the feature execution ended.
        End of feature
        """
        if not self.current_feature_data:
            return

        if 'no_evidences' in self.current_feature.tags:
            return

        self.get_template_var()
        self.add_scenario_data()
        self.add_feature_data()
        # -- NORMAL CASE: Write collected data of current feature.
        self.finish_current_scenario()
        self.update_status_data()

        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        """
        Close the stream.
        :return:
        :rtype:
        """
        if self.feature_count == 0:
            # -- FIRST FEATURE: Corner case when no features are provided.
            self.write_json_header()
        self.write_json_footer()
        self.close_stream()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        """
        Add element to feature.
        :param element:
        :return:
        """
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        """
        Return current feature elements data.
        :return:
        """
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        """
        Update status of feature.
        :return:
        """
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        """
        finish curren scenario data.
        :return:
        """
        if self.current_scenario:
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

    # -- JSON-WRITER:
    def write_json_header(self):
        """
        Write into json the header needed.
        :return:
        """
        self.stream.write("{\n \"features\":[")

    def write_json_footer(self):
        """
        This method end the features list and add the global data.
        :return:
        :rtype:
        """
        self.stream.write("],")
        self.stream.write(self.add_global_data())
        self.stream.write("\n}\n")

    def write_json_feature(self, feature_data):
        """
        This method write the feature data to the json file
        :param feature_data:
        :type feature_data:
        :return:
        :rtype:
        """
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        """
        Write separator by feature into json.
        :return:
        """
        self.stream.write(",\n\n")

    def get_template_var(self):
        """
        This method replace the template var in scenarios skipped.
        :return:
        :rtype:
        """
        for elem in self.current_feature_data['elements']:
            if elem['type'] == 'scenario':
                for step in elem['steps']:
                    if not step.get('result'):
                        step['name'] = replace_template_var(step['name'])

    def add_scenario_data(self):
        """
        This method add scenario data from the current_feature to the current_feature_data.
        :return:
        :rtype:
        """
        info_scenarios = {}
        count = 0
        for elem in self.current_feature_data['elements']:
            if elem["location"] not in info_scenarios.keys():
                info_scenarios[elem["location"]] = []
                count = 0
            count += 1
            info_scenarios[elem["location"]] = count

        for key in info_scenarios:
            count_scenarios = 1
            for idx, _element in enumerate(self.current_feature_data['elements']):
                while key in _element['location'] and count_scenarios < info_scenarios[key]:
                    del self.current_feature_data['elements'][idx]
                    count_scenarios += 1

        scenarios_feature_data = [element for element in self.current_feature_data['elements']
                                  if element.get("status") != "skipped" and
                                  element.get("type") in ['scenario', 'scenario_outline']]

        scenarios_list = []
        index_outline_scenarios = []
        count_total_scenario = 0
        for scenario in self.current_feature.scenarios:
            if scenario.type == "scenario":
                if scenario.status.name != "skipped":
                    scenarios_feature_data[count_total_scenario] = update_feature_scenario_data(
                        scenarios_feature_data[count_total_scenario], scenario)
                    count_total_scenario += 1
            elif scenario.type == "scenario_outline":
                if scenario.status.name != "skipped":
                    new_scenarios = [_scenario for _scenario in scenario.scenarios]
                    scenarios_list += new_scenarios
                    for i in range(0, len(new_scenarios)):
                        index_outline_scenarios.append(count_total_scenario + i)
                    count_total_scenario += len(new_scenarios)

        if len(scenarios_list) > 0:
            count_total_scenario = 0
            for scenario in scenarios_list:
                if scenario.status != "skipped":
                    scenarios_feature_data[
                        index_outline_scenarios[count_total_scenario]] = update_feature_scenario_data(
                        scenarios_feature_data[index_outline_scenarios[count_total_scenario]], scenario)
                    count_total_scenario = count_total_scenario + 1

    def add_feature_data(self):
        """
        This method add feature data from the current_feature to the current_feature_data
        :return:
        :rtype:
        """
        self.current_feature_data['total_scenarios'] = self.current_feature.total_scenarios
        self.current_feature_data['passed_scenarios'] = self.current_feature.passed_scenarios
        self.current_feature_data['failed_scenarios'] = self.current_feature.failed_scenarios
        self.current_feature_data['scenarios_passed_percent'] = self.current_feature.scenarios_passed_percent
        self.current_feature_data['scenarios_failed_percent'] = self.current_feature.scenarios_failed_percent
        self.current_feature_data['total_steps'] = self.current_feature.total_steps
        self.current_feature_data['steps_passed'] = self.current_feature.steps_passed
        self.current_feature_data['steps_failed'] = self.current_feature.steps_failed
        self.current_feature_data['steps_skipped'] = self.current_feature.steps_skipped
        self.current_feature_data['steps_passed_percent'] = self.current_feature.steps_passed_percent
        self.current_feature_data['steps_failed_percent'] = self.current_feature.steps_failed_percent
        self.current_feature_data['steps_skipped_percent'] = self.current_feature.steps_skipped_percent
        self.current_feature_data['start_time'] = self.current_feature.start_time
        self.current_feature_data['end_time'] = self.current_feature.end_time
        self.current_feature_data['duration'] = self.current_feature.duration
        self.current_feature_data['operating_system'] = f"{platform.system()} {platform.release()}"
        self.current_feature_data['driver'] = self.current_feature.driver

        self.features_storage.append(self.current_feature_data)

    def calculate_global_results(self):
        """
        This method calculate the following values for the global data section:
        - Start time of the execution
        - End time of the execution
        - Features passed
        - Features failed
        - Total scenarios
        - Scenarios passed
        :return:
        :rtype:
        """
        global_result = {
            "total_features": len(self.features_storage),
            "features_passed": 0,
            "features_failed": 0,
            "total_scenarios": 0,
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "total_steps": 0,
            "steps_passed": 0,
            "steps_failed": 0,
            "steps_skipped": 0,
            "features_passed_percent": 0,
            "features_failed_percent": 0,
            "scenarios_passed_percent": 0,
            "scenarios_failed_percent": 0
        }
        for idx, feature in enumerate(self.features_storage):
            if len(self.features_storage) == 1:
                global_result['start_time'] = feature.get('start_time')
                global_result['end_time'] = feature.get('end_time')
            elif idx == 0:
                global_result['start_time'] = feature.get('start_time')
            elif idx == len(self.features_storage) - 1:
                global_result['end_time'] = feature.get('end_time')

            if feature.get('status') == "passed":
                global_result['features_passed'] += 1
            else:
                global_result['features_failed'] += 1

            global_result['total_scenarios'] += feature.get('total_scenarios')
            global_result['passed_scenarios'] += feature.get('passed_scenarios')
            global_result['failed_scenarios'] += feature.get('failed_scenarios')

            global_result['total_steps'] += feature.get('total_steps')

            global_result['steps_passed'] += feature.get('steps_passed')
            global_result['steps_failed'] += feature.get('steps_failed')
            global_result['steps_skipped'] += feature.get('steps_skipped')

        global_result[  # noqa
            'scenarios_passed_percent'
        ] = "0" if global_result['passed_scenarios'] == 0 else format_decimal(
            (global_result['passed_scenarios'] * 100) / global_result['total_scenarios'])

        global_result['scenarios_failed_percent'] = "0" if global_result['failed_scenarios'] == 0 else format_decimal(
            (global_result['failed_scenarios'] * 100) / global_result['total_scenarios'])

        global_result['features_passed_percent'] = "0" if global_result['features_passed'] == 0 else format_decimal(
            (global_result['features_passed'] * 100) / global_result['total_features']
        )
        global_result['features_failed_percent'] = "0" if global_result['features_failed'] == 0 else format_decimal(
            (global_result['features_failed'] * 100) / global_result['total_features']
        )

        return global_result

    def add_global_data(self):
        """
        This method add global data for other purposes.
        :return:
        :rtype:
        """
        global_results = self.calculate_global_results()

        return '"global_data":' + json.dumps({
            'keyword': 'global_data',
            'date': datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
            'application': settings.PROJECT_INFO['application'],
            'business_area': settings.PROJECT_INFO['business_area'],
            'entity': settings.PROJECT_INFO['entity'],
            'user_code': settings.PROJECT_INFO['user_code'],
            'environment': settings.PYTALOS_PROFILES['environment'],
            'version': __VERSION__,
            'results': global_results,
            'octane': {
                'server': settings.PYTALOS_OCTANE['server'],
                'username': settings.PROJECT_INFO['user_code'],
                'clientid': settings.PYTALOS_OCTANE['client_id'],
                'secret': settings.PYTALOS_OCTANE['secret'],
                'sharedspace': settings.PYTALOS_OCTANE['shared_space'],
                'workspace': settings.PYTALOS_OCTANE['workspace']
            }
        }, **self.dumps_kwargs)


class CustomParallelFormatter(Formatter):
    """
    This is a custom formatter in order to print console output for parallel execution.
    """
    name = "parallel"
    description = "Formatter for parallel executions"
    driver = ''

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        try:
            self.stream = self.open()
        except FileExistsError:
            traceback.print_exc()

        self.feature_name = ''
        self.scenario_name = ''
        self.background_name = ''
        self.step_name = ''

    def feature(self, feature):
        """
        Called before a feature is executed.
        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        self.feature_name = feature.name
        self.driver = feature.driver.upper()

        line = f"--\t{self.driver}\t-\t{'FEATURE'}\t-\t{self.feature_name}\t-\tSTARTED\n"
        self.stream.write(Fore.MAGENTA + line)

    def background(self, background):
        """
        Called when a (Feature) Background is provided.
        Called after :method:`feature()` is called.
        Called before processing any scenarios or scenario outlines.
        :param background:  Background object (as :class:`behave.model.Background`)
        """
        self.background_name = background.name

    def scenario(self, scenario):
        """
        Called before a scenario is executed (or ScenarioOutline scenarios).
        :param scenario:  Scenario object (as :class:`behave.model.Scenario`)
        """
        self.scenario_name = scenario.name
        line = f"--\t{self.driver}\t-\t{'SCENARIO'}\t-\t{self.feature_name}\t-\t{self.scenario_name}\t-\tSTARTED\n"
        self.stream.write(Fore.YELLOW + line)

    def step(self, step):
        """
        Called before a step is executed (and matched).
        NOTE: Normally called before scenario is executed for all its steps.
        :param step: Step object (as :class:`behave.model.Step`)
        """
        self.step_name = step.name
        status = 'RUNNING'

        line = f"--\t{self.driver}\t-\t{'STEP'}\t-\t{self.feature_name}" \
               f"\t-\t{self.scenario_name}\t-\t{self.step_name}\t-\t{status}\n"

        self.stream.write(Fore.CYAN + line)

    def result(self, step):
        """
        Called after processing a step (when the step result is known).
        :param step:  Step object with result (after being executed/skipped).
        """
        self.step_name = step.name
        status = step.status.__str__().split('.')[1].upper()
        color = Fore.GREEN if status == 'PASSED' else Fore.RED

        line = f"--\t{self.driver}\t-\t{'STEP'}\t-\t{self.feature_name}" \
               f"\t-\t{self.scenario_name}\t-\t{self.step_name}\t-\t{status}\n"

        self.stream.write(color + line)

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        line = f"--\t{self.driver}\t-\t{'FEATURE'}\t-\t{self.feature_name}\t-\tFINISHED\n"

        self.stream.write(Fore.MAGENTA + line)


def update_feature_scenario_data(old_scenario, new_scenario):
    """
    This method updates the data from the old_scenario.
    :param old_scenario:
    :type old_scenario:
    :param new_scenario:
    :type new_scenario:
    :return:
    :rtype:
    """
    try:
        data = {
            "total_steps": new_scenario.total_steps,
            "steps_passed": new_scenario.steps_passed,
            "steps_failed": new_scenario.steps_failed,
            "steps_skipped": new_scenario.steps_skipped,
            "steps_passed_percent": new_scenario.steps_passed_percent,
            "steps_failed_percent": new_scenario.steps_failed_percent,
            "steps_skipped_percent": new_scenario.steps_skipped_percent,
            "start_time": new_scenario.start_time,
            "end_time": new_scenario.end_time,
            "duration": new_scenario.duration
        }
        return old_scenario.update(data)
    except AttributeError as error:
        logger.error(error)


def format_decimal(value):
    """
    This method transform a float/int to a float with 2 decimal places.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"
