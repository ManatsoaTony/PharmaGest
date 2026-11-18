# Guide d'utilisation - PharmaGest

## 1. Connexion
Ouvrir `http://127.0.0.1:8000/` : la page de connexion s'affiche.

| Compte | Mot de passe | Droits |
|---|---|---|
| pharmacien | Pharma2026! | Médicaments, stock, achats, ventes, retours |
| gestionnaire | Pharma2026! | Médicaments, fournisseurs, achats, réceptions |
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

## 4. Achats (commandes)
1. Menu « Achats » > « + Nouvelle commande » : choisir le fournisseur (statut **Brouillon**).
2. Ajouter les médicaments, quantités et prix, puis « Valider la commande » (statut **Commandée**). Le stock n'est pas modifié.
3. « Réceptionner » : saisir quantité, numéro de lot et date de péremption. Le stock augmente. Une réception partielle donne le statut **Partiellement réceptionnée**, la dernière réception **Entièrement réceptionnée**.
4. Une commande peut être annulée tant qu'elle n'est pas réceptionnée.

## 5. Stock
Menu « Stock » : quantité disponible par médicament et alertes (rupture, stock faible, péremption sous 30 jours, lots périmés).
- « Lots » : détail des lots et états.
- « Mouvements » : historique de toutes les entrées, sorties et retours avec auteur et date.
- « + Réception » : entrée directe de marchandise.

## 5 bis. Règles automatiques
Les lots périmés ou bloqués ne sont jamais vendus. La vente utilise d'abord le lot dont la péremption est la plus proche (FEFO).

## 6. Caisse et ventes
1. Menu « Caisse » : choisir un médicament, la quantité, « Ajouter au panier ».
2. Choisir le mode de paiement, « Valider la vente ».
3. Le reçu s'affiche : « Imprimer » ou « Reçu PDF ».
4. Refus si la quantité est nulle ou dépasse le stock disponible.

## 7. Retours de vente
Ouvrir un reçu (Caisse > Historique) > « Retour » sur la ligne : quantité, motif obligatoire, case « remettre en stock » si le produit est intact. La vente d'origine est conservée.

## 8. Tableau de bord
Ventes du jour et des 7 derniers jours, médicaments actifs, ruptures, stocks faibles, péremptions, produits les plus vendus, dernières ventes.

## 9. Administration
`/admin/` (superuser) : gestion des comptes, groupes et données.