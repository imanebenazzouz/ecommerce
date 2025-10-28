import React from "react";
// Page d'informations Livraison & Retours.
import "../styles/LegalPages.css";

export default function Livraison() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Livraison & Retours</h1>
        <p className="last-update">Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

        <section className="legal-section">
          <h2>📦 Modes de livraison</h2>
          
          <h3>Livraison Standard (3-5 jours ouvrés)</h3>
          <ul>
            <li><strong>Délai :</strong> 3 à 5 jours ouvrés après expédition</li>
            <li><strong>Frais :</strong> 4,90€ (Gratuit à partir de 50€ d'achat)</li>
            <li><strong>Suivi :</strong> Numéro de suivi fourni par email</li>
            <li><strong>Zone :</strong> France métropolitaine</li>
          </ul>

          <h3>Livraison Express (24-48h)</h3>
          <ul>
            <li><strong>Délai :</strong> 24 à 48h après expédition</li>
            <li><strong>Frais :</strong> 9,90€</li>
            <li><strong>Suivi :</strong> Suivi en temps réel</li>
            <li><strong>Zone :</strong> France métropolitaine</li>
          </ul>

          <h3>Livraison en Point Relais</h3>
          <ul>
            <li><strong>Délai :</strong> 3 à 5 jours ouvrés</li>
            <li><strong>Frais :</strong> 3,90€ (Gratuit à partir de 40€ d'achat)</li>
            <li><strong>Disponibilité :</strong> 7j/7, 24h/24</li>
            <li><strong>Réseau :</strong> Plus de 15 000 points relais en France</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>🌍 Zones de livraison</h2>
          
          <h3>France Métropolitaine</h3>
          <p>
            Livraison dans toute la France métropolitaine sous 3-5 jours ouvrés.
          </p>

          <h3>Corse</h3>
          <ul>
            <li><strong>Délai :</strong> 5 à 7 jours ouvrés</li>
            <li><strong>Frais :</strong> 8,90€</li>
          </ul>

          <h3>DOM-TOM</h3>
          <ul>
            <li><strong>Délai :</strong> 7 à 14 jours ouvrés</li>
            <li><strong>Frais :</strong> Calculés selon la destination et le poids</li>
            <li><strong>Note :</strong> Des frais de douane peuvent s'appliquer</li>
          </ul>

          <h3>International</h3>
          <p>
            Nous ne livrons pas encore à l'international, mais nous travaillons 
            activement à étendre nos services. Inscrivez-vous à notre newsletter 
            pour être informé dès que ce service sera disponible.
          </p>
        </section>

        <section className="legal-section">
          <h2>📅 Préparation et expédition</h2>
          
          <h3>Délais de préparation</h3>
          <p>
            Toutes les commandes validées avant 12h sont préparées et expédiées 
            le jour même (jours ouvrés). Les commandes passées après 12h ou le 
            week-end sont expédiées le jour ouvré suivant.
          </p>

          <h3>Notification d'expédition</h3>
          <p>
            Dès l'expédition de votre commande, vous recevrez :
          </p>
          <ul>
            <li>Un email de confirmation d'expédition</li>
            <li>Un numéro de suivi de colis</li>
            <li>Un lien pour suivre votre livraison en temps réel</li>
          </ul>

          <h3>Emballage</h3>
          <p>
            Tous nos colis sont soigneusement emballés pour garantir l'intégrité 
            de vos produits. Nous utilisons des matériaux recyclables et respectueux 
            de l'environnement.
          </p>
        </section>

        <section className="legal-section">
          <h2>🏠 Réception de votre commande</h2>
          
          <h3>Livraison à domicile</h3>
          <p>
            Le transporteur effectue généralement 2 tentatives de livraison. Si vous 
            êtes absent :
          </p>
          <ul>
            <li>Un avis de passage sera déposé dans votre boîte aux lettres</li>
            <li>Votre colis sera disponible dans un point relais proche</li>
            <li>Vous aurez 14 jours pour le récupérer</li>
          </ul>

          <h3>Vérification du colis</h3>
          <p>
            À la réception, nous vous recommandons de :
          </p>
          <ul>
            <li>Vérifier l'état du colis en présence du livreur</li>
            <li>Refuser le colis s'il est endommagé</li>
            <li>Signaler toute anomalie dans les 48h</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>↩️ Retours</h2>
          
          <h3>Droit de rétractation</h3>
          <p>
            Vous disposez de 14 jours pour retourner vos produits. 
            Consultez notre page <a href="/legal/retractation">Droit de Rétractation</a> 
            pour tous les détails.
          </p>

          <h3>Comment effectuer un retour ?</h3>
          <ol>
            <li>Connectez-vous à votre compte client</li>
            <li>Accédez à "Mes commandes"</li>
            <li>Sélectionnez la commande concernée</li>
            <li>Cliquez sur "Retourner un produit"</li>
            <li>Imprimez le bon de retour</li>
            <li>Renvoyez le colis à l'adresse indiquée</li>
          </ol>

          <h3>Frais de retour</h3>
          <p>
            Les frais de retour sont à votre charge, sauf en cas de :
          </p>
          <ul>
            <li>Produit défectueux ou non conforme</li>
            <li>Erreur de notre part dans la préparation</li>
            <li>Article endommagé lors du transport</li>
          </ul>

          <h3>Remboursement</h3>
          <p>
            Une fois votre retour réceptionné et vérifié, nous procédons au 
            remboursement sous 14 jours maximum sur votre moyen de paiement initial.
          </p>
        </section>

        <section className="legal-section">
          <h2>❓ Questions fréquentes</h2>
          
          <h3>Puis-je modifier l'adresse de livraison après validation ?</h3>
          <p>
            Si votre commande n'a pas encore été expédiée, contactez rapidement 
            notre service client qui fera son possible pour modifier l'adresse.
          </p>

          <h3>Que faire si je ne reçois pas ma commande ?</h3>
          <p>
            Si le délai de livraison est dépassé, contactez notre service client 
            avec votre numéro de commande. Nous lancerons une enquête avec le transporteur.
          </p>

          <h3>Mon colis est endommagé, que faire ?</h3>
          <p>
            Refusez le colis en présence du livreur ou contactez-nous dans les 48h 
            avec des photos du colis endommagé. Nous vous renverrons un nouveau 
            produit ou procéderons au remboursement.
          </p>
        </section>

        <section className="legal-section">
          <h2>📞 Besoin d'aide ?</h2>
          <p>
            Notre service client est là pour vous accompagner :
          </p>
          <ul>
            <li><strong>Email :</strong> livraison@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
            <li><strong>Chat en ligne :</strong> Disponible 7j/7</li>
            <li><strong>Formulaire :</strong> <a href="/support">Page de contact</a></li>
          </ul>
        </section>
      </div>
    </div>
  );
}

