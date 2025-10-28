import React from "react";
// Page légale: Politique des Cookies.
import "../../styles/LegalPages.css";

export default function Cookies() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Politique des Cookies</h1>
        <p className="last-update">Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

        <section className="legal-section">
          <h2>1. Qu'est-ce qu'un cookie ?</h2>
          <p>
            Un cookie est un petit fichier texte déposé sur votre terminal (ordinateur, 
            smartphone, tablette) lors de la visite d'un site web. Les cookies permettent 
            au site de reconnaître votre appareil et de mémoriser certaines informations 
            sur votre navigation.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Pourquoi utilisons-nous des cookies ?</h2>
          <p>
            Nous utilisons des cookies pour plusieurs raisons :
          </p>
          <ul>
            <li><strong>Fonctionnement du site :</strong> cookies essentiels pour la navigation</li>
            <li><strong>Mémorisation de vos préférences :</strong> langue, devise, panier</li>
            <li><strong>Analyse du trafic :</strong> amélioration de nos services</li>
            <li><strong>Sécurité :</strong> protection contre la fraude</li>
            <li><strong>Personnalisation :</strong> contenu adapté à vos intérêts</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>3. Types de cookies utilisés</h2>

          <h3>3.1 Cookies strictement nécessaires</h3>
          <p>
            Ces cookies sont indispensables au fonctionnement du site. Ils ne peuvent 
            pas être désactivés et ne nécessitent pas votre consentement.
          </p>
          <div className="cookie-table">
            <table>
              <thead>
                <tr>
                  <th>Cookie</th>
                  <th>Finalité</th>
                  <th>Durée</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>session_id</td>
                  <td>Identifiant de session utilisateur</td>
                  <td>Session</td>
                </tr>
                <tr>
                  <td>auth_token</td>
                  <td>Authentification sécurisée</td>
                  <td>7 jours</td>
                </tr>
                <tr>
                  <td>cart_id</td>
                  <td>Mémorisation du panier</td>
                  <td>30 jours</td>
                </tr>
                <tr>
                  <td>csrf_token</td>
                  <td>Protection contre les attaques CSRF</td>
                  <td>Session</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>3.2 Cookies de fonctionnalité</h3>
          <p>
            Ces cookies permettent d'améliorer votre expérience en mémorisant vos 
            préférences. Ils nécessitent votre consentement.
          </p>
          <div className="cookie-table">
            <table>
              <thead>
                <tr>
                  <th>Cookie</th>
                  <th>Finalité</th>
                  <th>Durée</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>language</td>
                  <td>Mémorisation de la langue choisie</td>
                  <td>12 mois</td>
                </tr>
                <tr>
                  <td>currency</td>
                  <td>Devise préférée</td>
                  <td>12 mois</td>
                </tr>
                <tr>
                  <td>preferences</td>
                  <td>Préférences d'affichage</td>
                  <td>12 mois</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>3.3 Cookies analytiques</h3>
          <p>
            Ces cookies nous permettent de comprendre comment les visiteurs utilisent 
            notre site. Ils nécessitent votre consentement.
          </p>
          <div className="cookie-table">
            <table>
              <thead>
                <tr>
                  <th>Cookie</th>
                  <th>Finalité</th>
                  <th>Durée</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>_ga</td>
                  <td>Google Analytics - Identifiant unique</td>
                  <td>13 mois</td>
                </tr>
                <tr>
                  <td>_gid</td>
                  <td>Google Analytics - Session</td>
                  <td>24 heures</td>
                </tr>
                <tr>
                  <td>analytics_session</td>
                  <td>Suivi des pages visitées</td>
                  <td>Session</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>3.4 Cookies publicitaires</h3>
          <p>
            Ces cookies permettent de vous proposer des publicités personnalisées. 
            Ils nécessitent votre consentement.
          </p>
          <div className="cookie-table">
            <table>
              <thead>
                <tr>
                  <th>Cookie</th>
                  <th>Finalité</th>
                  <th>Durée</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>ads_preferences</td>
                  <td>Ciblage publicitaire</td>
                  <td>13 mois</td>
                </tr>
                <tr>
                  <td>retargeting_id</td>
                  <td>Remarketing</td>
                  <td>90 jours</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="legal-section">
          <h2>4. Cookies tiers</h2>
          <p>
            Nous utilisons également des cookies de partenaires tiers pour améliorer 
            nos services :
          </p>
          <ul>
            <li>
              <strong>Google Analytics :</strong> analyse du trafic et du comportement 
              des utilisateurs. <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">
                Politique de confidentialité Google
              </a>
            </li>
            <li>
              <strong>Facebook Pixel :</strong> suivi des conversions publicitaires. 
              <a href="https://www.facebook.com/privacy/explanation" target="_blank" rel="noopener noreferrer">
                Politique de confidentialité Facebook
              </a>
            </li>
            <li>
              <strong>Stripe :</strong> traitement sécurisé des paiements. 
              <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer">
                Politique de confidentialité Stripe
              </a>
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>5. Gestion de vos préférences cookies</h2>
          
          <h3>5.1 Panneau de consentement</h3>
          <p>
            Lors de votre première visite, un bandeau vous permet de choisir les cookies 
            que vous acceptez. Vous pouvez modifier vos préférences à tout moment en 
            cliquant sur "Gérer les cookies" en bas de page.
          </p>

          <h3>5.2 Paramètres du navigateur</h3>
          <p>
            Vous pouvez également gérer les cookies directement depuis votre navigateur :
          </p>
          <ul>
            <li>
              <strong>Chrome :</strong> Paramètres &gt; Confidentialité et sécurité &gt; Cookies
            </li>
            <li>
              <strong>Firefox :</strong> Paramètres &gt; Vie privée et sécurité &gt; Cookies
            </li>
            <li>
              <strong>Safari :</strong> Préférences &gt; Confidentialité &gt; Cookies
            </li>
            <li>
              <strong>Edge :</strong> Paramètres &gt; Cookies et autorisations de site
            </li>
          </ul>

          <h3>5.3 Opposition aux cookies publicitaires</h3>
          <p>
            Vous pouvez vous opposer au ciblage publicitaire via :
          </p>
          <ul>
            <li>
              <strong>Plateforme française :</strong>{" "}
              <a href="https://www.youronlinechoices.com/fr/" target="_blank" rel="noopener noreferrer">
                www.youronlinechoices.com
              </a>
            </li>
            <li>
              <strong>Network Advertising Initiative :</strong>{" "}
              <a href="https://www.networkadvertising.org/choices/" target="_blank" rel="noopener noreferrer">
                www.networkadvertising.org
              </a>
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>6. Durée de conservation</h2>
          <p>
            Les cookies sont conservés pour une durée maximale de 13 mois conformément 
            aux recommandations de la CNIL. Votre consentement est valable 13 mois et 
            vous sera redemandé à l'expiration de ce délai.
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Conséquences du refus des cookies</h2>
          <p>
            Le refus de certains cookies peut impacter votre expérience de navigation :
          </p>
          <ul>
            <li>
              <strong>Cookies nécessaires :</strong> impossible de naviguer correctement 
              sur le site, de se connecter ou d'effectuer des achats
            </li>
            <li>
              <strong>Cookies de fonctionnalité :</strong> perte de vos préférences 
              (langue, devise) à chaque visite
            </li>
            <li>
              <strong>Cookies analytiques :</strong> aucun impact sur votre navigation, 
              mais nous aide moins à améliorer le site
            </li>
            <li>
              <strong>Cookies publicitaires :</strong> vous verrez toujours des publicités, 
              mais elles seront moins pertinentes
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>8. Technologies similaires</h2>
          <p>
            Outre les cookies, nous utilisons d'autres technologies de traçage :
          </p>
          <ul>
            <li>
              <strong>LocalStorage :</strong> stockage local de données non sensibles 
              (préférences d'interface)
            </li>
            <li>
              <strong>SessionStorage :</strong> données temporaires le temps de votre visite
            </li>
            <li>
              <strong>Web beacons :</strong> petites images invisibles pour le suivi des emails
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>9. Mises à jour de cette politique</h2>
          <p>
            Cette politique des cookies peut être mise à jour pour refléter les changements 
            dans nos pratiques ou pour d'autres raisons opérationnelles, légales ou 
            réglementaires. Nous vous encourageons à consulter régulièrement cette page.
          </p>
        </section>

        <section className="legal-section">
          <h2>10. Plus d'informations</h2>
          <p>
            Pour en savoir plus sur les cookies et la protection de votre vie privée :
          </p>
          <ul>
            <li>
              <strong>CNIL :</strong>{" "}
              <a href="https://www.cnil.fr/fr/cookies-et-autres-traceurs" target="_blank" rel="noopener noreferrer">
                Guide sur les cookies
              </a>
            </li>
            <li>
              <strong>Commission Européenne :</strong>{" "}
              <a href="https://ec.europa.eu/info/cookies_fr" target="_blank" rel="noopener noreferrer">
                Politique relative aux cookies
              </a>
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>11. Contact</h2>
          <p>
            Pour toute question concernant notre utilisation des cookies :
          </p>
          <ul>
            <li><strong>Email :</strong> dpo@techstore-pro.fr</li>
            <li><strong>Courrier :</strong> TechStore Pro - DPO, 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>Formulaire :</strong> <a href="/support">Page de contact</a></li>
          </ul>
        </section>
      </div>
    </div>
  );
}

