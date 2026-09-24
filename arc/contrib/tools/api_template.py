"""Generate the starting structure for a new REST API automation."""
from pathlib import Path

from arc.contrib.tools.system_catalog import normalize_system_name


def _write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def create_api_template(system_name, project_root=Path('.')):
    """Create a REST API smoke-test template without overwriting files."""
    module_name = normalize_system_name(system_name)
    project_root = Path(project_root).resolve()
    feature_dir = project_root / 'test' / 'features' / 'api' / module_name
    profile_root = project_root / 'settings' / 'profiles'
    if not profile_root.is_dir():
        raise FileNotFoundError(f'Profiles directory was not found: {profile_root}')
    profile_directories = [path for path in profile_root.iterdir() if path.is_dir()]
    if not profile_directories:
        raise FileNotFoundError(f'No profile directories were found in {profile_root}')

    targets = [feature_dir]
    targets.extend(profile / f'{module_name}.json' for profile in profile_directories)
    existing_targets = [path for path in targets if path.exists()]
    if existing_targets:
        paths = ', '.join(str(path) for path in existing_targets)
        raise FileExistsError(f'Template generation aborted; existing paths: {paths}')

    _write_file(feature_dir / '__init__.py', '')
    _write_file(
        feature_dir / 'health.feature',
        f'''@smoke
Feature: {system_name} API health check

  Scenario: Health endpoint responds successfully
    Given prepare the uri '${{{{{module_name}:api}}}}' request
    And prepare the method 'GET' request
    When send request
    Then verify status code is '200'
''',
    )
    for profile_directory in profile_directories:
        _write_file(
            profile_directory / f'{module_name}.json',
            '{\n  "api": "https://replace-with-the-api-url.example/health"\n}\n',
        )

    return {
        'module_name': module_name,
        'feature_directory': feature_dir,
        'profiles': profile_directories,
    }