# PharmaGest

Application web de gestion de pharmacie développée avec Django.

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
- Ventes : panier, FEFO automatique, transaction atomique, prix figé, refus si stock insuffisant ou lot périmé/bloqué
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
- Pas de factures ni de bons de commande/réception en PDF (seuls le reçu de vente et les rapports sont générés)
- Pas de réinitialisation du mot de passe par e-mail
- Sauvegarde déclenchée par commande (à planifier avec cron ou le planificateur de tâches), pas de planification intégrée

## Installation
```bash
git clone https://github.com/ManatsoaTony/PharmaGest.git
cd PharmaGest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed
python manage.py roles
python manage.py runserver
```
Ouvrir ensuite http://127.0.0.1:8000/

## Comptes de test
Après `python manage.py roles` : `pharmacien`, `caissier`, `gestionnaire`, mot de passe `Pharma2026!`.
Le compte administrateur est celui créé avec `createsuperuser`.

## Documentation
- `docs/guide_utilisation.md` : guide d'utilisation
- `docs/merise.md` : dossier de conception (dictionnaire, MCD, MLD, règles de gestion)
- `docs/mcd.png` : modèle conceptuel de données (Merise)
- `docs/mld.png` : schéma relationnel (MLD)
- `docs/classes.png` : diagramme de classes UML généré depuis les modèles

## Sauvegarde et restauration
```bash
python manage.py sauvegarde               # crée backups/pharmagest-AAAAMMJJ-HHMMSS.sqlite3 (+ photos en .zip)
python manage.py sauvegarde --garder 5    # ne conserve que les 5 dernières
python manage.py restaurer backups/pharmagest-AAAAMMJJ-HHMMSS.sqlite3
```
La base actuelle est copiée en `db.avant-restauration` avant toute restauration. Pour une sauvegarde quotidienne, planifier la première commande (cron sous Linux, planificateur de tâches sous Windows).

## Tests
```bash
python manage.py test
```

## Technologies
Python, Django, SQLite, Bootstrap 5, Pillow, ReportLab.