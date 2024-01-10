# -*- coding: utf-8 -*-

"""
Accessibility Generic Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the evidence files.

List of steps:
######################################################################################################################
## Actions Steps:
the current page should be audited for accessibility
the current page must be free of accessibility errors
the current page must have only <number> accessibility errors
"""
from behave import step, use_step_matcher

from arc.contrib.accessibility import axe_utils
from arc.contrib.accessibility.axe_utils import evidence_accessibility_violations
from arc.contrib.accessibility.axe_wrapper import AxeWrapper

use_step_matcher("re")

TITLE = 'Accessibility Results'


@step(u"the current page should be audited for accessibility")
def the_current_page_should_be_audited_for_accessibility(context):
    """
    This step performs an accessibility audit analysis on the current page.
    In case of violation of any accessibility rule, it does not return an exception so the step does not fail.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page should be audited for accessibility
    :
    :tag Accessibility Steps:
    :param context:
    """
    title = context.driver.title
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    _, file_name = axe_utils.write_results(results, title)

    context.func.evidences.add_custom_table(
        TITLE,
        inapplicable=len(results['inapplicable']),
        incomplete=len(results['incomplete']),
        passes=len(results['passes']),
        violations=len(results['violations']),
        details=file_name
    )


@step(u"the current page must be free of accessibility errors")
def the_current_page_must_be_free_of_accessibility_errors(context):
    """
    This step performs an accessibility audit analysis on the current page.
    This step fails the test in case of any violation of any Accessibility rule.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page must be free of accessibility errors
    :
    :tag Accessibility Steps:
    :param context:
    """
    title = context.driver.title  # noqa
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    _, file_name = axe_utils.write_results(results, title)

    violations = results['violations']
    current = len(violations)
    expected = 0
    error_msg = f"Found {len(violations)} accessibility violations"
    result = expected == current

    context.func.evidences.add_unit_table(
        TITLE,
        f"Violations",
        current,
        expected,
        result,
        error_msg=error_msg,
        details=file_name

    )

    evidence_accessibility_violations(context, violations)
    assert result, axe_utils.report(violations)


@step(u"the current page must have only '(?P<number>.+)' accessibility errors")
def the_current_page_must_have_only_num_accessibility_errors(context, number):
    """
    This step performs an accessibility audit analysis on the current page.
    This step fails in the event that the number of violations of accessibility rules is equal to the number
    passed by parameter.
    It generates the necessary evidence in the evidence documents.
    :example
        Then the current page must have only '3' accessibility errors
    :
    :tag Accessibility Steps:
    :param context:
    :param number:
    """
    title = context.driver.title  # noqa
    axe = AxeWrapper(context.driver)
    axe.inject()
    results = axe.run()
    _, file_name = axe_utils.write_results(results, title)

    violations = results['violations']
    current = len(violations)
    expected = int(number)
    error_msg = f"Found {len(violations)} accessibility violations"
    result = expected == current

    context.func.evidences.add_unit_table(
        'Accessibility Results',
        f"Violations",
        current,
        expected,
        result,
        error_msg=error_msg,
        details=file_name
    )

    if result is False:
        evidence_accessibility_violations(context, violations)

    assert result, axe_utils.report(violations)
