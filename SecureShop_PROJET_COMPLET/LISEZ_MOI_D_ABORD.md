# SecureShop — PROJET DJANGO COMPLET (prototype académique)

**Ce ZIP est un projet Django indépendant**, pas seulement une mise à jour à copier dans l'ancien dossier.
Les fichiers `manage.py`, `secureshop/settings.py`, les modèles, vues, URL, HTML, sécurité HMAC,
administration, templates OTP, scripts Windows, jeu de produits exemples et documentation sont inclus.

## Installation la plus facile (Windows)

1. Décompresser le ZIP dans `Téléchargements` ou `Documents`.
2. Ouvrir le dossier **SecureShop_PROJET_COMPLET**.
3. Double-cliquer sur **INSTALLER_WINDOWS.bat** (ordinateur connecté à Internet pour installer Django).
4. À la fin, double-cliquer sur **DEMARRER_WINDOWS.bat**.
5. Ouvrir dans Chrome : **http://127.0.0.1:8000/**.
6. Pour créer un administrateur, double-cliquer sur **CREER_ADMIN_WINDOWS.bat**.
   Se connecter ensuite sur **http://127.0.0.1:8000/accounts/admin-login/**.

Si Windows bloque les .bat, dans PowerShell à la racine du projet :

```powershell
py -3 -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe initialiser_config.py
.\env\Scripts\python.exe manage.py makemigrations accounts shop payments
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py seed_products
.\env\Scripts\python.exe manage.py runserver
```

## OTP (double authentification)

- **Mode démo immédiatement utilisable** : en l'absence de compte Gmail configuré,
  le code OTP apparaît dans le terminal où `runserver` fonctionne, pas dans la boîte Gmail.
  Le code reste valable **40 secondes**, avec **3 tentatives**.
- **Mode Gmail** : ouvrir `.env` (NE PAS partager), renseigner `EMAIL_HOST_USER` et
  `EMAIL_HOST_PASSWORD` avec le mot de passe d'application Google, puis redémarrer le serveur.
  L'adresse Gmail dans `.env` et la clef secrète ne sont jamais incluses dans l'archive.
- Une nouvelle inscription se fait avec une adresse e-mail ; c'est aussi l'identifiant de connexion.
  Pour un superutilisateur, entrer son *username* choisi à la création si différent d'un e-mail.

## Parcours de démonstration

- **Client** : Accueil → Produits → Ajouter au panier → badge rouge → Panier (+, −, Supprimer) →
  Paiement → choisir M-Pesa, Orange Money, Airtel Money ou carte **fictifs** →
  résultat validé, refusé ou en attente → reçu.
- **Admin** : `/accounts/admin-login/` → OTP → tableau de bord →
  journaux des paiements/sécurité → laboratoire d'intégrité → utilisateurs et catalogue.
- L'URL `/admin/` (administration Django native) redirige vers l'entrée OTP personnalisée.
- L'OTP administrateur est exigé pour les trois journaux et le tableau de bord,
  pas seulement le statut `is_staff`.

## Il s'agit d'une NOUVELLE base, pas de l'ancienne

Pour protéger ton travail antérieur, **ne remplace pas ton dossier original**
`SecureShop_OTP_40_secondes` et **ne copie pas `db.sqlite3` de l'ancien projet vers le nouveau**.
Le nouveau projet crée automatiquement une nouvelle base de données et six produits exemples.
L'archive n'inclut pas les anciens clients/paiements puisqu'ils n'ont pas été fournis dans la conversation.
Un transfert de ces données serait une étape séparée après comparaison des modèles.

## Limites et sécurité

- Projet de TP **sans paiement réel** : aucun opérateur ni banque connecté,
  aucun argent débité, aucune collecte de vrais numéros de carte.
- Ne pas utiliser en production tel quel : il reste à mettre en place TLS/HTTPS,
  `DEBUG=False`, limitation renforcée des demandes OTP, supervision et tests approfondis.
- Le calcul HMAC montre l'intégrité des données du démonstrateur ; il ne prouve pas un débit réel.
- `.env`, `db.sqlite3` et l'environnement virtuel `env/` sont exclus de Git via `.gitignore`.
- Pour GitHub : publier **le code uniquement** avec `.env.example`, jamais le mot de passe Gmail.

## Dépannage

- `python n'est pas reconnu` : installer Python 3.11+ et cocher **Add Python to PATH**.
- `ModuleNotFoundError: django` : lancer `INSTALLER_WINDOWS.bat` avec Internet actif.
- `no such table` : relancer `INSTALLER_WINDOWS.bat` (migrations automatiques).
- Pas de mail Gmail ? Contrôler `.env` et redémarrer le serveur, ou rester en mode OTP terminal.
- Pour relancer l'app après arrêt : **DEMARRER_WINDOWS.bat**. Ne pas recommencer l'installation.
