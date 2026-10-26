# SecureShop — Paiement e-commerce simulé avec contrôle d’intégrité

> **Projet académique de sécurité des protocoles** — Aucun paiement réel n'est effectué et aucune carte bancaire réelle ne doit être saisie.

## 1. Membres du groupe

| Nom complet |
|---|
| MALEBA DIYAZOLA SANG PRECIEUX |
| NAKALENGI MBUDA DIEU A VU |

**Établissement :** [Université / faculté]  
**Cours :** [Intitulé du cours]  
**Année académique :** [Année]

## 2. Objectifs

SecureShop est une boutique e-commerce de démonstration développée avec Django. Le projet illustre comment sécuriser un parcours de paiement **simulé** grâce aux mécanismes suivants :

- **HMAC-SHA-256** : vérifier l'intégrité des données d'une transaction (référence, montant et nonce).
- **Nonce anti-rejeu** : associer un identifiant aléatoire unique à chaque transaction et vérifier sa cohérence lors des tests de sécurité.
- **HTTPS** : protéger les échanges réseau lors d'un déploiement correctement configuré avec TLS.
- **Sessions sécurisées** : protéger le parcours client avec les sessions Django, le contrôle d'accès, les jetons CSRF et un jeton de validation du paiement.
- **Reçu numérique** : afficher le résultat et le récapitulatif de la transaction enregistrée.

## 3. Fonctionnalités

- Inscription et connexion des clients ; vérification OTP (validité : 40 secondes, au maximum 3 tentatives).
- Catalogue de produits et panier (ajout, modification de quantité, suppression).
- Paiements **simulés** : M-Pesa, Orange Money, Airtel Money, Visa, Mastercard et autre carte bancaire.
- Résultats possibles : **validé**, **refusé** ou **en attente**.
- Référence unique, montant recalculé côté serveur, signature HMAC-SHA-256 et nonce.
- Protection contre la répétition du formulaire par jeton de session et clé d'idempotence.
- Reçu/résultat de paiement et historique des transactions.
- Administration : gestion des produits et utilisateurs, journaux des transactions et événements de sécurité.
- Laboratoire d'intégrité permettant de démontrer les effets d'une modification du montant, d'une signature falsifiée et d'un rejeu.

**Important :** le simulateur produit un résultat de paiement sans contacter une banque ou un opérateur. Un reçu « validé » ne prouve pas un débit bancaire réel.

## 4. Architecture technique

| Couche | Technologie / composant | Responsabilité |
|---|---|---|
| Interface | HTML, CSS, JavaScript, templates Django | Catalogue, panier, paiement, reçus, administration |
| Serveur | Python, Django | Authentification, sessions, règles métier, validations |
| Données | SQLite (configuration actuelle) | Utilisateurs, produits, transactions, événements de sécurité |
| Sécurité | `payments/security.py` | Génération des nonces, signature et vérification HMAC-SHA-256 |
| Authentification | Application `accounts` | Inscription, OTP, accès client et administrateur |
| Boutique | Application `shop` | Produits et panier |
| Paiements | Application `payments` | Simulation, journalisation, reçus, laboratoire d'intégrité |

### Structure du projet

