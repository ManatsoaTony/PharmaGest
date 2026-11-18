# PharmaGest

Application web de gestion de pharmacie développée avec Django.
Elle couvre le cycle complet : approvisionnement auprès des fournisseurs, suivi du stock par lots et dates de péremption, vente à la caisse, retours, rapports PDF et traçabilité des opérations.

## Contenu de l'archive

| Élément | Rôle |
|---|---|
| `manage.py` | Point d'entrée des commandes Django |
| `config/` | Réglages et adresses du projet |
| `medicaments/`, `fournisseurs/`, `clients/`, `achats/`, `stock/`, `ventes/`, `rapports/`, `utilisateurs/` | Les applications (modèles, vues, formulaires) |
| `templates/` | Pages HTML (Bootstrap 5) |
| `db.sqlite3` | Base de données déjà remplie avec des données fictives |
| `media/` | Photos des médicaments |
| `docs/` | Guide d'utilisation et dossier de conception |
| `requirements.txt` | Liste des bibliothèques Python à installer |

## Installation et lancement

**Prérequis :** Python 3.12 ou plus récent (vérifier avec `python --version`).

**1. Décompresser l'archive**, puis ouvrir un terminal dans le dossier `PharmaGest` (celui qui contient `manage.py`).

**2. Créer un environnement virtuel.** Il isole les bibliothèques du projet du reste de l'ordinateur :
```bash
python -m venv .venv
```

**3. Activer l'environnement virtuel :**
```bash
source .venv/bin/activate        # Linux et macOS
.venv\Scripts\activate           # Windows
```
Le terminal affiche alors `(.venv)` au début de la ligne.

**4. Installer les bibliothèques** (Django, Pillow pour les photos, ReportLab pour les PDF) :
```bash
pip install -r requirements.txt
```

**5. Lancer le serveur :**
```bash
python manage.py runserver
```

**6. Ouvrir le navigateur** à l'adresse http://127.0.0.1:8000/ : la page de connexion s'affiche. Pour arrêter le serveur, faire Ctrl+C dans le terminal.

La base de données et les photos sont déjà dans l'archive : il n'y a ni migration, ni données à créer pour tester.

## Comptes de test

| Compte | Mot de passe | Ce qu'il peut faire |
|---|---|---|
| `pharmacien` | `Pharma2026!` | Tout : médicaments, stock, inventaire, achats, ventes, retours, rapports, journal d'audit |
| `gestionnaire` | `Pharma2026!` | Médicaments, fournisseurs, achats, réceptions, inventaire, rapports de stock, de péremptions et d'achats |
| `caissier` | `Pharma2026!` | Caisse, ventes, reçus, retours |

Un utilisateur qui tente une action hors de ses droits voit la page « Accès refusé ».

Pour utiliser l'administration Django (`/admin/`), créer un compte administrateur :
```bash
python manage.py createsuperuser
```

## Parcours de test conseillé (10 minutes)

1. Se connecter en `pharmacien` et regarder le **tableau de bord** : ventes, alertes de stock, péremptions, boutons PDF.
2. Ouvrir un **médicament** avec sa photo, puis tester la recherche et le filtre par catégorie.
3. **Achats** : créer une commande, la valider, puis réceptionner une partie. Le stock n'augmente qu'à la réception.
4. **Caisse** : vendre un médicament à un client, puis ouvrir le reçu PDF. Essayer une quantité supérieure au stock : la vente est refusée.
5. Sur un reçu, faire un **retour** avec un motif.
6. **Stock** : consulter les lots, les mouvements, et faire un **inventaire** (saisir une quantité comptée différente).
7. Revenir au tableau de bord et ouvrir le **journal d'audit** : toutes ces opérations y apparaissent.
8. Se connecter en `caissier` : la réception de stock, l'inventaire et le journal affichent « Accès refusé ».

## Fonctionnalités réalisées
- Authentification, toutes les pages protégées
- Rôles : Pharmacien, Caissier, Gestionnaire de stock
- Médicaments : CRUD, photo, recherche, filtre par catégorie, pagination, archivage
- Catégories : ajout, liste, modification
- Fournisseurs : CRUD, recherche, désactivation
- Clients : CRUD, recherche, historique des ventes, client facultatif (vente comptoir possible)
- Achats : commandes (brouillon, commandée, partiellement réceptionnée, entièrement réceptionnée, annulée), réception partielle par lot, stock modifié uniquement à la réception
- Stock : lots, péremptions, mouvements tracés, alertes (rupture, stock faible, péremption proche, lots périmés)
- Réception de marchandise directe (transaction atomique)
- Ventes : panier, FEFO automatique (le lot qui périme en premier part en premier), transaction atomique, prix figé, refus si stock insuffisant ou lot périmé ou bloqué
- Retours de vente : motif obligatoire, remise en stock conditionnelle, vente d'origine conservée
- Reçu de vente PDF (ReportLab)
- Rapports PDF : stock, produits périmés ou proches de la péremption, ventes, achats
- Inventaire physique : quantités comptées, écarts transformés en corrections tracées
- Journal d'audit : ventes, retours, commandes, réceptions et inventaires (qui, quoi, quand), consultable par le pharmacien et en lecture seule dans l'administration
- Sauvegarde et restauration de la base : commandes `sauvegarde` et `restaurer`
- Tableau de bord
- Tests automatisés (24) et données fictives (`seed`)

## Limites actuelles
- Pas de paiement électronique vérifié (le mode de paiement est enregistré, sans table de paiements séparée)
- Pas de factures ni de bons de commande et de réception en PDF (seuls le reçu de vente et les rapports sont générés)
- Pas de réinitialisation du mot de passe par e-mail
- Sauvegarde déclenchée par commande (à planifier avec cron ou le planificateur de tâches), pas de planification intégrée
- Réglages de développement (`DEBUG` actif, clé secrète dans `config/settings.py`) : à changer avant une mise en production

## Documentation
- `docs/guide_utilisation.md` : guide d'utilisation, écran par écran
- `docs/merise.md` : dossier de conception (dictionnaire de données, MCD, MLD, règles de gestion)
- `docs/mcd.png` : modèle conceptuel de données (Merise)
- `docs/mld.png` : schéma relationnel (MLD)
- `docs/classes.png` : diagramme de classes UML généré depuis les modèles

## Tests automatisés
```bash
python manage.py test
```
Résultat attendu : `Ran 24 tests ... OK` (une quinzaine de secondes, plus longtemps sur une machine lente). Les tests couvrent les permissions, les ventes, les achats, les retours, l'inventaire et les rapports.

## Sauvegarde et restauration
```bash
python manage.py sauvegarde               # crée backups/pharmagest-AAAAMMJJ-HHMMSS.sqlite3 (et les photos en .zip)
python manage.py sauvegarde --garder 5    # ne conserve que les 5 dernières sauvegardes
python manage.py restaurer backups/pharmagest-AAAAMMJJ-HHMMSS.sqlite3
```
Avant toute restauration, la base actuelle est copiée en `db.avant-restauration`. Pour une sauvegarde quotidienne, planifier la première commande (cron sous Linux, planificateur de tâches sous Windows).

## Repartir d'une base vide (facultatif)
Supprimer `db.sqlite3`, puis :
```bash
python manage.py migrate        # crée les tables
python manage.py createsuperuser
python manage.py seed           # médicaments, fournisseurs et stock fictifs
python manage.py roles          # groupes et comptes pharmacien, caissier, gestionnaire
```

## Technologies
Python, Django, SQLite, Bootstrap 5, Pillow, ReportLab.