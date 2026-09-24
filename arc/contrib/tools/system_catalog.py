"""Versioned registry for systems automated by AutomacaoBDD."""
import json
import re
import unicodedata
from pathlib import Path


SYSTEM_TYPES = {'web', 'api'}
AUTH_TYPES = {'password', 'sso', 'mfa'}


def normalize_system_name(system_name):
    """Convert a display name into a stable system identifier."""
    normalized = unicodedata.normalize('NFKD', system_name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii').lower()
    identifier = re.sub(r'[^a-z0-9]+', '_', ascii_name).strip('_')
    if not identifier or identifier[0].isdigit():
        raise ValueError('System name must start with a letter and contain letters or numbers.')
    return identifier


def register_system(system_name, system_type, auth_type, project_root=Path('.')):
    """Register a system without storing secrets in the repository."""
    system_type = system_type.lower()
    auth_type = auth_type.lower()
    if system_type not in SYSTEM_TYPES:
        raise ValueError(f"Unsupported system type: {system_type}. Choose from {sorted(SYSTEM_TYPES)}.")
    if auth_type not in AUTH_TYPES:
        raise ValueError(f"Unsupported authentication type: {auth_type}. Choose from {sorted(AUTH_TYPES)}.")
    if system_type == 'api' and auth_type == 'mfa':
        raise ValueError('MFA is not supported for API registrations; use a service token or OAuth client flow.')

    identifier = normalize_system_name(system_name)
    catalog_path = Path(project_root).resolve() / 'settings' / 'systems.json'
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog = {'systems': {}}
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
        catalog.setdefault('systems', {})
    if identifier in catalog['systems']:
        raise FileExistsError(f"System '{identifier}' is already registered.")

    environment_prefix = f'AUTOMACAOBDD_{identifier.upper()}'
    catalog['systems'][identifier] = {
        'name': system_name,
        'type': system_type,
        'authentication': auth_type,
        'credential_environment_prefix': environment_prefix,
    }
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return catalog['systems'][identifier]