# Guide d'utilisation - PharmaGest

## 1. Connexion
Ouvrir `http://127.0.0.1:8000/` : la page de connexion s'affiche.

| Compte | Mot de passe | Droits |
|---|---|---|
| pharmacien | Pharma2026! | Médicaments, stock, inventaire, achats, ventes, retours, rapports, journal d'audit |
| gestionnaire | Pharma2026! | Médicaments, fournisseurs, achats, réceptions, rapports stock et péremptions |
| caissier | Pharma2026! | Caisse, ventes, reçus, retours |
| (superuser) | défini à l'installation | Tout, plus l'administration |

Un utilisateur sans le droit voit la page « Accès refusé ».

## 2. Médicaments et catégories
- **Catégories** : menu « Catégories » > « + Ajouter ». Créer les catégories avant les médicaments.
- **Médicaments** : liste d'accueil > « + Ajouter » : nom, catégorie, forme, dosage, prix d'achat et de vente, seuil d'alerte, photo (JPG ou PNG, 2 Mo maximum).
- Recherche par nom ou code-barres, filtre par catégorie, pagination.
- **Archiver** un médicament le retire des ventes sans effacer l'historique.

## 3. Fournisseurs
Menu « Fournisseurs » : ajout, modification, recherche, désactivation (l'historique est conservé).

## 4. Clients
Menu « Clients » : ajout, modification, recherche, historique des ventes. À la caisse, le client est facultatif (« Client comptoir »).

## 5. Achats (commandes)
1. Menu « Achats » > « + Nouvelle commande » : choisir le fournisseur (statut **Brouillon**).
2. Ajouter les médicaments, quantités et prix, puis « Valider la commande » (statut **Commandée**). Le stock n'est pas modifié.
3. « Réceptionner » : saisir quantité, numéro de lot et date de péremption. Le stock augmente. Une réception partielle donne le statut **Partiellement réceptionnée**, la dernière réception **Entièrement réceptionnée**.
4. Une commande peut être annulée tant qu'elle n'est pas réceptionnée.

## 6. Stock
Menu « Stock » : quantité disponible par médicament et alertes (rupture, stock faible, péremption sous 30 jours, lots périmés).
- « Lots » : détail des lots et états.
- « Mouvements » : historique des entrées, sorties et retours avec auteur et date.
- « + Réception » : entrée directe de marchandise.
- « Inventaire » (pharmacien, gestionnaire) : saisir la quantité réellement comptée par lot ; laisser vide un lot non compté. Chaque écart met à jour le stock et crée une correction tracée (type « Correction d'inventaire »).

Les lots périmés ou bloqués ne sont jamais vendus. La vente utilise d'abord le lot dont la péremption est la plus proche (FEFO).

## 7. Caisse et ventes
1. Menu « Caisse » : choisir un médicament, la quantité, « Ajouter au panier ».
2. Choisir le client (facultatif) et le mode de paiement, « Valider la vente ».
3. Le reçu s'affiche : « Imprimer » ou « Reçu PDF ».
4. Refus si la quantité est nulle ou dépasse le stock disponible.

## 8. Retours de vente
Ouvrir un reçu (Caisse > Historique) > « Retour » sur la ligne : quantité, motif obligatoire, case « remettre en stock » si le produit est intact. La vente d'origine est conservée.

## 9. Tableau de bord et rapports PDF
Ventes du jour et des 7 derniers jours, médicaments actifs, ruptures, stocks faibles, péremptions, produits les plus vendus, dernières ventes.
Boutons « PDF Stock », « PDF Péremptions » et « PDF Achats » (pharmacien, gestionnaire) et « PDF Ventes » (pharmacien).
Bouton « Journal d'audit » (pharmacien) : liste des 200 dernières opérations sensibles (ventes, retours, commandes, réceptions, inventaires) avec auteur et date.

## 10. Sauvegarde et restauration
En ligne de commande, dans le dossier du projet :
- `python manage.py sauvegarde` : copie la base (et les photos) dans `backups/`.
- `python manage.py restaurer <fichier.sqlite3>` : restaure la base depuis une sauvegarde.

## 11. Administration
`/admin/` (superuser) : gestion des comptes, groupes et données. Le journal d'audit y est consultable en lecture seule.