"""Local-only, allowlisted browser test execution."""
import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dashboard.report_service import ROOT_PATH, load_report
from target_validation import validate_target_url

SUITES = frozenset({'url_smoke', 'shopee_pages', 'shopee_panel',
                   'shopee_sales', 'shopee_stock', 'shopee_investments'})


def _now():
    return datetime.now(timezone.utc).isoformat()


class LocalRunManager:
    def __init__(self, report_path):
        self.report_path = Path(report_path)
        self._lock = threading.Lock()
        self._thread = None
        self._state = {'status': 'idle', 'message': 'Nenhum teste iniciado.'}

    def snapshot(self):
        with self._lock:
            return self._state.copy()

    def start(self, target_url, expected_text='', show_browser=False, suite='url_smoke'):
        target_url = validate_target_url(target_url)
        if not isinstance(expected_text, str) or len(expected_text) > 120:
            raise ValueError('O texto esperado deve ter até 120 caracteres.')
        if not isinstance(show_browser, bool) or not isinstance(suite, str) or suite not in SUITES:
            raise ValueError('Selecione uma suíte e uma opção de navegador válidas.')
        with self._lock:
            if self._state['status'] == 'running':
                raise RuntimeError('Já existe um teste em andamento.')
            self._state = {'status': 'running', 'run_id': uuid4().hex, 'suite': suite,
                           'started_at': _now(), 'message': 'Abrindo o Chrome…'}
            self._thread = threading.Thread(target=self._execute,
                                            args=(target_url, expected_text, show_browser, suite), daemon=True)
            self._thread.start()
            return self._state.copy()

    def _execute(self, target_url, expected_text, show_browser, suite):
        result = {'status': 'failed', 'message': 'Não foi possível concluir o teste.'}
        try:
            if self.report_path.is_file():
                history = self.report_path.parent / 'history'
                history.mkdir(parents=True, exist_ok=True)
                self.report_path.replace(history / f'{self.report_path.stem}-{uuid4().hex}.json')
            environment = os.environ.copy()
            environment['AUTOMACAO_TARGET_URL'] = target_url
            if expected_text and suite == 'url_smoke':
                environment['AUTOMACAO_EXPECTED_TEXT'] = expected_text.strip()
            else:
                environment.pop('AUTOMACAO_EXPECTED_TEXT', None)
            command = [sys.executable, str(ROOT_PATH / 'talos_run.py'), '--tags', f'@{suite}',
                       '-D', f'Config_environment={"chrome" if show_browser else "chrome-ci"}', '--no-alm']
            completed = subprocess.run(command, cwd=ROOT_PATH, env=environment, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace',
                                       timeout=300, check=False)
            report = load_report(self.report_path) if self.report_path.is_file() else None
            scenarios = report['summary']['scenarios'] if report else 0
            expected = 4 if suite == 'shopee_pages' else 1
            passed = (completed.returncode == 0 and scenarios == expected and
                      report['summary']['passed'] == expected and report['summary']['failed'] == 0)
            result = {'status': 'passed' if passed else 'failed', 'scenarios': scenarios,
                      'exit_code': completed.returncode,
                      'message': 'Cenários aprovados.' if passed else 'Teste falhou. Confira a saída abaixo.',
                      'log_tail': (completed.stdout or '')[-4000:]}
        except subprocess.TimeoutExpired:
            result['message'] = 'O teste excedeu 5 minutos.'
        except Exception as error:
            result['message'] = f'Erro ao executar: {type(error).__name__}: {error}'
        finally:
            with self._lock:
                self._state.update(result)
                self._state['finished_at'] = _now()
