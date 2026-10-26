"""Crée .env sans aucun secret distribué et respecte un .env utilisateur existant."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent
path = root / '.env'
if not path.exists():
    path.write_text((root / '.env.example').read_text(encoding='utf-8'), encoding='utf-8')

lines = path.read_text(encoding='utf-8').splitlines()
for key in ('DJANGO_SECRET_KEY', 'PAYMENT_HMAC_KEY'):
    has_value = any(line.strip().startswith(key + '=') and line.split('=', 1)[1].strip() for line in lines)
    if not has_value:
        # Remplacer les lignes vides ou ajouter la variable si elle était absente.
        lines = [line for line in lines if not line.strip().startswith(key + '=')]
        lines.append(f'{key}={secrets.token_urlsafe(48)}')
path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Configuration privée prête : fichier .env créé ou complété. Clés non affichées.')
