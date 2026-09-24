from pathlib import Path

import pytest

from arc.contrib.tools.web_template import create_web_template


def create_project_structure(project_root):
    import_file = project_root / 'test' / 'steps' / 'import_steps.py'
    import_file.parent.mkdir(parents=True)
    import_file.write_text('try:\n    # USER STEPS\n    pass\n', encoding='utf-8')
    for environment in ('dev', 'qa'):
        (project_root / 'settings' / 'profiles' / environment).mkdir(parents=True)


def test_create_web_template_generates_files_profiles_and_steps_import(tmp_path):
    create_project_structure(tmp_path)

    result = create_web_template('Portal Clientes', tmp_path)

    assert result['module_name'] == 'portal_clientes'
    assert (tmp_path / 'test' / 'features' / 'web' / 'portal_clientes' / 'smoke.feature').is_file()
    assert (tmp_path / 'test' / 'helpers' / 'page_objects' / 'portal_clientes' / 'login_page.py').is_file()
    assert (tmp_path / 'test' / 'steps' / 'web' / 'portal_clientes' / 'smoke_steps.py').is_file()
    assert (tmp_path / 'settings' / 'profiles' / 'dev' / 'portal_clientes.json').is_file()
    assert (tmp_path / 'settings' / 'profiles' / 'qa' / 'portal_clientes.json').is_file()
    assert 'from test.steps.web.portal_clientes import smoke_steps' in (
        tmp_path / 'test' / 'steps' / 'import_steps.py'
    ).read_text(encoding='utf-8')


def test_create_web_template_does_not_overwrite_existing_system(tmp_path):
    create_project_structure(tmp_path)
    create_web_template('Portal Clientes', tmp_path)

    with pytest.raises(FileExistsError):
        create_web_template('Portal Clientes', tmp_path)