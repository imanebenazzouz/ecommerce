import React from "react";
// Page d'informations Paiement Sécurisé.
import "../styles/LegalPages.css";

export default function PaiementSecurise() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Paiement Sécurisé</h1>
        <p className="last-update">
          Votre sécurité est notre priorité. Découvrez comment nous protégeons vos transactions.
        </p>

        <section className="legal-section">
          <h2>🔒 Sécurité de vos paiements</h2>
          <p>
            Chez TechStore, la sécurité de vos transactions est notre priorité absolue. 
            Nous mettons en œuvre les technologies les plus avancées pour protéger vos 
            données bancaires et garantir des paiements 100% sécurisés.
          </p>

          <div className="info-box">
            <p>
              <strong>Garantie 100% sécurisé :</strong> Toutes nos transactions sont 
              cryptées et sécurisées selon les normes internationales les plus strictes.
            </p>
          </div>
        </section>

        <section className="legal-section">
          <h2>Moyens de paiement acceptés</h2>
          
          <h3>Cartes bancaires</h3>
          <p>
            Nous acceptons toutes les cartes bancaires internationales :
          </p>
          <ul>
            <li>✓ Visa</li>
            <li>✓ Mastercard</li>
            <li>✓ American Express</li>
            <li>✓ Carte Bleue</li>
          </ul>

          <h3>Paiement en plusieurs fois</h3>
          <p>
            Pour les achats supérieurs à 100€, vous pouvez régler en 3 ou 4 fois 
            sans frais. Cette option vous sera proposée lors du paiement.
          </p>

          <h3>Bientôt disponibles</h3>
          <p>
            Nous travaillons à intégrer d'autres moyens de paiement :
          </p>
          <ul>
            <li>PayPal</li>
            <li>Apple Pay</li>
            <li>Google Pay</li>
            <li>Virement bancaire</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>Technologies de sécurité</h2>
          
          <h3>Cryptage SSL/TLS</h3>
          <p>
            Toutes les pages de notre site sont sécurisées par un certificat SSL/TLS. 
            Ce protocole crypte toutes les informations échangées entre votre navigateur et nos serveurs.
          </p>

          <h3>Certification PCI-DSS</h3>
          <p>
            Notre prestataire de paiement est certifié PCI-DSS (Payment Card Industry 
            Data Security Standard), le niveau de sécurité le plus élevé de l'industrie 
            des cartes bancaires.
          </p>

          <h3>3D Secure</h3>
          <p>
            Tous les paiements sont protégés par le protocole 3D Secure (Verified by Visa, 
            Mastercard SecureCode). Vous serez redirigé vers la page de votre banque pour 
            valider le paiement avec :
          </p>
          <ul>
            <li>Un code SMS</li>
            <li>Votre application bancaire</li>
            <li>Votre code secret personnel</li>
          </ul>

          <h3>Tokenisation</h3>
          <p>
            Vos données bancaires ne sont jamais stockées sur nos serveurs. Elles sont 
            immédiatement remplacées par un "token" (jeton) unique et sécurisé, inutilisable 
            en cas d'interception.
          </p>
        </section>

        <section className="legal-section">
          <h2>🏦 Processus de paiement</h2>
          
          <h3>Étape 1 : Validation du panier</h3>
          <p>
            Vérifiez votre panier et cliquez sur "Passer la commande".
          </p>

          <h3>Étape 2 : Informations de livraison</h3>
          <p>
            Renseignez ou vérifiez vos coordonnées de livraison et de facturation.
          </p>

          <h3>Étape 3 : Choix du mode de livraison</h3>
          <p>
            Sélectionnez votre mode de livraison préféré (standard, express, point relais).
          </p>

          <h3>Étape 4 : Paiement sécurisé</h3>
          <p>
            Saisissez vos informations bancaires sur la page sécurisée de notre 
            prestataire de paiement. Vous serez redirigé vers votre banque pour 
            l'authentification 3D Secure.
          </p>

          <h3>Étape 5 : Confirmation</h3>
          <p>
            Une fois le paiement validé, vous recevez immédiatement un email de 
            confirmation avec le récapitulatif de votre commande.
          </p>
        </section>

        <section className="legal-section">
          <h2>Quand êtes-vous débité ?</h2>
          <p>
            Votre carte bancaire est débitée immédiatement lors de la validation 
            de votre commande. Le montant apparaît généralement sur votre compte 
            sous 24 à 48h selon votre banque.
          </p>

          <h3>Paiement en plusieurs fois</h3>
          <p>
            Si vous choisissez le paiement fractionné :
          </p>
          <ul>
            <li><strong>1er prélèvement :</strong> À la validation de la commande</li>
            <li><strong>2e prélèvement :</strong> 30 jours après</li>
            <li><strong>3e prélèvement :</strong> 60 jours après (si applicable)</li>
            <li><strong>4e prélèvement :</strong> 90 jours après (si applicable)</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>Protection contre la fraude</h2>
          
          <h3>Détection automatique</h3>
          <p>
            Nous utilisons des systèmes intelligents de détection de fraude qui 
            analysent chaque transaction en temps réel pour identifier les comportements 
            suspects.
          </p>

          <h3>Vérifications supplémentaires</h3>
          <p>
            Dans certains cas, nous pouvons vous demander des vérifications supplémentaires 
            pour protéger votre compte :
          </p>
          <ul>
            <li>Confirmation de l'adresse email</li>
            <li>Vérification téléphonique</li>
            <li>Justificatif de domicile</li>
          </ul>

          <h3>Que faire en cas de transaction frauduleuse ?</h3>
          <p>
            Si vous constatez une transaction suspecte sur votre compte :
          </p>
          <ol>
            <li>Contactez immédiatement votre banque</li>
            <li>Faites opposition sur votre carte bancaire</li>
            <li>Prévenez-nous à : securite@techstore-pro.fr</li>
            <li>Modifiez votre mot de passe de compte</li>
          </ol>
        </section>

        <section className="legal-section">
          <h2>📧 Factures et justificatifs</h2>
          
          <h3>Facture</h3>
          <p>
            Une facture au format PDF vous est automatiquement envoyée par email 
            après chaque commande. Vous pouvez également la télécharger depuis 
            votre compte client dans la section "Mes commandes".
          </p>

          <h3>Conservation</h3>
          <p>
            Nous vous recommandons de conserver vos factures et justificatifs de 
            paiement, particulièrement pour :
          </p>
          <ul>
            <li>La garantie des produits</li>
            <li>Les éventuels retours</li>
            <li>Vos déclarations fiscales (si achat professionnel)</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>🔄 Remboursements</h2>
          
          <h3>Délais</h3>
          <p>
            En cas de retour ou d'annulation, nous procédons au remboursement sous 
            14 jours maximum à compter de la réception du retour.
          </p>

          <h3>Méthode</h3>
          <p>
            Le remboursement est effectué sur le même moyen de paiement que celui 
            utilisé lors de l'achat. Le délai d'affichage sur votre compte dépend 
            de votre banque (généralement 3-5 jours ouvrés).
          </p>

          <h3>Paiement fractionné</h3>
          <p>
            Si vous avez payé en plusieurs fois, le remboursement annule automatiquement 
            les prélèvements à venir et rembourse les montants déjà prélevés.
          </p>
        </section>

        <section className="legal-section">
          <h2>❓ Questions fréquentes</h2>
          
          <h3>Mes données bancaires sont-elles stockées ?</h3>
          <p>
            <strong>Non.</strong> Vos données bancaires ne sont jamais stockées sur 
            nos serveurs. Elles sont directement traitées par notre prestataire de 
            paiement sécurisé et immédiatement tokenisées.
          </p>

          <h3>Pourquoi mon paiement a-t-il été refusé ?</h3>
          <p>
            Plusieurs raisons peuvent expliquer un refus :
          </p>
          <ul>
            <li>Solde insuffisant</li>
            <li>Plafond de paiement dépassé</li>
            <li>Carte expirée</li>
            <li>Informations incorrectes</li>
            <li>Refus de votre banque</li>
          </ul>
          <p>
            Contactez votre banque ou essayez avec un autre moyen de paiement.
          </p>

          <h3>Puis-je payer par virement bancaire ?</h3>
          <p>
            Ce mode de paiement n'est pas encore disponible mais sera bientôt proposé.
          </p>

          <h3>Puis-je sauvegarder ma carte pour mes prochains achats ?</h3>
          <p>
            Oui, vous pouvez enregistrer votre carte de manière sécurisée (sous forme 
            de token) pour accélérer vos futurs achats. Cette option vous sera proposée 
            lors du paiement.
          </p>
        </section>

        <section className="legal-section">
          <h2>🏅 Nos certifications</h2>
          <div className="info-box">
            <ul style={{ marginBottom: 0 }}>
              <li>✓ Certificat SSL/TLS 256 bits</li>
              <li>✓ Prestataire certifié PCI-DSS Level 1</li>
              <li>✓ Conforme au règlement européen DSP2</li>
              <li>✓ Protection 3D Secure activée</li>
              <li>✓ Conforme RGPD</li>
            </ul>
          </div>
        </section>

        <section className="legal-section">
          <h2>Besoin d'aide ?</h2>
          <p>
            Pour toute question concernant le paiement :
          </p>
          <ul>
            <li><strong>Email :</strong> paiement@techstore-pro.fr</li>
            <li><strong>Sécurité :</strong> securite@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
            <li><strong>Formulaire :</strong> <a href="/support">Page de contact</a></li>
          </ul>
        </section>
      </div>
    </div>
  );
}

