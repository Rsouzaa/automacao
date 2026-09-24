# -*- coding: utf-8 -*-
"""
TalosBDD execution file.
You can run this file via the IDE option or via command line.
"""
import sys

from arc.core.behave import runner


def main():
    """TalosBDD main function."""
    runner.main(' '.join(sys.argv[1:]))


if __name__ == '__main__':
    main()

    # runner.main(make_behave_argv(conf_properties='backend', tags=['first_generation']))
    # runner.main(make_behave_argv(conf_properties='chrome', tags=['san_adb']))
