from arc import environment
from arc.core.behave import environment as behave_environment


def test_after_execution_skips_reports_when_json_was_not_created(tmp_path, monkeypatch):
    cleanup_calls = []

    monkeypatch.setattr(environment, 'BASE_DIR', str(tmp_path))
    monkeypatch.setenv('RUN_TYPE', 'sequential')
    monkeypatch.setattr(environment, 'validate_generate_reports', lambda: None)
    monkeypatch.setattr(environment, 'utils_after_execution', lambda: cleanup_calls.append('cleanup'))

    environment.after_execution()

    assert cleanup_calls == ['cleanup']


def test_before_all_continues_when_pytest_assertion_hook_is_incompatible(monkeypatch):
    calls = []

    monkeypatch.setattr(
        behave_environment,
        'install_pytest_asserts',
        lambda: (_ for _ in ()).throw(ImportError('legacy')),
    )
    monkeypatch.setattr(behave_environment, 'utils_before_all', lambda context: calls.append(context))

    context = object()
    behave_environment.before_all(context)

    assert calls == [context]