# PharmaGest

Application web de gestion de pharmacie développée avec Django.

## Fonctionnalités réalisées
- Authentification, toutes les pages protégées
- Rôles : Pharmacien, Caissier, Gestionnaire de stock (comptes de démo via `python manage.py roles`, mot de passe `Pharma2026!`)
- Médicaments : CRUD, photo, recherche, filtre par catégorie, pagination, archivage
- Catégories : ajout, liste, modification
- Fournisseurs : CRUD, recherche, désactivation
- Stock : lots, péremptions, mouvements tracés, alertes (rupture, stock faible, péremption proche, lots périmés)
- Réception de marchandise (transaction atomique)
- Ventes : panier, FEFO automatique, transaction atomique, prix figé, refus si stock insuffisant ou lot périmé/bloqué
- Reçu de vente PDF (ReportLab)
- Tableau de bord
- Tests automatisés (12) et données fictives (`seed`)
- Retours de vente : motif obligatoire, remise en stock conditionnelle, vente d'origine conservée

## Limites actuelles (non réalisées)
- Module Achats complet (commandes, statuts) : seule la réception directe existe
- Retours et annulations de vente
- Gestion des clients
- Rapports PDF (stock, ventes, achats), inventaire physique, journal d'audit
- Sauvegarde automatique de la base

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

## Tests
```bash
python manage.py test
```

## Technologies
Python, Django, SQLite, Bootstrap 5, Pillow, ReportLab.