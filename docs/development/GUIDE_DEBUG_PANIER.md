# 🔍 Guide de Debug - Problème Ajout au Panier

## ✅ Vérifications effectuées

### 1. API Backend ✅
- ✅ Serveur API démarré correctement (port 8000)
- ✅ Endpoint `/products` fonctionne
- ✅ Endpoint `/cart/add` fonctionne (avec authentification)
- ✅ Format de données correct (`price_cents`, `stock_qty`)

### 2. Frontend ✅
- ✅ Serveur Vite démarré (port 5176)
- ✅ Code React semble correct
- ✅ Gestion panier local implémentée
- ✅ Gestion panier serveur implémentée

## 🧪 Tests à effectuer

### Test 1: Vérifier l'API
```bash
# Vérifier que l'API répond
curl http://localhost:8000/products

# Vérifier le format des données
curl http://localhost:8000/products | jq '.[0]'
```

### Test 2: Vérifier le frontend
1. Ouvrir http://localhost:5176
2. Aller au catalogue
3. Ouvrir la console développeur (F12)
4. Cliquer sur "Ajouter au panier"
5. Vérifier les logs dans la console

### Test 3: Vérifier l'authentification
1. Aller sur http://localhost:5176/login
2. Se connecter avec un compte de test
3. Retourner au catalogue
4. Essayer d'ajouter au panier

## 🔧 Solutions possibles

### Problème 1: Utilisateur non connecté
**Symptôme**: Bouton "Ajouter au panier" ne fonctionne pas
**Solution**: Vérifier que le panier local fonctionne
```javascript
// Dans la console du navigateur
localStorage.getItem('localCart')
```

### Problème 2: Utilisateur connecté
**Symptôme**: Erreur 401 ou 403
**Solution**: Vérifier le token d'authentification
```javascript
// Dans la console du navigateur
localStorage.getItem('token')
```

### Problème 3: Format de données
**Symptôme**: Erreur de format ou données manquantes
**Solution**: Vérifier que l'API retourne le bon format

## 🚀 Actions à effectuer

1. **Ouvrir le navigateur** sur http://localhost:5176
2. **Ouvrir la console** (F12)
3. **Aller au catalogue**
4. **Cliquer sur "Ajouter au panier"**
5. **Vérifier les erreurs** dans la console
6. **Partager les erreurs** pour diagnostic

## 📋 Checklist de debug

- [ ] API backend fonctionne (port 8000)
- [ ] Frontend React fonctionne (port 5176)
- [ ] Console développeur ouverte
- [ ] Test d'ajout au panier effectué
- [ ] Erreurs JavaScript identifiées
- [ ] Logs réseau vérifiés (onglet Network)

## 🎯 Prochaines étapes

1. **Tester l'interface** manuellement
2. **Identifier l'erreur** exacte
3. **Corriger le problème** spécifique
4. **Valider la solution**

---

**Note**: Le code semble correct, le problème est probablement dans l'exécution ou la configuration. Les tests manuels permettront d'identifier la cause exacte.
