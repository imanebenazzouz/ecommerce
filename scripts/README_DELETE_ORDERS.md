# Script de suppression de toutes les commandes

## Description

Ce script (`delete_all_orders.py`) permet de supprimer **toutes les commandes de tous les utilisateurs** de manière sécurisée, en respectant les contraintes de clés étrangères de la base de données.

## ⚠️ ATTENTION

Cette opération est **IRRÉVERSIBLE** ! Toutes les commandes seront définitivement supprimées de la base de données.

## Ce qui sera supprimé

1. **Payments** (Paiements) - Tous les paiements liés aux commandes
2. **Invoices** (Factures) - Toutes les factures générées
3. **Deliveries** (Livraisons) - Toutes les informations de livraison
4. **OrderItems** (Éléments de commande) - Tous les produits commandés
5. **Orders** (Commandes) - Toutes les commandes

## Ce qui sera préservé

- **Users** (Utilisateurs) - Les comptes utilisateurs sont conservés
- **Products** (Produits) - Le catalogue de produits est conservé
- **Carts** (Paniers) - Les paniers utilisateurs sont conservés
- **MessageThread** (Threads de support) - Les fils de discussion sont conservés, mais les références `order_id` sont mises à `NULL`

## Utilisation

### Depuis le répertoire racine du projet :

```bash
python3 scripts/delete_all_orders.py
```

### Ou depuis le répertoire ecommerce-backend :

```bash
cd ecommerce-backend
python3 ../scripts/delete_all_orders.py
```

## Sécurité

Le script demande une confirmation explicite avant d'exécuter la suppression. Vous devez taper **"OUI"** (en majuscules) pour confirmer.

## Vérification

Après exécution du script :

1. **Backend** : Les endpoints `/orders` et `/admin/orders` retourneront des listes vides (`[]`)
2. **Frontend** : 
   - La page "Mes commandes" affichera "Vous n'avez pas encore de commandes"
   - La page Admin affichera une liste vide de commandes
   - Le support client fonctionnera toujours, mais sans référence aux commandes supprimées

## Gestion des erreurs

Le script utilise des transactions SQLAlchemy pour garantir l'intégrité des données :
- Si une erreur survient, toutes les modifications sont annulées (rollback)
- Le script affiche un message d'erreur détaillé en cas d'échec

## Note technique

Le script respecte l'ordre de suppression nécessaire pour éviter les violations de contraintes de clés étrangères :

1. D'abord les entités dépendantes (Payments, Invoices, Deliveries)
2. Ensuite les références dans MessageThread (mise à NULL)
3. Puis les OrderItems
4. Enfin les Orders

