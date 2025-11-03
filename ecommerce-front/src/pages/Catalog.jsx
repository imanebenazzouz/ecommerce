// ============================================================
// PAGE CATALOG (Catalogue de produits)
// ============================================================
// 
// Cette page affiche tous les produits disponibles dans la boutique.
// Les utilisateurs peuvent :
// - Voir la liste complète des produits
// - Consulter les prix et le stock disponible
// - Ajouter des produits au panier (connecté ou local)
//
// FONCTIONNALITÉS :
// - Chargement automatique des produits au montage du composant
// - Gestion du panier pour utilisateurs connectés (via API)
// - Gestion du panier local (localStorage) pour visiteurs non connectés
// - Vérification du stock avant ajout
// - Messages de succès/erreur dynamiques
// ============================================================

// ========== IMPORTS ==========
import React, { useEffect, useState } from "react"; // React : bibliothèque pour créer l'interface
                                                     // useEffect : pour exécuter du code au chargement
                                                     // useState : pour gérer l'état des données
import { api } from "../lib/api";                    // api : client HTTP pour appeler le backend
import { useAuth } from "../hooks/useAuth";          // useAuth : hook personnalisé pour vérifier si l'utilisateur est connecté
import "../styles/catalog.css";                      // Styles CSS spécifiques à cette page

// ========== COMPOSANT PRINCIPAL ==========
/**
 * Composant Catalog - Affiche le catalogue de produits
 * 
 * Ce composant gère l'affichage de tous les produits disponibles et permet
 * aux utilisateurs d'ajouter des produits au panier.
 * 
 * @returns {JSX.Element} La page du catalogue avec la liste des produits
 */
