# -*- coding: utf-8 -*-
"""
Module for generating HTML from XML file.
"""
import logging
import os

from junit2htmlreport import runner as junit2html_runner

from arc.settings import settings

logger = logging.getLogger(__name__)

REPORTS_HOME = os.path.join(settings.OUTPUT_PATH, 'reports/html') + os.sep


def make_html_reports(path=REPORTS_HOME):
    """
    It converts junit reports into html report and return output paths
    :param path:
    :return:
    """
    if os.path.isdir(path):
        xml_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-4:] == '.xml']
        output = []
        for r in xml_list:
            _file = path + r
            new_file = path + r[:-4] + '.html'
            junit2html_runner.run([_file, new_file])
            output.append(new_file)

        logger.debug(f'Simple HTML generated in: {output}')
        return output

    else:
        os.stat(path)
        new_path = path[:-4] + '.html'
        junit2html_runner.run([path, new_path])
        logger.debug(f'Simple HTML generated in: {new_path}')
        return new_path
