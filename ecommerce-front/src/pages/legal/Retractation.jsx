import React from "react";
// Page légale: Droit de Rétractation.
import "../../styles/LegalPages.css";

export default function Retractation() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Droit de Rétractation</h1>
        <p className="last-update">Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}</p>

        <section className="legal-section">
          <h2>1. Principe du droit de rétractation</h2>
          <p>
            Conformément aux articles L221-18 et suivants du Code de la consommation, 
            vous disposez d'un délai de <strong>14 jours calendaires</strong> pour exercer 
            votre droit de rétractation sans avoir à justifier de motifs ni à payer de pénalité.
          </p>
          <p>
            Ce droit s'applique à tous les achats effectués à distance sur notre site internet.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Délai de rétractation</h2>
          <p>
            Le délai de rétractation expire 14 jours :
          </p>
          <ul>
            <li>
              <strong>Pour les biens :</strong> après le jour où vous-même, ou un tiers 
              autre que le transporteur et désigné par vous, prend physiquement possession 
              du dernier bien.
            </li>
            <li>
              <strong>Pour les services :</strong> après le jour de la conclusion du contrat.
            </li>
            <li>
              <strong>Commande multiple avec livraison échelonnée :</strong> après le jour 
              où vous-même, ou un tiers désigné par vous, prend possession du dernier bien.
            </li>
          </ul>
          <p>
            <strong>Exemple :</strong> Si vous recevez votre colis le lundi 1er janvier, 
            vous avez jusqu'au lundi 15 janvier à minuit pour exercer votre droit de rétractation.
          </p>
        </section>

        <section className="legal-section">
          <h2>3. Comment exercer votre droit de rétractation ?</h2>
          
          <h3>3.1 Déclaration de rétractation</h3>
          <p>
            Pour exercer votre droit de rétractation, vous devez nous notifier votre 
            décision de vous rétracter par une déclaration claire et non équivoque.
          </p>
          
          <h3>3.2 Moyens de notification</h3>
          <p>
            Vous pouvez nous informer de votre décision de rétractation par :
          </p>
          <ul>
            <li>
              <strong>Email :</strong> retractation@mon-ecommerce.fr
            </li>
            <li>
              <strong>Courrier postal :</strong> Mon e-commerce - Service Rétractation, 
              [Adresse complète]
            </li>
            <li>
              <strong>Formulaire en ligne :</strong> Depuis votre compte client, 
              section "Mes commandes" &gt; "Retourner un produit"
            </li>
            <li>
              <strong>Formulaire de rétractation :</strong> Vous pouvez utiliser le 
              formulaire type ci-dessous (non obligatoire)
            </li>
          </ul>

          <h3>3.3 Formulaire type de rétractation</h3>
          <div className="retractation-form">
            <p><em>(Veuillez compléter et renvoyer le présent formulaire uniquement si vous souhaitez vous rétracter du contrat)</em></p>
            <p>À l'attention de TechStore Pro - Service Rétractation :</p>
            <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
              <li>• Je vous notifie par la présente ma rétractation du contrat portant sur la vente du bien ci-dessous :</li>
              <li>• Numéro de commande : _________________</li>
              <li>• Commandé le : _________________</li>
              <li>• Reçu le : _________________</li>
              <li>• Nom du consommateur : _________________</li>
              <li>• Adresse du consommateur : _________________</li>
              <li>• Signature du consommateur (uniquement en cas de notification sur papier) : _________________</li>
              <li>• Date : _________________</li>
            </ul>
          </div>
        </section>

        <section className="legal-section">
          <h2>4. Effets de la rétractation</h2>
          
          <h3>4.1 Remboursement</h3>
          <p>
            En cas de rétractation de votre part, nous vous rembourserons tous les 
            paiements reçus de vous, y compris les frais de livraison (à l'exception 
            des frais supplémentaires si vous avez choisi un mode de livraison autre 
            que le mode standard proposé par nous).
          </p>
          
          <h3>4.2 Délai de remboursement</h3>
          <p>
            Nous procéderons au remboursement en utilisant le même moyen de paiement 
            que celui utilisé lors de la transaction initiale, sauf accord contraire 
            de votre part. Ce remboursement n'occasionnera pas de frais pour vous.
          </p>
          <p>
            Nous pouvons différer le remboursement jusqu'à :
          </p>
          <ul>
            <li>Récupération des biens, ou</li>
            <li>Jusqu'à ce que vous ayez fourni une preuve d'expédition des biens</li>
          </ul>
          <p>
            La date retenue étant celle du premier de ces faits.
          </p>

          <h3>4.3 Frais de retour</h3>
          <p>
            <strong>Important :</strong> Les frais directs de renvoi des biens sont à votre charge.
          </p>
          <p>
            Montant estimé des frais de retour : variable selon le poids et la destination 
            (généralement entre 5€ et 15€ pour un envoi en France métropolitaine).
          </p>
        </section>

        <section className="legal-section">
          <h2>5. Conditions de retour des produits</h2>
          
          <h3>5.1 État des produits</h3>
          <p>
            Pour que votre rétractation soit acceptée, les produits doivent être retournés :
          </p>
          <ul>
            <li><strong>Dans leur emballage d'origine :</strong> intact et non endommagé</li>
            <li><strong>Complets :</strong> avec tous les accessoires, notices et étiquettes</li>
            <li><strong>Non utilisés :</strong> sauf pour tester le produit</li>
            <li><strong>En parfait état de revente :</strong> propres et non abîmés</li>
          </ul>

          <h3>5.2 Dépréciation des biens</h3>
          <p>
            Votre responsabilité n'est engagée qu'à l'égard de la dépréciation des biens 
            résultant de manipulations autres que celles nécessaires pour établir la nature, 
            les caractéristiques et le bon fonctionnement de ces biens.
          </p>
          <p>
            <strong>En pratique :</strong> Vous pouvez déballer et tester le produit comme 
            vous le feriez en magasin, mais si vous l'utilisez de manière excessive et que 
            cela entraîne une dépréciation, nous pourrons déduire un montant du remboursement.
          </p>

          <h3>5.3 Procédure de retour</h3>
          <ol>
            <li>Notifiez-nous votre intention de vous rétracter (voir section 3)</li>
            <li>Emballez soigneusement le(s) produit(s) dans l'emballage d'origine</li>
            <li>Joignez une copie de votre facture et du formulaire de rétractation</li>
            <li>Renvoyez le colis à l'adresse indiquée :</li>
          </ol>
          <div className="address-box">
            <p><strong>Adresse de retour :</strong></p>
            <p>
              Mon e-commerce - Service Retours<br />
              [Adresse complète de retour]<br />
              [Code postal] [Ville]<br />
              France
            </p>
          </div>
          <p>
            <strong>Conseil :</strong> Conservez votre preuve d'expédition et optez pour 
            un envoi avec suivi pour sécuriser votre retour.
          </p>
        </section>

        <section className="legal-section">
          <h2>6. Exceptions au droit de rétractation</h2>
          <p>
            Conformément à l'article L221-28 du Code de la consommation, le droit de 
            rétractation ne s'applique pas aux contrats suivants :
          </p>
          <ul>
            <li>
              <strong>Biens confectionnés selon les spécifications du consommateur :</strong> 
              articles personnalisés ou faits sur mesure
            </li>
            <li>
              <strong>Biens susceptibles de se détériorer rapidement :</strong> produits 
              alimentaires frais, fleurs
            </li>
            <li>
              <strong>Biens descellés après livraison :</strong> produits non retournables 
              pour raisons d'hygiène ou de protection de la santé (sous-vêtements, cosmétiques, etc.)
            </li>
            <li>
              <strong>Enregistrements audio ou vidéo descellés :</strong> CD, DVD descellés
            </li>
            <li>
              <strong>Journaux, périodiques ou magazines :</strong> sauf contrat d'abonnement
            </li>
            <li>
              <strong>Biens mélangés de manière indissociable :</strong> après livraison 
              avec d'autres articles
            </li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>7. Cas particuliers</h2>
          
          <h3>7.1 Produit défectueux</h3>
          <p>
            Si vous recevez un produit défectueux ou non conforme à votre commande, 
            les frais de retour seront à notre charge. Contactez immédiatement notre 
            service client.
          </p>

          <h3>7.2 Erreur de livraison</h3>
          <p>
            En cas d'erreur dans la livraison (produit différent de celui commandé), 
            nous prendrons en charge l'intégralité des frais de retour et de réexpédition.
          </p>

          <h3>7.3 Délai de rétractation prolongé</h3>
          <p>
            Durant certaines périodes promotionnelles (Noël, soldes, etc.), nous pouvons 
            prolonger volontairement le délai de rétractation. Ces conditions particulières 
            seront mentionnées lors de votre achat.
          </p>
        </section>

        <section className="legal-section">
          <h2>8. Suivi de votre rétractation</h2>
          <p>
            Vous pouvez suivre l'état de votre demande de rétractation depuis votre compte client :
          </p>
          <ul>
            <li>Connexion à votre compte</li>
            <li>Section "Mes commandes"</li>
            <li>Cliquez sur la commande concernée</li>
            <li>Consultez le statut du retour</li>
          </ul>
          <p>
            Vous recevrez également des emails de confirmation à chaque étape :
          </p>
          <ul>
            <li>Réception de votre demande de rétractation</li>
            <li>Réception du colis retourné dans nos entrepôts</li>
            <li>Traitement du retour et acceptation</li>
            <li>Remboursement effectué</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>9. Questions fréquentes</h2>
          
          <h3>Q : Puis-je me rétracter après avoir ouvert le produit ?</h3>
          <p>
            <strong>R :</strong> Oui, vous pouvez ouvrir l'emballage et tester le produit. 
            Seule une utilisation excessive pouvant entraîner une dépréciation peut affecter 
            votre remboursement.
          </p>

          <h3>Q : Combien de temps prend le remboursement ?</h3>
          <p>
            <strong>R :</strong> Une fois que nous avons reçu et vérifié votre retour, 
            le remboursement est effectué sous 14 jours maximum. Le délai d'affichage sur 
            votre compte bancaire dépend de votre banque (généralement 3-5 jours ouvrés).
          </p>

          <h3>Q : Dois-je renvoyer le produit dans son carton d'origine ?</h3>
          <p>
            <strong>R :</strong> Oui, si possible. Le produit doit être retourné avec 
            son emballage d'origine en bon état pour pouvoir être revendu.
          </p>

          <h3>Q : Qui paie les frais de retour ?</h3>
          <p>
            <strong>R :</strong> Les frais de retour sont à votre charge, sauf si le 
            produit est défectueux ou si nous avons fait une erreur de livraison.
          </p>
        </section>

        <section className="legal-section">
          <h2>10. Textes de référence</h2>
          <p>
            Le droit de rétractation est régi par les textes suivants :
          </p>
          <ul>
            <li>Articles L221-18 à L221-28 du Code de la consommation</li>
            <li>Directive européenne 2011/83/UE sur les droits des consommateurs</li>
            <li>Article L217-4 et suivants du Code de la consommation (garanties légales)</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>11. Contact</h2>
          <p>
            Pour toute question concernant votre droit de rétractation ou pour effectuer 
            un retour :
          </p>
          <ul>
            <li><strong>Email :</strong> retractation@techstore-pro.fr</li>
            <li><strong>Téléphone :</strong> +33 (0)1 42 86 95 47 (du lundi au vendredi, 9h-18h)</li>
            <li><strong>Courrier :</strong> TechStore Pro - Service Rétractation, 42 Avenue des Champs-Élysées, 75008 Paris</li>
            <li><strong>Formulaire en ligne :</strong> <a href="/support">Page de contact</a></li>
            <li><strong>Espace client :</strong> <a href="/orders">Mes commandes</a> &gt; Retourner un produit</li>
          </ul>
        </section>
      </div>
    </div>
  );
}