export default function Catalog() {
  // ===== ÉTATS (STATE) DU COMPOSANT =====
  // Les états React permettent de stocker et de mettre à jour les données dynamiques
  
  // isAuthenticated : fonction pour vérifier si l'utilisateur est connecté
  const { isAuthenticated } = useAuth();
  
  // products : tableau contenant tous les produits récupérés depuis l'API
  // Initialisé à un tableau vide [] au chargement
  const [products, setProducts] = useState([]);
  
  // msg : message de succès affiché après une action réussie (ex: "Produit ajouté")
  // Initialisé à une chaîne vide ""
  const [msg, setMsg] = useState("");
  
  // err : message d'erreur affiché en cas de problème (ex: "Stock insuffisant")
  // Initialisé à une chaîne vide ""
  const [err, setErr] = useState("");

  // ===== EFFET DE CHARGEMENT INITIAL =====
  // useEffect s'exécute automatiquement au montage du composant (quand la page s'affiche)
  // Le tableau [] vide en deuxième paramètre signifie : "exécute une seule fois au chargement"
  useEffect(() => {
    // Fonction asynchrone immédiatement invoquée (IIFE - Immediately Invoked Function Expression)
    // Permet d'utiliser await à l'intérieur de useEffect
    (async () => {
      try {
        // Réinitialiser le message d'erreur avant de charger les produits
        setErr("");
        
        // Appel API : récupérer la liste de tous les produits depuis le backend
        // GET /products → retourne un tableau de produits
        const data = await api.listProducts();
        
        // Mettre à jour l'état avec les produits récupérés
        // Cela déclenche un re-render (re-affichage) du composant
        setProducts(data);
        
      } catch (e) {
        // En cas d'erreur (réseau, serveur down, etc.)
        // Afficher l'erreur dans la console du navigateur (pour le développeur)
        console.error('Erreur chargement produits:', e);
        
        // Afficher un message d'erreur à l'utilisateur
        setErr(`Erreur de chargement: ${e.message}`);
      }
    })();
  }, []); // Tableau de dépendances vide = exécution une seule fois au montage

  // ===== FONCTION D'AJOUT AU PANIER =====
  /**
   * Ajoute un produit au panier (serveur ou local selon l'état de connexion)
   * 
   * Comportement :
   * - Si l'utilisateur est connecté → ajoute au panier serveur (via API)
   * - Si l'utilisateur n'est PAS connecté → ajoute au panier local (localStorage)
   * 
   * Validations effectuées :
   * - Vérification du stock disponible
   * - Vérification de la quantité déjà dans le panier
   * 
   * @param {Object} p - Le produit à ajouter (contient id, name, stock_qty, etc.)
   * @returns {Promise<void>}
   */
  async function add(p) {
    // Réinitialiser tous les messages avant une nouvelle action
    setMsg("");  // Efface le message de succès précédent
    setErr("");  // Efface le message d'erreur précédent
    
    try {
      // ===== CAS 1 : UTILISATEUR CONNECTÉ =====
      if (isAuthenticated()) {
        // L'utilisateur a un compte et est connecté
        // On ajoute le produit au panier serveur (stocké en base de données)
        // POST /cart/add → backend gère la vérification du stock
        await api.addToCart({ product_id: p.id, qty: 1 });
        
        // Afficher un message de succès à l'utilisateur
        setMsg(`${p.name} ajouté au panier`);
        
      } else {
        // ===== CAS 2 : UTILISATEUR NON CONNECTÉ (VISITEUR) =====
        // On utilise le localStorage du navigateur pour stocker temporairement le panier
        // localStorage : stockage local du navigateur (persiste même si on ferme l'onglet)
        
        // Récupérer le panier local existant depuis le localStorage
        const localCartData = localStorage.getItem('localCart');
        
        // Parser le JSON ou créer un nouveau panier vide si n'existe pas
        // Format du panier local : { items: { "product_id": { product_id, quantity } } }
        const localCart = localCartData ? JSON.parse(localCartData) : { items: {} };
        
        // ===== VALIDATION DU STOCK =====
        // Vérifier qu'il y a assez de stock avant d'ajouter
        
        // Récupérer le stock disponible (compatible avec différents formats d'API)
        const available = p.stock_qty || p.stock || 0;
        
        // Récupérer la quantité déjà présente dans le panier local pour ce produit
        // Si le produit n'est pas encore dans le panier, quantité = 0
        const existingQty = localCart.items[p.id]?.quantity || 0;
        
        // Validation 1 : Vérifier que le produit est en stock
        if (available <= 0) {
          setErr("Produit indisponible");  // Stock = 0
          return;  // Arrêter l'exécution de la fonction
        }
        
        // Validation 2 : Vérifier qu'on ne dépasse pas le stock disponible
        // Comparer : (quantité déjà dans panier + 1 nouveau) vs stock disponible
        if (existingQty + 1 > available) {
          setErr(`Stock insuffisant. Vous avez déjà ${existingQty} dans le panier (stock: ${available}).`);
          return;  // Arrêter l'exécution
        }
        
        // ===== MISE À JOUR DU PANIER LOCAL =====
        // Vérifier si le produit existe déjà dans le panier
        const existingItem = localCart.items[p.id];
        
        if (existingItem) {
          // Le produit est déjà dans le panier → incrémenter la quantité de 1
          localCart.items[p.id].quantity = existingQty + 1;
        } else {
          // Le produit n'est pas encore dans le panier → l'ajouter avec quantité = 1
          localCart.items[p.id] = { product_id: p.id, quantity: 1 };
        }
        
        // Sauvegarder le panier mis à jour dans le localStorage
        // JSON.stringify() convertit l'objet JavaScript en chaîne JSON pour le stockage
        localStorage.setItem('localCart', JSON.stringify(localCart));
        
        // Afficher un message de succès avec indication "(local)"
        setMsg(`${p.name} ajouté au panier (local)`);
      }
      
    } catch (e) {
      // ===== GESTION DES ERREURS =====
      // En cas d'erreur lors de l'ajout (ex: problème réseau, serveur indisponible)
      
      // Vérifier si c'est une erreur d'authentification (401 Unauthorized)
      if (e.message.startsWith("HTTP 401")) {
        setErr("Erreur de connexion. Vérifiez votre authentification.");
      } else {
        // Autre type d'erreur → afficher le message d'erreur brut
        setErr(e.message);
      }
    }
  }

  // ===== FORMATEUR DE PRIX =====
  // Intl.NumberFormat : API JavaScript pour formater des nombres selon une locale
  // "fr-FR" : format français (ex: 12,50 €)
  // style: "currency" : afficher comme une devise
  // currency: "EUR" : utiliser l'euro (€)
  // Exemple d'utilisation : fmt.format(1250) → "12,50 €"
  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  // ===== RENDU JSX (INTERFACE VISUELLE) =====
  // JSX = mélange de HTML et JavaScript pour créer l'interface React
  // Tout ce qui est dans return() sera affiché à l'écran
  return (
    // Conteneur principal avec la classe CSS "cat" (catalogue)
    <div className="cat">
      
      {/* ===== SECTION HERO (BANDEAU D'ACCUEIL) ===== */}
      {/* Bannière d'accueil en haut de la page */}
      <section className="hero">
        {/* Titre principal de la boutique */}
        <h1 className="hero__title">Bienvenue sur notre boutique</h1>
        
        {/* Sous-titre avec emoji */}
        <p className="hero__subtitle">
          Découvrez nos meilleurs produits au meilleur prix 💎
        </p>
      </section>

      {/* ===== EN-TÊTE DU CATALOGUE ===== */}
      {/* Affiche le titre "Catalogue" et le nombre de produits disponibles */}
      <div className="cat__header">
        <h2 className="cat__title">Catalogue</h2>
        
        {/* Affichage dynamique du nombre de produits */}
        {/* products.length = nombre d'éléments dans le tableau products */}
        <p className="cat__subtitle">{products.length} produit(s)</p>
      </div>

      {/* ===== MESSAGES DE SUCCÈS / ERREUR ===== */}
      {/* Affichage conditionnel : le message ne s'affiche que si msg n'est pas vide */}
      {/* Syntaxe : {condition && <element>} signifie "si condition est vraie, afficher element" */}
      {msg && <p className="cat__alert cat__alert--ok">{msg}</p>}
      
      {/* Message d'erreur (rouge) si err n'est pas vide */}
      {err && <p className="cat__alert cat__alert--ko">{err}</p>}

      {/* ===== GRILLE DE PRODUITS ===== */}
      {/* Affiche tous les produits sous forme de grille (layout CSS) */}
      <div className="cat__grid">
        
        {/* ===== BOUCLE SUR LES PRODUITS ===== */}
        {/* products.map() : pour chaque produit (p), créer une carte de produit */}
        {/* map() retourne un nouveau tableau de composants JSX */}
        {products.map((p) => (
          
          // ===== CARTE DE PRODUIT =====
          // article = élément HTML sémantique pour un contenu autonome
          // key={p.id} : requis par React pour identifier chaque élément de liste de manière unique
          // Cela aide React à optimiser les mises à jour (ne re-render que ce qui change)
          <article key={p.id} className="pcard">
            
            {/* ===== IMAGE DU PRODUIT ===== */}
            {/* Pour l'instant, on utilise un placeholder à la place d'une vraie image */}
            {/* TODO : Remplacer par <img src={p.image_url} alt={p.name} /> */}
            <div className="pcard__media">Image</div>

            {/* ===== CORPS DE LA CARTE (INFOS PRODUIT) ===== */}
            <div className="pcard__body">
              
              {/* Nom du produit (titre h3) */}
              <h3 className="pcard__title">{p.name}</h3>

              {/* ===== MÉTADONNÉES (PRIX + STOCK) ===== */}
              <div className="pcard__meta">
                
                {/* ===== AFFICHAGE DU PRIX ===== */}
                <span className="pcard__price">
                  {/* IIFE (Immediately Invoked Function Expression) pour calculer le prix */}
                  {/* Permet d'écrire de la logique JavaScript inline dans JSX */}
                  {(() => {
                    // Compatibilité avec différents formats d'API :
                    // - price_cents : format backend (ex: 1250 = 12,50€)
                    // - price : format alternatif en euros (ex: 12.50)
                    const price = p.price_cents || (p.price ? Math.round(p.price * 100) : 0);
                    
                    // Si prix > 0 : formater en euros français (12,50 €)
                    // Sinon : afficher "Prix non disponible"
                    return price > 0 ? fmt.format(price / 100) : "Prix non disponible";
                  })()}
                </span>
                
                {/* ===== AFFICHAGE DU STOCK ===== */}
                <span className="pcard__stock">
                  {/* Condition : si le produit est actif (disponible à la vente) */}
                  {p.active ? (
                    // ===== PRODUIT ACTIF : AFFICHER LE STOCK =====
                    // \u00a0 = espace insécable (non-breaking space) pour éviter le retour à la ligne
                    // IIFE pour calculer l'affichage du stock
                    <>Stock\u00a0:{" "}{(() => { 
                      // Récupérer la quantité en stock (compatibilité avec différents formats)
                      const s = p.stock_qty || p.stock || 0; 
                      // Si stock < 5 : afficher "Faible" (alerte visuelle)
                      // Sinon : afficher le nombre exact d'unités disponibles
                      return s < 5 ? "Faible" : s; 
                    })()}</>
                  ) : (
                    // ===== PRODUIT INACTIF : AFFICHER "INDISPONIBLE" =====
                    <>Indisponible</>
                  )}
                </span>
              </div>
            </div>

            {/* ===== PIED DE LA CARTE (BOUTON D'ACTION) ===== */}
            <div className="pcard__foot">
              {/* Bouton pour ajouter le produit au panier */}
              <button
                // Événement onClick : appeler la fonction add() avec le produit (p) en paramètre
                // () => add(p) : fonction fléchée pour passer le paramètre
                onClick={() => add(p)}
                
                // disabled : désactiver le bouton si le produit n'est pas actif
                // Un bouton désactivé ne peut pas être cliqué et est grisé par CSS
                disabled={!p.active}
                
                // Classes CSS pour le style du bouton (btn = bouton, btn--primary = couleur principale)
                className="btn btn--primary"
              >
                {/* Texte du bouton : "Ajouter au panier" ou "Indisponible" selon p.active */}
                {/* Condition ternaire : condition ? valeur_si_vrai : valeur_si_faux */}
                {p.active ? "Ajouter au panier" : "Indisponible"}
              </button>
            </div>
          </article>
        ))}
        {/* FIN DE LA BOUCLE products.map() */}
        
      </div>
      {/* FIN DE LA GRILLE */}
      
    </div>
    // FIN DU CONTENEUR PRINCIPAL
  );
  // FIN DU RETURN (fin du rendu JSX)
}
// FIN DU COMPOSANT Catalog