"""Validate the public URL used by local browser checks."""
import ipaddress
from urllib.parse import urlsplit


def validate_target_url(value):
    if not isinstance(value, str):
        raise ValueError('Informe uma URL.')
    url = value.strip()
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('Informe uma URL completa com http:// ou https://.')
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port not in (None, 80, 443):
        raise ValueError('Remova credenciais, parâmetros e portas não padrão da URL.')
    host = parsed.hostname.lower()
    if host == 'localhost' or host.endswith(('.local', '.internal', '.localhost')):
        raise ValueError('Informe um domínio público.')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if '.' not in host:
            raise ValueError('Informe um domínio público.') from None
    else:
        if not address.is_global:
            raise ValueError('Endereços privados não são aceitos.')
    return url