```text
SecureShop_PROJET_COMPLET/
├── accounts/                  # Comptes, OTP et administration
├── payments/                  # Transactions et sécurité HMAC
│   ├── security.py
│   ├── views.py
│   ├── lab.py
│   └── models.py
├── shop/                      # Catalogue et panier
├── secureshop/                # Configuration Django, URL, WSGI/ASGI
├── templates/                 # Pages HTML
├── static/                    # Ressources statiques
├── media/                     # Images des produits (locales)
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## 5. Protocoles et mécanismes de sécurité

### HMAC-SHA-256

Le serveur calcule une signature HMAC sur les valeurs **référence**, **montant** et **nonce** à l'aide d'une clé secrète `PAYMENT_HMAC_KEY` :

```text
signature = HMAC-SHA256(clé_secrète, JSON([référence, montant, nonce]))
```

La comparaison utilise `hmac.compare_digest`, afin d'éviter une comparaison naïve de chaînes. Une modification d'une donnée signée invalide la signature si l'attaquant ne connaît pas la clé.

### Nonce et anti-rejeu

Chaque transaction reçoit un nonce aléatoire généré avec `secrets.token_hex(24)`. La base impose son unicité. Le laboratoire de sécurité vérifie la correspondance du nonce avec la transaction originale. Le formulaire de paiement dispose également d'un jeton de session et la transaction d'une clé d'idempotence pour limiter les doubles soumissions.

### HTTPS et sessions

Django active les cookies de session `HttpOnly` et `SameSite=Lax` ainsi que la protection CSRF. Les attributs `Secure` des cookies sont activés lorsque `DEBUG=False`. **HTTPS doit être effectivement activé et vérifié sur l'hébergement public** ; le serveur local `runserver` n'offre pas HTTPS par défaut.

### OTP

Les codes OTP expirent après 40 secondes et autorisent au maximum trois tentatives. En local, sans SMTP configuré, le code est affiché dans la console du serveur : cette option n'est **pas adaptée à une démonstration publique** sans dispositif de remise du code au testeur.

## 6. Installation locale

**Prérequis :** Python compatible avec les dépendances du projet, `pip`, Git et un terminal.

```powershell
# Se placer dans le dossier contenant manage.py
cd SecureShop_PROJET_COMPLET

# Créer et activer l'environnement virtuel sous Windows
py -m venv env
.\env\Scripts\Activate.ps1

# Installer les dépendances
python -m pip install -r requirements.txt

# Générer la configuration locale (fichier .env)
python initialiser_config.py

# Initialiser la base
python manage.py migrate
python manage.py seed_products

# Démarrer l'application
python manage.py runserver
```

Si PowerShell bloque l'activation, utiliser `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` uniquement pour la session de terminal en cours, puis relancer l'activation. Autre possibilité : exécuter directement `env\Scripts\python.exe` sans activation.

**Adresse locale :** `http://127.0.0.1:8000/`

