from arc.core.behave import runner
from arc.core.behave.runner import make_behave_argv
import talos_run


def test_make_behave_argv_builds_common_execution_options():
    arguments = make_behave_argv(
        verbose=True,
        junit=True,
        tags=["@smoke", "@api"],
        conf_properties="chrome",
        allure=True,
        teamcity=True,
    )

    assert " -v" in arguments
    assert " --junit" in arguments
    assert " --tags=@smoke" in arguments
    assert " --tags=@api" in arguments
    assert " -D Config_environment=chrome" in arguments
    assert "allure_behave.formatter:AllureFormatter" in arguments
    assert "behave_teamcity:TeamcityFormatter" in arguments


def test_make_behave_argv_builds_parallel_options():
    arguments = make_behave_argv(
        conf_properties=["chrome", "firefox"],
        parallel="browsers",
        processes=2,
        environment=["qa", "staging"],
        includes=["smoke"],
        excludes=["wip"],
    )

    assert " --browsers chrome,firefox" in arguments
    assert " --parallel browsers" in arguments
    assert " --processes 2" in arguments
    assert " --environment qa,staging" in arguments
    assert " --include smoke" in arguments
    assert " --exclude wip" in arguments


def test_execute_accepts_missing_arguments_and_runs_cleanup(monkeypatch):
    calls = []

    monkeypatch.setattr(runner, 'before_execution', lambda: calls.append('before'))
    monkeypatch.setattr(runner, 'run_sequential', lambda args: calls.append(('sequential', args)) or 0)
    monkeypatch.setattr(runner, 'after_execution', lambda: calls.append('after'))

    result = runner.execute()

    assert result == 0
    assert calls == ['before', ('sequential', ''), 'after']


def test_main_exits_with_execution_result(monkeypatch):
    exit_codes = []

    monkeypatch.setattr(runner, 'execute', lambda args: 3)
    monkeypatch.setattr(runner.sys, 'exit', exit_codes.append)

    runner.main('--tags=@smoke')

    assert exit_codes == [3]


def test_entrypoint_forwards_command_line_arguments(monkeypatch):
    received_arguments = []

    monkeypatch.setattr(talos_run.sys, 'argv', ['talos_run.py', '--tags=@smoke'])
    monkeypatch.setattr(talos_run.runner, 'main', received_arguments.append)

    talos_run.main()

    assert received_arguments == ['--tags=@smoke']