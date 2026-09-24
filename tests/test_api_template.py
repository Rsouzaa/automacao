import pytest

from arc.contrib.tools.api_template import create_api_template


def create_profile_structure(project_root):
    for environment in ('dev', 'qa'):
        (project_root / 'settings' / 'profiles' / environment).mkdir(parents=True)


def test_create_api_template_generates_feature_and_profiles(tmp_path):
    create_profile_structure(tmp_path)

    result = create_api_template('Orders API', tmp_path)

    assert result['module_name'] == 'orders_api'
    feature = tmp_path / 'test' / 'features' / 'api' / 'orders_api' / 'health.feature'
    assert feature.is_file()
    assert "${{orders_api:api}}" in feature.read_text(encoding='utf-8')
    assert (tmp_path / 'settings' / 'profiles' / 'dev' / 'orders_api.json').is_file()


def test_create_api_template_does_not_overwrite_existing_system(tmp_path):
    create_profile_structure(tmp_path)
    create_api_template('Orders API', tmp_path)

    with pytest.raises(FileExistsError):
        create_api_template('Orders API', tmp_path)