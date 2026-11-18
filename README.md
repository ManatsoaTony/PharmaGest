# PharmaGest

Application web de gestion de pharmacie développée avec Django.

## Fonctionnalités réalisées
- Authentification, toutes les pages protégées
- Rôles : Pharmacien, Caissier, Gestionnaire de stock (comptes de démo via `python manage.py roles`, mot de passe `Pharma2026!`)
- Médicaments : CRUD, photo, recherche, filtre par catégorie, pagination, archivage
- Catégories : ajout, liste, modification
- Fournisseurs : CRUD, recherche, désactivation
- Achats : commandes (brouillon, commandée, partiellement réceptionnée, entièrement réceptionnée, annulée), réception partielle par lot, stock modifié uniquement à la réception
- Stock : lots, péremptions, mouvements tracés, alertes (rupture, stock faible, péremption proche, lots périmés)
- Réception de marchandise directe (transaction atomique)
- Ventes : panier, FEFO automatique, transaction atomique, prix figé, refus si stock insuffisant ou lot périmé/bloqué
- Retours de vente : motif obligatoire, remise en stock conditionnelle, vente d'origine conservée
- Reçu de vente PDF (ReportLab)
- Tableau de bord
- Tests automatisés (19) et données fictives (`seed`)

## Limites actuelles (non réalisées)
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