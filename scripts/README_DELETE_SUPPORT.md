# Script de suppression de toutes les conversations de support

## Description

Ce script (`delete_all_support_threads.py`) permet de supprimer **toutes les conversations de support** (threads et messages) de manière sécurisée, en respectant les contraintes de clés étrangères de la base de données.

## ⚠️ ATTENTION

Cette opération est **IRRÉVERSIBLE** ! Toutes les conversations seront définitivement supprimées de la base de données.

## Ce qui sera supprimé

1. **Messages** - Tous les messages individuels dans les conversations
2. **MessageThread** - Tous les fils de discussion (conversations)

## Ce qui sera préservé

- **Users** (Utilisateurs) - Les comptes utilisateurs sont conservés
- **Orders** (Commandes) - Les commandes sont conservées
- Toutes les autres données du système

## Utilisation

### Depuis le répertoire racine du projet :

```bash
python3 scripts/delete_all_support_threads.py
```

### Ou depuis le répertoire ecommerce-backend :

```bash
cd ecommerce-backend
python3 ../scripts/delete_all_support_threads.py
```

## Sécurité

Le script demande une confirmation explicite avant d'exécuter la suppression. Vous devez taper **"OUI"** (en majuscules) pour confirmer.

## Vérification

Après exécution du script :

1. **Backend** : Les endpoints `/support/threads` et `/admin/support/threads` retourneront des listes vides (`[]`)
2. **Frontend** : 
   - La page Support client affichera "Aucune demande de support"
   - La page Admin Support affichera une liste vide
   - Les utilisateurs pourront toujours créer de nouvelles conversations

## Gestion des erreurs

Le script utilise des transactions SQLAlchemy pour garantir l'intégrité des données :
- Si une erreur survient, toutes les modifications sont annulées (rollback)
- Le script affiche un message d'erreur détaillé en cas d'échec

## Note technique

Le script respecte l'ordre de suppression nécessaire pour éviter les violations de contraintes de clés étrangères :

1. D'abord les Messages (qui référencent message_threads.id)
2. Ensuite les MessageThread (fils de discussion)

La relation entre MessageThread et Message utilise `cascade="all, delete-orphan"`, donc théoriquement les messages devraient être supprimés automatiquement, mais le script les supprime explicitement pour être sûr et éviter toute erreur.

