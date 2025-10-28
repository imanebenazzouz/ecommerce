import React from "react";
// Page légale: Mentions Légales.
import "../../styles/LegalPages.css";

export default function MentionsLegales() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Mentions Légales</h1>
        <p className="last-update">Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

        <section className="legal-section">
          <h2>1. Éditeur du site</h2>
          <p>
            Le site <strong>TechStore Pro</strong> est édité par :
          </p>
          <ul>
            <li><strong>Raison sociale :</strong> TechStore Pro SAS</li>
            <li><strong>Capital social :</strong> 150 000 €</li>
            <li><strong>Siège social :</strong> 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>RCS :</strong> Paris B 123 456 789</li>
            <li><strong>SIRET :</strong> 123 456 789 00012</li>
            <li><strong>TVA intracommunautaire :</strong> FR12 123456789</li>
            <li><strong>Email :</strong> contact@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>2. Directeur de la publication</h2>
          <p>
            <strong>Directeur de la publication :</strong> Marie Dubois
          </p>
          <p>
            <strong>Responsable de la rédaction :</strong> Pierre Martin
          </p>
        </section>

        <section className="legal-section">
          <h2>3. Hébergement</h2>
          <p>
            Le site est hébergé par :
          </p>
          <ul>
            <li><strong>Raison sociale :</strong> OVH SAS</li>
            <li><strong>Adresse :</strong> 2 rue Kellermann, 59100 Roubaix</li>
            <li><strong>Téléphone :</strong> +33 (0)9 72 10 10 07</li>
            <li><strong>Site web :</strong> www.ovh.com</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>4. Développement et maintenance technique</h2>
          <p>
            Le site a été développé et est maintenu par :
          </p>
          <ul>
            <li><strong>Société :</strong> WebDev Solutions</li>
            <li><strong>Email :</strong> technique@techstore-pro.fr</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>5. Propriété intellectuelle</h2>
          <p>
            L'ensemble du contenu de ce site (textes, images, vidéos, logos, icônes, etc.) 
            est la propriété exclusive de TechStore Pro SAS, sauf mention contraire.
          </p>
          <p>
            Toute reproduction, distribution, modification, adaptation, retransmission ou 
            publication de ces différents éléments est strictement interdite sans l'accord 
            exprès par écrit de TechStore Pro SAS.
          </p>
          <p>
            Cette représentation ou reproduction, par quelque procédé que ce soit, constitue 
            une contrefaçon sanctionnée par les articles L.335-2 et suivants du Code de la 
            propriété intellectuelle.
          </p>
        </section>

        <section className="legal-section">
          <h2>6. Crédits</h2>
          <p>
            <strong>Conception et design :</strong> TechStore Pro SAS
          </p>
          <p>
            <strong>Photographies :</strong> Unsplash, Pexels, Shutterstock
          </p>
          <p>
            <strong>Icônes et illustrations :</strong> Feather Icons, Heroicons
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Protection des données personnelles</h2>
          <p>
            Conformément au Règlement Général sur la Protection des Données (RGPD) 
            et à la loi Informatique et Libertés, vous disposez d'un droit d'accès, 
            de rectification, de suppression et d'opposition aux données personnelles 
            vous concernant.
          </p>
          <p>
            Pour exercer ces droits ou pour toute question sur le traitement de vos données, 
            vous pouvez contacter notre Délégué à la Protection des Données (DPO) :
          </p>
          <ul>
            <li><strong>Email DPO :</strong> dpo@techstore-pro.fr</li>
            <li><strong>Courrier :</strong> TechStore Pro - DPO, 42 Avenue des Champs-Élysées, 75008 Paris</li>
          </ul>
          <p>
            Pour plus d'informations, consultez notre{" "}
            <a href="/legal/confidentialite">Politique de Confidentialité</a>.
          </p>
        </section>

        <section className="legal-section">
          <h2>8. Cookies</h2>
          <p>
            Le site utilise des cookies pour améliorer votre expérience de navigation 
            et réaliser des statistiques de visites. Vous pouvez à tout moment désactiver 
            ces cookies depuis les paramètres de votre navigateur.
          </p>
          <p>
            Pour plus d'informations, consultez notre{" "}
            <a href="/legal/cookies">Politique des Cookies</a>.
          </p>
        </section>

        <section className="legal-section">
          <h2>9. Limitation de responsabilité</h2>
          <p>
            TechStore Pro SAS s'efforce d'assurer au mieux l'exactitude et la mise à jour 
            des informations diffusées sur ce site. Toutefois, elle ne peut garantir 
            l'exactitude, la précision ou l'exhaustivité des informations mises à 
            disposition sur ce site.
          </p>
          <p>
            TechStore Pro SAS ne pourra être tenue responsable des dommages directs ou 
            indirects qui pourraient résulter de l'accès au site ou de l'utilisation du 
            site et de ses services.
          </p>
        </section>

        <section className="legal-section">
          <h2>10. Liens hypertextes</h2>
          <p>
            Le site peut contenir des liens vers d'autres sites. TechStore Pro SAS 
            n'exerce aucun contrôle sur ces sites et décline toute responsabilité quant 
            à l'accès, au contenu ou à l'utilisation de ces sites.
          </p>
        </section>

        <section className="legal-section">
          <h2>11. Droit applicable et juridiction</h2>
          <p>
            Les présentes mentions légales sont régies par le droit français. En cas de 
            litige et à défaut d'accord amiable, le litige sera porté devant les tribunaux 
            français conformément aux règles de compétence en vigueur.
          </p>
        </section>

        <section className="legal-section">
          <h2>12. Contact</h2>
          <p>
            Pour toute question concernant les mentions légales, vous pouvez nous contacter :
          </p>
          <ul>
            <li><strong>Email :</strong> contact@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47</li>
            <li><strong>Courrier :</strong> TechStore Pro, Service Juridique, 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>Formulaire en ligne :</strong> <a href="/support">Page de contact</a></li>
          </ul>
        </section>
      </div>
    </div>
  );
}