**Administration :** `/accounts/admin-login/` (créer d'abord un compte administrateur avec `python manage.py createsuperuser`).

## 7. Configuration

Copier ou générer le fichier `.env` à partir de `.env.example`. Variables prévues :

| Variable | Usage |
|---|---|
| `DJANGO_SECRET_KEY` | Secret Django |
| `PAYMENT_HMAC_KEY` | Clé secrète HMAC (au moins 32 caractères) |
| `DJANGO_DEBUG` | `True` en local, `False` en public |
| `DJANGO_ALLOWED_HOSTS` | Domaines autorisés |
| `EMAIL_HOST_USER` | Compte SMTP pour l'OTP (facultatif en local) |
| `EMAIL_HOST_PASSWORD` | Mot de passe d'application SMTP |

**Ne jamais publier** `.env`, les secrets, les mots de passe, `db.sqlite3` ou l'environnement virtuel `env/` sur GitHub.

## 8. Déploiement web

**Statut : à compléter après mise en ligne et vérification.**

- **Plateforme choisie :** Render
- **URL publique :** https://secureshop-sv04.onrender.com/
- **Dépôt GitHub :** https://github.com/Sang-precieux/SecureShop

Le projet est une application Django **dynamique** : un simple hébergement de pages statiques tel que GitHub Pages ne suffit pas pour faire fonctionner l'authentification, les sessions, la base et les paiements simulés.

Avant la mise en ligne, adapter et vérifier :

1. Le démarrage par serveur WSGI/ASGI adapté à la plateforme (ne pas exposer `runserver`).
2. Les variables d'environnement et `DEBUG=False`.
3. Les domaines autorisés, les origines CSRF et les paramètres HTTPS/proxy.
4. Les fichiers statiques et les images produits.
5. La persistance de la base de données et des médias : **SQLite sur disque éphémère risque de perdre les données au redémarrage** ; prévoir une base persistante, par exemple PostgreSQL, avec adaptation des paramètres Django.
6. Les migrations et la création d'un compte de démonstration.
7. L'envoi des OTP pour les comptes de démonstration : prévoir un SMTP fonctionnel ou une procédure de démonstration sûre.
8. Les tests complets depuis un navigateur privé, sans session préexistante.

La configuration présente dans l'archive est avant tout **locale** ; cette section ne prétend pas que le déploiement public est déjà réalisé.

## 9. Tests à effectuer et à documenter

| Test | Résultat attendu | Résultat observé |
|---|---|---|
| Inscription et OTP | Connexion seulement après OTP valide | [À renseigner] |
| Ajout au panier | Quantités et total cohérents | [À renseigner] |
| Paiement simulé validé | Transaction enregistrée et reçu affiché | [À renseigner] |
| Paiement refusé ou en attente | Page correspondant au statut simulé | [À renseigner] |
| Modification du montant dans le laboratoire | Échec de la vérification d'intégrité | [À renseigner] |
| Signature HMAC falsifiée | Signature rejetée | [À renseigner] |
| Nonce incorrect / rejeu | Contrôle de nonce / rejeu déclenché | [À renseigner] |
| Accès client au journal admin | Accès refusé | [À renseigner] |
| HTTPS en ligne | Connexion HTTPS sans alerte | [À renseigner] |
| Navigation privée | Accueil, connexion, paiement et reçu accessibles | [À renseigner] |

Des tests automatisés existent dans `accounts/tests.py` et `shop/tests.py`. Pour les exécuter :

```powershell
python manage.py test
```

Les résultats du tableau doivent être remplis **après exécution réelle**, sans inventer des validations.

## 10. Captures d'écran

Ajouter les captures dans `docs/captures/`, puis remplacer les chemins ci-dessous si nécessaire :

| Écran | Fichier à ajouter |
|---|---|
| Accueil et catalogue | `docs/captures/01-accueil.png` |
| Panier | `docs/captures/02-panier.png` |
| Formulaire de paiement | `docs/captures/03-paiement.png` |
| Reçu / résultat | `docs/captures/04-recu.png` |
| Laboratoire HMAC | `docs/captures/05-integrite.png` |
| Journal de sécurité | `docs/captures/06-journal-securite.png` |

Exemple d'intégration après ajout des fichiers :

```markdown
![Formulaire de paiement simulé](docs/captures/03-paiement.png)
```

Ne pas afficher de mots de passe, OTP actifs, secrets ou données bancaires réelles dans les captures.

## 11. Identifiants de démonstration

**Compte client :** `[adresse ou identifiant de démonstration]`  
**Mot de passe client :** `[mot de passe de démonstration à créer]`  
**Compte administrateur (si nécessaire) :** `[identifiant de démonstration]`  
**Procédure OTP :** `[expliquer comment le correcteur reçoit le code]`

Créer des comptes **réservés à la démonstration**, avec permissions minimales, sans réutiliser des identifiants personnels. Ne jamais publier de véritables secrets administrateur.

## 12. Limites

- Les paiements sont simulés : **aucun débit réel**, aucune connexion aux API M-Pesa, Orange Money, Airtel ou Visa.
- Le HMAC démontre l'intégrité des données signées ; il ne constitue pas une preuve de paiement bancaire.
- Le laboratoire de sécurité est une démonstration pédagogique et ne remplace pas un audit complet.
- Un déploiement public demande des ajustements supplémentaires de sécurité, de stockage, de gestion des fichiers statiques et de disponibilité des OTP.

## 13. Livrables demandés

Le dépôt doit contenir ce `README.md`, le code source, les dépendances, `.env.example`, les tests et les captures. **Pour la remise finale, fournir uniquement deux liens :**

1. **Site public :** https://secureshop-sv04.onrender.com/
2. **Dépôt GitHub :** https://github.com/Sang-precieux/SecureShop

Vérifier les deux liens en **navigation privée** avant la remise.
