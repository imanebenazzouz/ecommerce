#!/bin/bash

echo "🧪 Test de navigation de l'application e-commerce"
echo "=================================================="

# Vérifier si les serveurs sont démarrés
echo "🔍 Vérification des serveurs..."

# Test du backend
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend FastAPI opérationnel sur http://localhost:8000"
else
    echo "❌ Backend non accessible. Démarrez-le avec: ./start-backend.sh"
    exit 1
fi

# Test du frontend
if curl -s http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend React opérationnel sur http://localhost:5173"
else
    echo "❌ Frontend non accessible. Démarrez-le avec: ./start-frontend.sh"
    exit 1
fi

echo ""
echo "🎯 Tests de navigation à effectuer manuellement :"
echo "=================================================="
echo ""
echo "1. 📱 Ouvrez http://localhost:5173 dans votre navigateur"
echo ""
echo "2. 🏠 Page d'accueil (/) :"
echo "   - Vérifiez que le catalogue s'affiche"
echo "   - Testez l'ajout d'articles au panier"
echo "   - Vérifiez la navigation vers le panier"
echo ""
echo "3. 🔐 Page de connexion (/login) :"
echo "   - Utilisez les comptes de test :"
echo "     • Admin: admin@example.com / admin"
echo "     • Client: client@example.com / secret"
echo "   - Testez la redirection après connexion"
echo "   - Vérifiez le lien vers l'inscription"
echo ""
echo "4. 👤 Page d'inscription (/register) :"
echo "   - Testez la validation des champs"
echo "   - Vérifiez l'indicateur de force de mot de passe"
echo "   - Testez la redirection vers la connexion"
echo ""
echo "5. 🛒 Page panier (/cart) :"
echo "   - Vérifiez la protection de route (redirection si non connecté)"
echo "   - Testez la gestion des quantités"
echo "   - Vérifiez le processus de paiement"
echo ""
echo "6. 🧭 Navigation :"
echo "   - Testez tous les liens de navigation"
echo "   - Vérifiez les états actifs des liens"
echo "   - Testez la déconnexion"
echo ""
echo "7. 📱 Responsive :"
echo "   - Redimensionnez la fenêtre"
echo "   - Testez sur mobile (F12 > Device toolbar)"
echo ""
echo "8. ✨ Animations :"
echo "   - Survolez les cartes et boutons"
echo "   - Vérifiez les transitions"
echo "   - Testez les états de chargement"
echo ""
echo "🎉 Si tous ces tests passent, l'application fonctionne correctement !"
echo ""
echo "🐛 En cas de problème :"
echo "   - Vérifiez la console du navigateur (F12)"
echo "   - Vérifiez les logs du backend"
echo "   - Redémarrez les serveurs si nécessaire"
