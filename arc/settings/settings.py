# -*- coding: utf-8 -*-
"""
Talos core configuration module.
"""
import os
from pathlib import Path

# Automation resources settings and paths
BASE_PATH = Path(__file__).absolute().parent.parent.parent  # base project path
SETTINGS_PATH = os.path.join(BASE_PATH, 'settings')  # user settings path
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')  # output path
TEST_PATH = os.path.join(BASE_PATH, 'test')  # test folder path
REPORTS_PATH = os.path.join(OUTPUT_PATH, 'reports')  # report folder path
DRIVERS_HOME = os.path.join(SETTINGS_PATH, 'drivers')  # driver folder path
ARC_PATH = os.path.join(BASE_PATH, 'arc')  # arc folder path
RESOURCES_PATH = os.path.join(ARC_PATH, 'resources')  # resources folder path
HELPERS_PATH = os.path.join(TEST_PATH, 'helpers')  # helpers folder path
LOCALE_PATH = os.path.join(BASE_PATH, 'arc/settings/locale')  # locale folder path

# Resources
VS_MIDDLEWARE = 'arc/resources/talos-pcom.vbs'  # visual basic script for host execution path

""" Behave configurations """
# BEHAVE configuration
BEHAVE = {
    'color': True,
    'junit': False,
    'junit_directory': 'output/reports/html',
    'default_format': 'pretty',
    'format': [
        'pretty',
        'plain',
        'progress3',
        'json.pretty',
        'json',
        'rerun',
        'sphinx.steps',
        'steps',
        'steps.doc',
        'steps.usage',
        'tags',
        'tags.location',
    ],
    'show_skipped': False,
    'show_multiline': True,
    'stdout_capture': True,
    'stderr_capture': False,
    'summary': True,
    'outfiles': [
        'output/logs/features_pretty.txt',
        'output/logs/features_plain.txt',
        'output/logs/features_progress.txt',
        'output/reports/report_json_pretty.json',
        'output/reports/report_json.json',
        'output/reports/scenario_failed.txt',
        'output/info/steps_rst',
        'output/info/steps_list.txt',
        'output/info/steps_definition.txt',
        'output/info/steps_usage.txt',
        'output/info/tags_usage.txt',
        'output/info/tags_location.txt',

    ],
    'show_source': True,
    'show_timings': True,
    'verbose': False,
    'more_formatters': {},
    'userdata': {}
}
