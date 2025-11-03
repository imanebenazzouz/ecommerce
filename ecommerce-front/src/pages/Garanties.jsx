import React from "react";
// Page d'informations Garanties (légales et constructeur).
import "../styles/LegalPages.css";

export default function Garanties() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Garanties</h1>
        <p className="last-update">
          Tous nos produits bénéficient de garanties légales et constructeur
        </p>

        <section className="legal-section">
          <h2>Garanties légales</h2>
          <p>
            En France, tous les produits neufs bénéficient de deux garanties légales 
            automatiques et gratuites, en plus de la garantie commerciale du fabricant.
          </p>

          <div className="info-box">
            <p>
              <strong>Important :</strong> Ces garanties légales sont indépendantes 
              et cumulatives. Vous pouvez les invoquer même si la garantie commerciale 
              est expirée.
            </p>
          </div>
        </section>

        <section className="legal-section">
          <h2>📋 Garantie légale de conformité</h2>
          
          <h3>Durée</h3>
          <p>
            <strong>2 ans</strong> à compter de la délivrance du bien (réception du produit)
          </p>

          <h3>Qu'est-ce qu'un défaut de conformité ?</h3>
          <p>
            Un bien est considéré comme non conforme s'il présente un défaut existant 
            au moment de la livraison, même s'il se révèle après la vente :
          </p>
          <ul>
            <li>Le produit ne correspond pas à la description</li>
            <li>Le produit n'est pas apte à l'usage habituellement attendu</li>
            <li>Le produit ne présente pas les qualités annoncées</li>
            <li>Le produit n'est pas livré avec les accessoires mentionnés</li>
          </ul>

          <h3>Présomption d'antériorité</h3>
          <ul>
            <li>
              <strong>Défaut constaté dans les 24 mois :</strong> Il est présumé exister 
              au moment de la livraison (vous n'avez pas à le prouver)
            </li>
            <li>
              <strong>Après 24 mois :</strong> Vous devrez prouver que le défaut existait 
              à la livraison
            </li>
          </ul>

          <h3>Vos droits</h3>
          <p>
            En cas de défaut de conformité, vous pouvez demander :
          </p>
          <ol>
            <li>
              <strong>La réparation ou le remplacement du bien</strong> (sans frais, 
              dans un délai de 30 jours maximum)
            </li>
            <li>
              <strong>À défaut, la réduction du prix ou la restitution intégrale</strong> 
              (remboursement) contre retour du produit
            </li>
          </ol>

          <h3>Base légale</h3>
          <p>
            Articles L217-4 à L217-14 du Code de la consommation
          </p>
        </section>

        <section className="legal-section">
          <h2>Garantie des vices cachés</h2>
          
          <h3>Durée</h3>
          <p>
            <strong>2 ans</strong> à compter de la découverte du vice
          </p>

          <h3>Qu'est-ce qu'un vice caché ?</h3>
          <p>
            Un vice caché est un défaut :
          </p>
          <ul>
            <li>Qui existait avant l'achat</li>
            <li>Qui n'était pas apparent lors de l'achat</li>
            <li>Qui rend le produit impropre à l'usage auquel on le destine</li>
            <li>Qui diminue tellement l'usage du produit que vous ne l'auriez pas 
                acheté ou auriez payé moins cher</li>
          </ul>

          <h3>Vos droits</h3>
          <p>
            En cas de vice caché, vous pouvez demander :
          </p>
          <ul>
            <li>
              <strong>Le remboursement intégral</strong> (restitution du prix payé) 
              et restitution du produit
            </li>
            <li>
              <strong>Ou une réduction du prix</strong> et conservation du produit
            </li>
          </ul>

          <h3>Délai pour agir</h3>
          <p>
            Vous avez 2 ans à compter de la découverte du vice pour agir en justice.
          </p>

          <h3>Base légale</h3>
          <p>
            Articles 1641 à 1649 du Code civil
          </p>
        </section>

        <section className="legal-section">
          <h2>🏭 Garantie commerciale constructeur</h2>
          
          <h3>Qu'est-ce que c'est ?</h3>
          <p>
            La garantie commerciale (ou garantie fabricant) est une garantie 
            supplémentaire, facultative, offerte par le fabricant ou le vendeur.
          </p>

          <h3>Durée</h3>
          <p>
            La durée varie selon les fabricants et les produits (généralement 1 à 3 ans). 
            Elle est indiquée sur la fiche produit et dans la documentation fournie.
          </p>

          <h3>Couverture</h3>
          <p>
            La garantie constructeur couvre généralement :
          </p>
          <ul>
            <li>Les défauts de fabrication</li>
            <li>Les pannes liées à une utilisation normale</li>
            <li>Les vices de matériaux ou de main d'œuvre</li>
          </ul>

          <h3>Exclusions courantes</h3>
          <p>
            Ne sont généralement pas couverts :
          </p>
          <ul>
            <li>L'usure normale</li>
            <li>Les dommages accidentels</li>
            <li>Une mauvaise utilisation</li>
            <li>Les réparations par un tiers non agréé</li>
            <li>Les pièces consommables (piles, cartouches, etc.)</li>
          </ul>

          <h3>Comment l'activer ?</h3>
          <p>
            Pour bénéficier de la garantie constructeur :
          </p>
          <ol>
            <li>Conservez votre facture d'achat</li>
            <li>Enregistrez votre produit sur le site du fabricant (si applicable)</li>
            <li>En cas de problème, contactez le service après-vente du fabricant</li>
          </ol>
        </section>

        <section className="legal-section">
          <h2>Comment faire valoir vos garanties ?</h2>
          
          <h3>Étape 1 : Contactez-nous</h3>
          <p>
            Dès que vous constatez un problème, contactez notre service client :
          </p>
          <ul>
            <li><strong>Email :</strong> sav@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 XX XX XX XX</li>
            <li><strong>Formulaire :</strong> <a href="/support">Page de contact</a></li>
          </ul>

          <h3>Étape 2 : Documents à fournir</h3>
          <p>
            Préparez les éléments suivants :
          </p>
          <ul>
            <li>Votre numéro de commande</li>
            <li>Votre facture d'achat</li>
            <li>Photos ou vidéos du défaut constaté</li>
            <li>Description détaillée du problème</li>
          </ul>

          <h3>Étape 3 : Diagnostic</h3>
          <p>
            Notre équipe analyse votre demande et vous propose une solution :
          </p>
          <ul>
            <li>Réparation du produit</li>
            <li>Échange contre un produit identique ou équivalent</li>
            <li>Remboursement (si réparation/échange impossible)</li>
          </ul>

          <h3>Étape 4 : Retour du produit</h3>
          <p>
            Si un retour est nécessaire :
          </p>
          <ul>
            <li>Nous vous fournissons une étiquette de retour prépayée</li>
            <li>Emballez soigneusement le produit</li>
            <li>Déposez le colis dans un point relais</li>
          </ul>

          <h3>Étape 5 : Solution</h3>
          <p>
            Selon le diagnostic :
          </p>
          <ul>
            <li><strong>Réparation :</strong> Nous réparons et vous renvoyons le produit</li>
            <li><strong>Échange :</strong> Nous vous envoyons un produit neuf</li>
            <li><strong>Remboursement :</strong> Nous remboursons le montant sur votre compte</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>Délais</h2>
          
          <h3>Traitement de votre demande</h3>
          <ul>
            <li><strong>Réponse initiale :</strong> Sous 48h ouvrées</li>
            <li><strong>Réparation ou échange :</strong> Maximum 30 jours</li>
            <li><strong>Remboursement :</strong> Sous 14 jours après retour</li>
          </ul>

          <div className="info-box">
            <p>
              <strong>Produit de remplacement temporaire :</strong> Pour certains produits 
              essentiels (ex : électroménager), nous pouvons vous proposer un produit de 
              remplacement pendant la durée de la réparation.
            </p>
          </div>
        </section>

        <section className="legal-section">
          <h2>Frais</h2>
          
          <h3>Garantie légale</h3>
          <p>
            La mise en œuvre des garanties légales est <strong>totalement gratuite</strong> :
          </p>
          <ul>
            <li>Pas de frais de retour</li>
            <li>Pas de frais de diagnostic</li>
            <li>Pas de frais de réparation</li>
            <li>Pas de frais de renvoi</li>
          </ul>

          <h3>Garantie commerciale</h3>
          <p>
            Les conditions varient selon les fabricants. Consultez les conditions 
            particulières de la garantie constructeur fournie avec votre produit.
          </p>
        </section>

        <section className="legal-section">
          <h2>Conservation des documents</h2>
          <p>
            Pour faciliter la gestion de vos garanties, conservez :
          </p>
          <ul>
            <li>
              <strong>La facture d'achat :</strong> Indispensable pour toute réclamation 
              (disponible dans votre compte client)
            </li>
            <li>
              <strong>Le certificat de garantie :</strong> Fourni avec certains produits
            </li>
            <li>
              <strong>Le mode d'emploi :</strong> Prouve une utilisation conforme
            </li>
            <li>
              <strong>L'emballage d'origine :</strong> Utile en cas de retour
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>❓ Questions fréquentes</h2>
          
          <h3>Quelle garantie choisir ?</h3>
          <p>
            Vous n'avez pas à choisir ! Les garanties légales s'appliquent automatiquement 
            et vous pouvez les cumuler avec la garantie commerciale.
          </p>

          <h3>La garantie fonctionne-t-elle si je déménage ?</h3>
          <p>
            Oui, les garanties légales sont attachées au produit, pas à l'adresse. 
            Pensez à mettre à jour vos coordonnées dans votre compte client.
          </p>

          <h3>Puis-je faire réparer mon produit par un tiers ?</h3>
          <p>
            Oui, mais cela peut annuler la garantie constructeur. En revanche, les 
            garanties légales restent applicables si le défaut existait avant la réparation.
          </p>

          <h3>Le produit est cassé, suis-je couvert ?</h3>
          <p>
            Cela dépend :
          </p>
          <ul>
            <li><strong>Défaut de fabrication :</strong> Oui, couvert par les garanties</li>
            <li><strong>Casse accidentelle :</strong> Non couvert par les garanties légales</li>
            <li><strong>Produit mal emballé à l'envoi :</strong> Oui, nous sommes responsables</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>Service Après-Vente</h2>
          <p>
            Notre équipe SAV est à votre disposition pour toute question :
          </p>
          <ul>
            <li><strong>Email :</strong> sav@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47 (Lun-Ven : 9h-18h)</li>
            <li><strong>Chat en ligne :</strong> Disponible sur notre site</li>
            <li><strong>Formulaire :</strong> <a href="/support">Page de contact</a></li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>📚 Textes de référence</h2>
          <ul>
            <li>
              <strong>Garantie de conformité :</strong> Articles L217-4 à L217-14 
              du Code de la consommation
            </li>
            <li>
              <strong>Garantie des vices cachés :</strong> Articles 1641 à 1649 
              du Code civil
            </li>
            <li>
              <strong>Garantie commerciale :</strong> Articles L217-15 à L217-17 
              du Code de la consommation
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}

