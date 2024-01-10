# -*- coding: utf-8 -*-
"""
Class and functions of utilities and context support.
"""

import six # NOQA
import re
import logging

from behave.runner import Context as _Context

from arc.core.behave.template_var import get_template_var_value

logger = logging.getLogger(__name__)


class Context(_Context):
    """
        This Context class overrides the original Context class from Behave in order to have additional behaviour in
        Talos BDD
    """
    def execute_steps(self, steps_text):
        """The steps identified in the "steps" text string will be parsed and
        executed in turn just as though they were defined in a feature file.

        If the execute_steps call fails (either through error or failure
        assertion) then the step invoking it will need to catch the resulting
        exceptions.

        :param steps_text:  Text with the Gherkin steps to execute (as string).
        :returns: True, if the steps executed successfully.
        :raises: AssertionError, if a step failure occurs.
        :raises: ValueError, if invoked without a feature context.
        """
        logger.debug("Executing sub steps")
        assert isinstance(steps_text, six.text_type), "Steps must be unicode."
        if not self.feature:
            raise ValueError("execute_steps() called outside of feature")


        # -- PREPARE: Save original context data for current step.
        # Needed if step definition that called this method uses .table/.text
        original_table = getattr(self, "table", None)
        original_text = getattr(self, "text", None)

        self.feature.parser.variant = "steps"
        steps_text = self.__parse_examples(steps_text)
        steps = self.feature.parser.parse_steps(steps_text)
        for step in steps:
            if self._runner.step_registry.find_match(step):
                self.runtime.step.sub_steps.append(step)
                step.parent_step = self.runtime.step

        with self._use_with_behave_mode():
            for step in steps:
                logger.debug(f"Executing sub step {step.name}")
                print(u"\t\t%s %s" % (step.keyword, step.name))
                passed = step.run(self._runner, quiet=True, capture=False)
                if not passed:
                    logger.debug(f"Sub step failed {step.name}")
                    # -- ISSUE #96: Provide more substep info to diagnose problem.
                    step_line = u"%s %s" % (step.keyword, step.name)
                    message = "%s SUB-STEP: %s" % \
                              (step.status.name.upper(), step_line)
                    if step.error_message:
                        message += "\nSubstep info: %s\n" % step.error_message

                    assert False, message
                logger.debug(f"Sub step success {step.name}")

            # -- FINALLY: Restore original context data for current step.
            self.table = original_table
            self.text = original_text
        return True

    def __parse_examples(self, steps_text):
        """
            This method parse the example tables of the scenarios in sub steps.
            Allowing to use template vars in example tables of sub steps.
        :param steps_text:
        :type steps_text:
        """
        regex_table = r"<(.*?)>"
        matchers_profiles = re.findall(regex_table, steps_text)
        for match in matchers_profiles:
            _value = get_template_var_value(self.active_outline[match])
            steps_text = steps_text.replace(f"<{match}>", _value)
            logger.debug(f"Parsed example table {match} with value {_value}")
        return steps_text


class PyTalosContext:
    """
        Utility class for storing Talos core information and configurations within the context.
        """
    """
    Utility class for storing Talos core information and configurations within the context.
    """
    context: None

    def __init__(self, context):
        self.context = context


class RuntimeDatas:
    """
    Utility class for storing run time information within the context.
    """
    context = None

    def __init__(self, context):
        self.context = context


class TestData:
    """
    Utility class for storing test data information within the context.
    """
    context = None

    def __init__(self, context):
        self.context = context
