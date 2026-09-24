"""Generate the starting structure for a new web automation."""
import re
import unicodedata
from pathlib import Path


def _module_name(system_name):
    normalized = unicodedata.normalize('NFKD', system_name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii').lower()
    module_name = re.sub(r'[^a-z0-9]+', '_', ascii_name).strip('_')
    if not module_name or module_name[0].isdigit():
        raise ValueError('System name must start with a letter and contain letters or numbers.')
    return module_name


def _write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def _ensure_package(path):
    path.mkdir(parents=True, exist_ok=True)
    init_file = path / '__init__.py'
    if not init_file.exists():
        init_file.write_text('', encoding='utf-8')


def _register_steps(import_file, module_path):
    import_line = f'    from {module_path} import smoke_steps\n'
    content = import_file.read_text(encoding='utf-8')
    if import_line in content:
        return

    marker = '    # USER STEPS\n'
    if marker not in content:
        raise ValueError(f'Unable to register steps: marker not found in {import_file}.')
    import_file.write_text(content.replace(marker, marker + import_line), encoding='utf-8')


def create_web_template(system_name, project_root=Path('.')):
    """Create a Web smoke-test template without overwriting existing files.

    Returns a dictionary containing the module name and generated file paths.
    """
    module_name = _module_name(system_name)
    project_root = Path(project_root).resolve()
    test_root = project_root / 'test'
    import_file = test_root / 'steps' / 'import_steps.py'
    if not import_file.is_file():
        raise FileNotFoundError(f'Steps import file was not found: {import_file}')

    feature_dir = test_root / 'features' / 'web' / module_name
    steps_dir = test_root / 'steps' / 'web' / module_name
    page_object_dir = test_root / 'helpers' / 'page_objects' / module_name
    profile_root = project_root / 'settings' / 'profiles'
    if not profile_root.is_dir():
        raise FileNotFoundError(f'Profiles directory was not found: {profile_root}')
    profile_directories = [path for path in profile_root.iterdir() if path.is_dir()]
    if not profile_directories:
        raise FileNotFoundError(f'No profile directories were found in {profile_root}')

    targets = [feature_dir, steps_dir, page_object_dir]
    targets.extend(profile / f'{module_name}.json' for profile in profile_directories)
    existing_targets = [path for path in targets if path.exists()]
    if existing_targets:
        paths = ', '.join(str(path) for path in existing_targets)
        raise FileExistsError(f'Template generation aborted; existing paths: {paths}')

    class_name = ''.join(part.capitalize() for part in module_name.split('_')) + 'LoginPage'
    _write_file(feature_dir / '__init__.py', '')
    _write_file(
        feature_dir / 'smoke.feature',
        f'''@smoke
Feature: {system_name} smoke test

  Scenario: Authenticate successfully
    Given access to the web application '${{{{{module_name}:web}}}}'
    When I sign in to {system_name}
    Then I should see the {system_name} dashboard
''',
    )
    _ensure_package(page_object_dir.parent)
    _write_file(page_object_dir / '__init__.py', '')
    _write_file(
        page_object_dir / 'login_page.py',
        f'''from selenium.webdriver.common.by import By

from arc.page_elements import Button, InputText, Text
from arc.page_objects.page_object import PageObject


class {class_name}(PageObject):
    def init_page_elements(self):
        self.username = InputText(By.ID, 'TODO_USERNAME_SELECTOR', wait=True)
        self.password = InputText(By.ID, 'TODO_PASSWORD_SELECTOR', wait=True)
        self.submit = Button(By.ID, 'TODO_SUBMIT_SELECTOR', wait=True)
        self.dashboard = Text(By.ID, 'TODO_DASHBOARD_SELECTOR', wait=True)
''',
    )
    _ensure_package(steps_dir.parent)
    _write_file(steps_dir / '__init__.py', '')
    _write_file(
        steps_dir / 'smoke_steps.py',
        f'''import os

from behave import step

from arc.contrib.web import login
from test.helpers.page_objects.{module_name}.login_page import {class_name}


@step('I sign in to {system_name}')
def sign_in(context):
    page = {class_name}(context)
    login(
        page.username,
        page.password,
        page.submit,
        os.environ['AUTOMACAOBDD_{module_name.upper()}_USERNAME'],
        os.environ['AUTOMACAOBDD_{module_name.upper()}_PASSWORD'],
    )


@step('I should see the {system_name} dashboard')
def see_dashboard(context):
    page = {class_name}(context)
    page.dashboard.wait_until_visible()
''',
    )

    for profile_directory in profile_directories:
        _write_file(
            profile_directory / f'{module_name}.json',
            '{\n  "web": "https://replace-with-the-system-url.example"\n}\n',
        )

    _register_steps(import_file, f'test.steps.web.{module_name}')
    return {
        'module_name': module_name,
        'feature_directory': feature_dir,
        'steps_directory': steps_dir,
        'page_object_directory': page_object_dir,
        'profiles': profile_directories,
    }