// Test de l'API de paiement depuis JavaScript
const API_BASE = 'http://localhost:8000';

async function testPaymentFlow() {
    console.log('🧪 Test du flux de paiement...');
    
    try {
        // 1. Connexion
        console.log('1. Connexion...');
        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'client@example.com',
                password: 'secret'
            })
        });
        
        const loginData = await loginResponse.json();
        if (!loginResponse.ok) {
            throw new Error(`Erreur de connexion: ${loginData.detail}`);
        }
        
        const token = loginData.token;
        console.log('✅ Connexion réussie');
        
        // 2. Ajouter au panier
        console.log('2. Ajout au panier...');
        const cartResponse = await fetch(`${API_BASE}/cart/add`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                product_id: 'bac6752c-8cf2-4feb-a40f-05b33d95b828',
                qty: 1
            })
        });
        
        if (!cartResponse.ok) {
            const cartData = await cartResponse.json();
            throw new Error(`Erreur panier: ${cartData.detail}`);
        }
        console.log('✅ Produit ajouté au panier');
        
        // 3. Créer une commande
        console.log('3. Création de commande...');
        const orderResponse = await fetch(`${API_BASE}/orders/checkout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const orderData = await orderResponse.json();
        if (!orderResponse.ok) {
            throw new Error(`Erreur commande: ${orderData.detail}`);
        }
        
        const orderId = orderData.order_id;
        console.log(`✅ Commande créée: ${orderId}`);
        
        // 4. Payer la commande
        console.log('4. Paiement...');
        const paymentResponse = await fetch(`${API_BASE}/orders/${orderId}/pay`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                card_number: '4242424242424242',
                exp_month: 12,
                exp_year: 2025,
                cvc: '123'
            })
        });
        
        const paymentData = await paymentResponse.json();
        if (!paymentResponse.ok) {
            throw new Error(`Erreur paiement: ${paymentData.detail}`);
        }
        
        console.log('✅ Paiement réussi!');
        console.log('Données du paiement:', paymentData);
        
        // 5. Vérifier le statut
        console.log('5. Vérification du statut...');
        const statusResponse = await fetch(`${API_BASE}/orders/${orderId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const statusData = await statusResponse.json();
        console.log(`✅ Statut de la commande: ${statusData.status}`);
        
        return { success: true, orderId, paymentData, statusData };
        
    } catch (error) {
        console.error('❌ Erreur:', error.message);
        return { success: false, error: error.message };
    }
}

// Exécuter le test
testPaymentFlow().then(result => {
    if (result.success) {
        console.log('🎉 Test réussi!');
    } else {
        console.log('💥 Test échoué:', result.error);
    }
});
