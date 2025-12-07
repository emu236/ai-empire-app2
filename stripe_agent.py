# stripe_agent.py - WERSJA OBSŁUGUJĄCA KREDYTY I SUBSKRYPCJE (DICT RETURN)
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
APP_URL = os.getenv("APP_URL", "http://localhost:8501")

# Cennik Abonamentów
SUBSCRIPTIONS = {
    "Basic": 4900,
    "Standard": 9900,
    "Premium": 19900
}

# Cennik Kredytów
CREDIT_PACKS = {
    "Small": {"amount": 50, "price": 2900, "name": "50 Kredytów"},
    "Medium": {"amount": 200, "price": 9900, "name": "200 Kredytów"},
    "Large": {"amount": 1000, "price": 39900, "name": "1000 Kredytów"}
}

def create_checkout_session(item_key, item_type, customer_email, username):
    """
    Tworzy sesję płatności.
    item_type: 'subscription' lub 'credits'
    """
    try:
        if item_type == 'subscription':
            amount = SUBSCRIPTIONS.get(item_key, 4900)
            product_name = f"Pakiet {item_key} - AI Empire"
            metadata = {'type': 'subscription', 'tier': item_key, 'username': username}
        else:
            # Zakup kredytów
            pack = CREDIT_PACKS.get(item_key)
            amount = pack['price']
            product_name = f"Doładowanie: {pack['name']}"
            metadata = {'type': 'credits', 'amount': pack['amount'], 'username': username}

        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'blik'],
            line_items=[{
                'price_data': {
                    'currency': 'pln',
                    'product_data': {'name': product_name},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=customer_email,
            metadata=metadata,
            success_url=f"{APP_URL}/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{APP_URL}/?canceled=true",
        )
        return session.url
    except Exception as e:
        print(f"Błąd Stripe: {e}")
        return None

def verify_payment(session_id):
    """
    Weryfikuje płatność i zwraca SŁOWNIK (Dictionary), a nie Tuple.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            meta = session.metadata
            return {
                "verified": True,
                "type": meta.get('type'),       # 'subscription' lub 'credits'
                "value": meta.get('tier') if meta.get('type') == 'subscription' else meta.get('amount'),
                "username": meta.get('username'),
                "email": session.customer_details.email
            }
    except Exception as e:
        print(f"Błąd weryfikacji: {e}")
    
    # W przypadku błędu zwracamy słownik z flagą False
    return {"verified": False}