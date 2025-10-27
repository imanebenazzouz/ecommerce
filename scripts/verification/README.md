# 🔍 Scripts de Vérification

Scripts utilitaires pour vérifier l'état de la base de données et tester les fonctionnalités.

## 📋 Scripts Disponibles

### `check_database.py`
Vérifie la connexion et l'état de la base de données PostgreSQL.

```bash
python scripts/verification/check_database.py
```

**Ce qu'il vérifie :**
- ✅ Connexion à PostgreSQL
- ✅ Liste des tables
- ✅ Nombre d'enregistrements par table
- ✅ Intégrité des données

### `check_database_backend.py`
Version backend du script de vérification de base de données.

```bash
cd ecommerce-backend
python ../scripts/verification/check_database_backend.py
```

### `verify_database_orders.py`
Vérifie la cohérence des commandes dans la base de données.

```bash
python scripts/verification/verify_database_orders.py
```

**Ce qu'il vérifie :**
- ✅ Commandes et leurs statuts
- ✅ Relation commandes ↔ paiements
- ✅ Relation commandes ↔ articles
- ✅ Stock des produits

### `verify_database_sync.py`
Vérifie la synchronisation de la structure de la base de données.

```bash
python scripts/verification/verify_database_sync.py
```

**Ce qu'il vérifie :**
- ✅ Structure de la table `payments`
- ✅ Présence de tous les champs requis
- ✅ Contraintes et index
- ✅ Synchronisation avec les modèles backend

### `demo_name_validation.py`
Script de démonstration de la validation des noms et prénoms.

```bash
python scripts/verification/demo_name_validation.py
```

**Ce qu'il fait :**
- ✅ Démontre les règles de validation
- ✅ Affiche des exemples valides/invalides
- ✅ Teste les edge cases

## 🎯 Utilisation

### Vérification Rapide
```bash
# Vérifier que tout fonctionne
python scripts/verification/check_database.py
python scripts/verification/verify_database_orders.py
```

### Vérification Après Modifications
```bash
# Après des changements sur les paiements
python scripts/verification/verify_database_sync.py

# Après des changements sur les commandes
python scripts/verification/verify_database_orders.py
```

## 📝 Notes

Ces scripts sont des **outils de vérification** et ne font pas partie de la suite de tests automatisés.

Pour les tests automatisés, voir le dossier `tests/`.

---

**Date de création :** Octobre 2025

