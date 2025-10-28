import React, { useState } from "react";
// Page FAQ: catégories et questions/réponses avec accordéon.
import "../styles/LegalPages.css";

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      category: "Commande",
      questions: [
        {
          q: "Comment passer une commande ?",
          a: "Pour passer commande, parcourez notre catalogue, ajoutez les produits souhaités à votre panier, puis cliquez sur 'Passer la commande'. Vous devrez créer un compte ou vous connecter, puis renseigner vos informations de livraison et de paiement."
        },
        {
          q: "Puis-je modifier ma commande après validation ?",
          a: "Une fois votre commande validée et le paiement effectué, il n'est plus possible de la modifier. Cependant, vous pouvez contacter notre service client dans les plus brefs délais, et nous ferons notre possible pour répondre à votre demande."
        },
        {
          q: "Comment annuler ma commande ?",
          a: "Si votre commande n'a pas encore été expédiée, vous pouvez l'annuler depuis votre compte client (section 'Mes commandes') ou en contactant notre service client. Une fois expédiée, vous devrez exercer votre droit de rétractation."
        }
      ]
    },
    {
      category: "Paiement",
      questions: [
        {
          q: "Quels moyens de paiement acceptez-vous ?",
          a: "Nous acceptons les cartes bancaires Visa, Mastercard et American Express. Tous les paiements sont sécurisés via notre prestataire de paiement certifié PCI-DSS."
        },
        {
          q: "Le paiement est-il sécurisé ?",
          a: "Oui, absolument. Nous utilisons le protocole SSL/TLS pour crypter toutes les données sensibles. Vos informations bancaires ne sont jamais stockées sur nos serveurs et sont directement traitées par notre prestataire de paiement sécurisé."
        },
        {
          q: "Quand suis-je débité ?",
          a: "Votre carte bancaire est débitée immédiatement lors de la validation de votre commande."
        }
      ]
    },
    {
      category: "Livraison",
      questions: [
        {
          q: "Quels sont les délais de livraison ?",
          a: "Les délais de livraison sont de 3-5 jours ouvrés pour la livraison standard en France métropolitaine, et 24-48h pour la livraison express. Ces délais sont donnés à titre indicatif."
        },
        {
          q: "Comment suivre ma commande ?",
          a: "Dès l'expédition de votre commande, vous recevrez un email avec un numéro de suivi. Vous pouvez également suivre votre commande depuis votre compte client dans la section 'Mes commandes'."
        },
        {
          q: "Livrez-vous à l'international ?",
          a: "Actuellement, nous livrons uniquement en France métropolitaine, en Corse et dans les DOM-TOM. Nous travaillons à étendre nos services à l'international prochainement."
        },
        {
          q: "Que faire si je ne suis pas là pour réceptionner mon colis ?",
          a: "Si vous êtes absent lors de la livraison, le transporteur laissera un avis de passage. Votre colis sera généralement déposé dans un point relais proche ou au bureau de poste le plus proche. Vous aurez alors 14 jours pour le récupérer."
        }
      ]
    },
    {
      category: "Retours et Remboursements",
      questions: [
        {
          q: "Comment retourner un produit ?",
          a: "Vous disposez de 14 jours à compter de la réception pour exercer votre droit de rétractation. Connectez-vous à votre compte, allez dans 'Mes commandes', sélectionnez la commande concernée et cliquez sur 'Retourner un produit'. Pour plus de détails, consultez notre page 'Droit de Rétractation'."
        },
        {
          q: "Les retours sont-ils gratuits ?",
          a: "Les frais de retour sont à votre charge, sauf si le produit est défectueux ou si nous avons commis une erreur dans votre commande."
        },
        {
          q: "Quand serais-je remboursé ?",
          a: "Une fois que nous avons reçu et vérifié votre retour, le remboursement est effectué sous 14 jours maximum sur le moyen de paiement utilisé lors de l'achat. Le délai d'affichage sur votre compte bancaire peut prendre 3-5 jours ouvrés supplémentaires."
        },
        {
          q: "Puis-je échanger un produit ?",
          a: "Nous ne proposons pas d'échange direct. Pour recevoir un produit différent, vous devez retourner le produit initial pour remboursement, puis passer une nouvelle commande."
        }
      ]
    },
    {
      category: "Compte Client",
      questions: [
        {
          q: "Dois-je créer un compte pour commander ?",
          a: "Oui, la création d'un compte est nécessaire pour passer commande. Cela vous permet de suivre vos commandes, gérer vos adresses et accéder à votre historique d'achats."
        },
        {
          q: "J'ai oublié mon mot de passe, que faire ?",
          a: "Sur la page de connexion, cliquez sur 'Mot de passe oublié ?'. Entrez votre adresse email, et vous recevrez un lien pour réinitialiser votre mot de passe."
        },
        {
          q: "Comment modifier mes informations personnelles ?",
          a: "Connectez-vous à votre compte et accédez à la section 'Mon profil' où vous pourrez modifier vos informations personnelles, adresses et mot de passe."
        },
        {
          q: "Comment supprimer mon compte ?",
          a: "Pour supprimer votre compte, contactez notre service client à dpo@mon-ecommerce.fr. Conformément au RGPD, nous supprimerons vos données personnelles sous 30 jours."
        }
      ]
    },
    {
      category: "Produits",
      questions: [
        {
          q: "Les produits sont-ils garantis ?",
          a: "Oui, tous nos produits bénéficient de la garantie légale de conformité (2 ans) et de la garantie contre les vices cachés. Certains produits peuvent également avoir une garantie constructeur."
        },
        {
          q: "Comment connaître la disponibilité d'un produit ?",
          a: "La disponibilité est indiquée sur chaque fiche produit. Si un produit est en rupture de stock, vous pouvez vous inscrire pour être notifié de son retour en stock."
        },
        {
          q: "Proposez-vous des promotions ?",
          a: "Oui, nous proposons régulièrement des promotions et offres spéciales. Inscrivez-vous à notre newsletter pour être informé en avant-première."
        }
      ]
    },
    {
      category: "Sécurité et Confidentialité",
      questions: [
        {
          q: "Mes données personnelles sont-elles protégées ?",
          a: "Oui, nous prenons la protection de vos données très au sérieux. Nous sommes conformes au RGPD et utilisons des technologies de cryptage avancées. Pour plus d'informations, consultez notre Politique de Confidentialité."
        },
        {
          q: "Utilisez-vous des cookies ?",
          a: "Oui, nous utilisons des cookies pour améliorer votre expérience de navigation et analyser le trafic de notre site. Vous pouvez gérer vos préférences cookies à tout moment. Consultez notre Politique des Cookies pour plus de détails."
        },
        {
          q: "Comment exercer mes droits RGPD ?",
          a: "Vous pouvez exercer vos droits d'accès, de rectification, de suppression et d'opposition en nous contactant à dpo@mon-ecommerce.fr. Pour plus d'informations, consultez notre Politique de Confidentialité."
        }
      ]
    },
    {
      category: "Service Client",
      questions: [
        {
          q: "Comment contacter le service client ?",
          a: "Vous pouvez nous contacter par email à contact@mon-ecommerce.fr, par téléphone au +33 (0)1 XX XX XX XX (du lundi au vendredi, 9h-18h), ou via notre formulaire de contact."
        },
        {
          q: "Quels sont vos horaires ?",
          a: "Notre service client est disponible du lundi au vendredi de 9h à 18h, et le samedi de 10h à 17h. En dehors de ces horaires, vous pouvez nous envoyer un email ou utiliser notre formulaire de contact."
        },
        {
          q: "Puis-je venir récupérer ma commande en magasin ?",
          a: "Non, nous sommes un site de vente en ligne uniquement. Nous n'avons pas de magasin physique pour le moment."
        }
      ]
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  let questionIndex = 0;

  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Questions Fréquentes (FAQ)</h1>
        <p className="last-update">
          Vous trouverez ici les réponses aux questions les plus fréquemment posées.
          Si vous ne trouvez pas la réponse à votre question, n'hésitez pas à{" "}
          <a href="/support">contacter notre service client</a>.
        </p>

        {faqs.map((category, catIndex) => (
          <div key={catIndex} className="legal-section">
            <h2>{category.category}</h2>
            <div style={{ marginTop: 20 }}>
              {category.questions.map((faq) => {
                const currentIndex = questionIndex++;
                const isOpen = openIndex === currentIndex;
                
                return (
                  <div
                    key={currentIndex}
                    style={{
                      marginBottom: 15,
                      border: "1px solid #e5e7eb",
                      borderRadius: 8,
                      overflow: "hidden",
                      transition: "all 0.3s ease"
                    }}
                  >
                    <button
                      onClick={() => toggleFAQ(currentIndex)}
                      style={{
                        width: "100%",
                        padding: "15px 20px",
                        background: isOpen ? "#eff6ff" : "white",
                        border: "none",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        cursor: "pointer",
                        fontSize: "1rem",
                        fontWeight: 600,
                        color: "#1f2937",
                        textAlign: "left",
                        transition: "background 0.2s ease"
                      }}
                    >
                      <span>{faq.q}</span>
                      <span
                        style={{
                          fontSize: "1.5rem",
                          color: "#3b82f6",
                          transition: "transform 0.3s ease",
                          transform: isOpen ? "rotate(45deg)" : "rotate(0deg)"
                        }}
                      >
                        +
                      </span>
                    </button>
                    {isOpen && (
                      <div
                        style={{
                          padding: "15px 20px",
                          background: "#f9fafb",
                          borderTop: "1px solid #e5e7eb",
                          animation: "fadeIn 0.3s ease"
                        }}
                      >
                        <p style={{ margin: 0, lineHeight: 1.6, color: "#4b5563" }}>
                          {faq.a}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        <section className="legal-section" style={{ marginTop: 50 }}>
          <h2>Vous n'avez pas trouvé de réponse ?</h2>
          <p>
            Notre équipe de service client est là pour vous aider ! N'hésitez pas à nous contacter :
          </p>
          <ul>
            <li>
              <strong>Par email :</strong> contact@techstore-pro.fr
            </li>
            <li>
              <strong>Par téléphone :</strong> +33 (0)1 42 86 95 47 (Lun-Ven : 9h-18h, Sam : 10h-17h)
            </li>
            <li>
              <strong>Via notre formulaire :</strong> <a href="/support">Page de contact</a>
            </li>
          </ul>
        </section>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

