import React from "react";
// Page légale: Politique de Confidentialité (RGPD).
import "../../styles/LegalPages.css";

export default function Confidentialite() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Politique de Confidentialité (RGPD)</h1>
        <p className="last-update">Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

        <section className="legal-section">
          <h2>1. Introduction</h2>
          <p>
            Mon e-commerce s'engage à protéger la vie privée et les données personnelles 
            de ses utilisateurs. Cette politique de confidentialité explique comment nous 
            collectons, utilisons, stockons et protégeons vos données conformément au 
            Règlement Général sur la Protection des Données (RGPD) et à la loi Informatique 
            et Libertés.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Responsable du traitement</h2>
          <p>
            Le responsable du traitement des données personnelles est :
          </p>
          <ul>
            <li><strong>Raison sociale :</strong> TechStore Pro SAS</li>
            <li><strong>Adresse :</strong> 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>Email :</strong> dpo@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>3. Données collectées</h2>
          <p>
            Nous collectons différents types de données personnelles pour vous fournir 
            nos services :
          </p>
          
          <h3>3.1 Données d'identification</h3>
          <ul>
            <li>Nom et prénom</li>
            <li>Adresse email</li>
            <li>Numéro de téléphone</li>
            <li>Date de naissance (optionnel)</li>
          </ul>

          <h3>3.2 Données de livraison</h3>
          <ul>
            <li>Adresse de livraison</li>
            <li>Adresse de facturation</li>
            <li>Nom de la rue et numéro</li>
            <li>Code postal et ville</li>
            <li>Pays</li>
          </ul>

          <h3>3.3 Données de paiement</h3>
          <ul>
            <li>Informations de carte bancaire (cryptées et non stockées)</li>
            <li>Historique des transactions</li>
            <li>Montants des commandes</li>
          </ul>

          <h3>3.4 Données de navigation</h3>
          <ul>
            <li>Adresse IP</li>
            <li>Type de navigateur</li>
            <li>Pages visitées</li>
            <li>Durée de visite</li>
            <li>Cookies (voir notre <a href="/legal/cookies">Politique des Cookies</a>)</li>
          </ul>

          <h3>3.5 Données de commande</h3>
          <ul>
            <li>Historique des achats</li>
            <li>Produits consultés</li>
            <li>Panier d'achat</li>
            <li>Préférences d'achat</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>4. Finalités du traitement</h2>
          <p>
            Vos données personnelles sont collectées et traitées pour les finalités suivantes :
          </p>
          <ul>
            <li><strong>Gestion des commandes :</strong> traitement, livraison, facturation</li>
            <li><strong>Gestion du compte client :</strong> création et suivi du compte</li>
            <li><strong>Service client :</strong> assistance et support technique</li>
            <li><strong>Communication :</strong> emails de confirmation, notifications</li>
            <li><strong>Marketing :</strong> newsletters, offres personnalisées (avec consentement)</li>
            <li><strong>Sécurité :</strong> prévention de la fraude, sécurisation des transactions</li>
            <li><strong>Statistiques :</strong> amélioration de nos services</li>
            <li><strong>Obligations légales :</strong> conformité fiscale et comptable</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>5. Base légale du traitement</h2>
          <p>
            Le traitement de vos données repose sur les bases légales suivantes :
          </p>
          <ul>
            <li><strong>Exécution du contrat :</strong> traitement des commandes et livraisons</li>
            <li><strong>Obligation légale :</strong> conservation des factures, déclarations fiscales</li>
            <li><strong>Consentement :</strong> newsletters, cookies non essentiels</li>
            <li><strong>Intérêt légitime :</strong> lutte contre la fraude, amélioration des services</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>6. Destinataires des données</h2>
          <p>
            Vos données personnelles peuvent être transmises aux destinataires suivants :
          </p>
          <ul>
            <li><strong>Personnel autorisé :</strong> services internes (commercial, logistique, support)</li>
            <li><strong>Prestataires techniques :</strong> hébergement, maintenance du site</li>
            <li><strong>Partenaires logistiques :</strong> transporteurs pour la livraison</li>
            <li><strong>Prestataires de paiement :</strong> traitement sécurisé des paiements</li>
            <li><strong>Autorités compétentes :</strong> en cas d'obligation légale</li>
          </ul>
          <p>
            Tous nos prestataires sont soumis à des obligations de confidentialité et ne 
            peuvent utiliser vos données qu'aux fins prévues.
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Transfert hors UE</h2>
          <p>
            Vos données sont hébergées au sein de l'Union Européenne. En cas de transfert 
            hors UE, nous nous assurons que des garanties appropriées sont mises en place 
            (clauses contractuelles types, décision d'adéquation de la Commission Européenne).
          </p>
        </section>

        <section className="legal-section">
          <h2>8. Durée de conservation</h2>
          <p>
            Vos données sont conservées pour les durées suivantes :
          </p>
          <ul>
            <li><strong>Données de compte client :</strong> durée de la relation contractuelle + 3 ans</li>
            <li><strong>Données de commande :</strong> 10 ans (obligation comptable et fiscale)</li>
            <li><strong>Données de paiement :</strong> 13 mois (obligation légale)</li>
            <li><strong>Cookies :</strong> 13 mois maximum</li>
            <li><strong>Données de prospection :</strong> 3 ans à compter du dernier contact</li>
            <li><strong>Données de navigation :</strong> 13 mois</li>
          </ul>
          <p>
            Au-delà de ces durées, vos données sont supprimées ou anonymisées.
          </p>
        </section>

        <section className="legal-section">
          <h2>9. Vos droits RGPD</h2>
          <p>
            Conformément au RGPD, vous disposez des droits suivants :
          </p>
          
          <h3>9.1 Droit d'accès</h3>
          <p>
            Vous pouvez obtenir une copie de vos données personnelles que nous détenons.
          </p>

          <h3>9.2 Droit de rectification</h3>
          <p>
            Vous pouvez demander la correction de vos données inexactes ou incomplètes.
          </p>

          <h3>9.3 Droit à l'effacement ("droit à l'oubli")</h3>
          <p>
            Vous pouvez demander la suppression de vos données dans certaines conditions.
          </p>

          <h3>9.4 Droit à la limitation du traitement</h3>
          <p>
            Vous pouvez demander la limitation du traitement de vos données.
          </p>

          <h3>9.5 Droit à la portabilité</h3>
          <p>
            Vous pouvez récupérer vos données dans un format structuré et lisible.
          </p>

          <h3>9.6 Droit d'opposition</h3>
          <p>
            Vous pouvez vous opposer au traitement de vos données pour des raisons 
            tenant à votre situation particulière.
          </p>

          <h3>9.7 Droit de retirer votre consentement</h3>
          <p>
            Pour les traitements basés sur le consentement, vous pouvez le retirer à tout moment.
          </p>

          <h3>9.8 Directives post-mortem</h3>
          <p>
            Vous pouvez définir des directives relatives au sort de vos données après votre décès.
          </p>

          <h3>Comment exercer vos droits ?</h3>
          <ul>
            <li><strong>Email :</strong> dpo@techstore-pro.fr</li>
            <li><strong>Courrier :</strong> TechStore Pro - DPO, 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>Formulaire en ligne :</strong> <a href="/support">Page de contact</a></li>
          </ul>
          <p>
            Nous vous répondrons dans un délai maximum d'un mois. Une copie de votre pièce 
            d'identité pourra être demandée pour vérifier votre identité.
          </p>
        </section>

        <section className="legal-section">
          <h2>10. Sécurité des données</h2>
          <p>
            Nous mettons en œuvre des mesures techniques et organisationnelles appropriées 
            pour protéger vos données personnelles :
          </p>
          <ul>
            <li><strong>Chiffrement :</strong> protocole SSL/TLS pour toutes les transactions</li>
            <li><strong>Authentification :</strong> mots de passe cryptés, double authentification (optionnel)</li>
            <li><strong>Contrôle d'accès :</strong> accès restreint aux seules personnes autorisées</li>
            <li><strong>Sauvegardes :</strong> sauvegardes régulières et sécurisées</li>
            <li><strong>Surveillance :</strong> détection et prévention des intrusions</li>
            <li><strong>Mises à jour :</strong> correctifs de sécurité réguliers</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>11. Cookies et technologies similaires</h2>
          <p>
            Notre site utilise des cookies pour améliorer votre expérience. Pour plus 
            d'informations, consultez notre <a href="/legal/cookies">Politique des Cookies</a>.
          </p>
        </section>

        <section className="legal-section">
          <h2>12. Mineurs</h2>
          <p>
            Notre site est destiné aux personnes âgées de 18 ans et plus. Si vous avez 
            moins de 18 ans, vous devez obtenir l'autorisation de vos parents ou tuteurs 
            légaux avant de créer un compte ou de passer commande.
          </p>
        </section>

        <section className="legal-section">
          <h2>13. Modifications de la politique</h2>
          <p>
            Nous nous réservons le droit de modifier cette politique de confidentialité 
            à tout moment. Les modifications seront publiées sur cette page avec une 
            nouvelle date de mise à jour. Nous vous encourageons à consulter régulièrement 
            cette page.
          </p>
        </section>

        <section className="legal-section">
          <h2>14. Réclamation</h2>
          <p>
            Si vous estimez que vos droits ne sont pas respectés, vous pouvez introduire 
            une réclamation auprès de la Commission Nationale de l'Informatique et des 
            Libertés (CNIL) :
          </p>
          <ul>
            <li><strong>Site web :</strong> <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer">www.cnil.fr</a></li>
            <li><strong>Adresse :</strong> CNIL, 3 Place de Fontenoy, TSA 80715, 75334 PARIS CEDEX 07</li>
            <li><strong>Téléphone :</strong> +33 (0)1 53 73 22 22</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>15. Contact</h2>
          <p>
            Pour toute question concernant cette politique de confidentialité ou le 
            traitement de vos données personnelles :
          </p>
          <ul>
            <li><strong>DPO :</strong> dpo@techstore-pro.fr</li>
            <li><strong>Service Client :</strong> contact@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
            <li><strong>Courrier :</strong> TechStore Pro - Service RGPD, 42 Avenue des Champs-Élysées, 75008 Paris</li>
          </ul>
        </section>
      </div>
    </div>
  );
}

