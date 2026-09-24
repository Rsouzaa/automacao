import json

import pytest

from arc.contrib.tools.system_catalog import register_system


def test_register_system_creates_catalog_without_credentials(tmp_path):
    registered = register_system('Portal Clientes', 'web', 'password', tmp_path)

    catalog = json.loads((tmp_path / 'settings' / 'systems.json').read_text(encoding='utf-8'))
    assert registered['credential_environment_prefix'] == 'AUTOMACAOBDD_PORTAL_CLIENTES'
    assert catalog['systems']['portal_clientes']['authentication'] == 'password'
    assert 'password' not in catalog['systems']['portal_clientes']


def test_register_system_supports_sso_and_api(tmp_path):
    register_system('Intranet', 'web', 'sso', tmp_path)
    register_system('Orders API', 'api', 'password', tmp_path)

    catalog = json.loads((tmp_path / 'settings' / 'systems.json').read_text(encoding='utf-8'))
    assert catalog['systems']['intranet']['authentication'] == 'sso'
    assert catalog['systems']['orders_api']['type'] == 'api'


def test_register_system_rejects_duplicate_and_unsupported_combinations(tmp_path):
    register_system('Portal Clientes', 'web', 'password', tmp_path)

    with pytest.raises(FileExistsError):
        register_system('Portal Clientes', 'web', 'password', tmp_path)
    with pytest.raises(ValueError, match='MFA'):
        register_system('Orders API', 'api', 'mfa', tmp_path)