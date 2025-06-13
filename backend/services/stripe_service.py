import stripe
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StripeService:
    """Service für Stripe Payment Integration"""
    
    def __init__(self):
        # Stripe API Key aus Umgebungsvariablen
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_key:
            raise ValueError("STRIPE_SECRET_KEY muss in .env gesetzt sein")
            
        stripe.api_key = stripe_key
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Frontend URL für Redirects
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://inclusa.de')
        
        logger.info("Stripe Service initialisiert")
    
    async def create_checkout_session(
        self, 
        plan_id: str,
        price_amount: int,  # in Cent
        success_url: str,
        cancel_url: str,
        currency: str = "eur",
        url: str = "",
        customer_email: str = "",
        user_id: str = "",
        metadata: Dict[str, Any] = None,
        coupon_code: str = None
    ) -> Dict[str, Any]:
        """
        Erstellt eine Stripe Checkout Session für die Zahlung
        
        Args:
            plan_id: Plan ID (basic, enterprise)
            price_amount: Preis in Cent (z.B. 35000 für €350)
            currency: Währung (eur)
            url: Website URL die analysiert werden soll
            customer_email: Kunde Email
            user_id: User ID aus Supabase
            metadata: Zusätzliche Metadaten
            coupon_code: Rabattcode (optional)
            
        Returns:
            Dict mit checkout_url und session_id
        """
        try:
            # Metadaten für spätere Verarbeitung
            session_metadata = {
                "plan_id": plan_id,
                "website_url": url,
                "user_id": user_id,
                "analysis_type": "wcag_accessibility",
                **(metadata or {})
            }
            
            # Rabattcode zu Metadaten hinzufügen falls vorhanden
            if coupon_code:
                session_metadata["coupon_code"] = coupon_code
            
            # Produkt-Name basierend auf Plan
            product_names = {
                "basic": "WCAG Basic Analyse",
                "enterprise": "WCAG Enterprise Analyse"
            }
            
            product_name = product_names.get(plan_id, "WCAG Analyse")
            
            # Checkout Session Parameter
            session_params = {
                'payment_method_types': ['card'],
                'line_items': [{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': product_name,
                            'description': f'Barrierefreiheits-Analyse für {url}',
                        },
                        'unit_amount': price_amount,
                    },
                    'quantity': 1,
                }],
                'mode': 'payment',
                'customer_email': customer_email,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': session_metadata,
                'automatic_tax': {'enabled': False},
                'invoice_creation': {
                    'enabled': True,
                    'invoice_data': {
                        'description': f'Barrierefreiheits-Analyse: {url}',
                        'metadata': session_metadata,
                    }
                },
                'expires_at': int((datetime.now() + timedelta(minutes=30)).timestamp())
            }
            
            # Wenn ein spezifischer Coupon-Code übergeben wurde, validiere und verwende ihn
            if coupon_code:
                try:
                    # Prüfe ob Coupon existiert
                    coupon = stripe.Coupon.retrieve(coupon_code)
                    logger.info(f"Verwende Coupon: {coupon_code} ({coupon.percent_off}% off)")
                    
                    # Füge Discount zur Session hinzu (anstatt allow_promotion_codes)
                    session_params['discounts'] = [{'coupon': coupon_code}]
                    
                except stripe.error.InvalidRequestError:
                    logger.warning(f"Ungültiger Coupon-Code: {coupon_code}")
                    # Session trotzdem erstellen, aber mit allow_promotion_codes für manuelle Eingabe
                    session_params['allow_promotion_codes'] = True
                except Exception as e:
                    logger.error(f"Fehler beim Validieren des Coupons: {str(e)}")
                    # Session trotzdem erstellen, aber mit allow_promotion_codes für manuelle Eingabe
                    session_params['allow_promotion_codes'] = True
            else:
                # Nur wenn kein Coupon-Code übergeben wurde, erlaube manuelle Eingabe
                session_params['allow_promotion_codes'] = True
            
            # Checkout Session erstellen
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"Stripe Checkout Session erstellt: {session.id} für User {user_id}")
            
            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "expires_at": session.expires_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Fehler bei Checkout Session: {str(e)}")
            raise Exception(f"Payment-Fehler: {str(e)}")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler bei Checkout Session: {str(e)}")
            raise
    
    async def get_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Holt Details einer Checkout Session, inklusive Payment Intent"""
        try:
            logger.info(f"Rufe Session {session_id} von Stripe ab mit expandiertem Payment Intent")
            session = await stripe.checkout.Session.retrieve(
                session_id,
                expand=["payment_intent"]
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Fehler beim Abrufen der Session {session_id}: {str(e)}")
            raise Exception(f"Stripe Session nicht gefunden: {str(e)}")

    async def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Holt einen Payment Intent"""
        try:
            payment_intent = await stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Fehler beim Abrufen des Payment Intent {payment_intent_id}: {str(e)}")
            raise Exception(f"Stripe Payment Intent nicht gefunden: {str(e)}")

    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Holt Details einer Checkout Session
        
        Args:
            session_id: Stripe Session ID
            
        Returns:
            Session Details inklusive Payment Status
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                "id": session.id,
                "payment_status": session.payment_status,
                "status": session.status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer_email": session.customer_details.email if session.customer_details else None,
                "metadata": session.metadata,
                "payment_intent": session.payment_intent,
                "created": session.created,
                "expires_at": session.expires_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Fehler beim Abrufen der Session {session_id}: {str(e)}")
            raise Exception(f"Session nicht gefunden: {str(e)}")
    
    def verify_payment_success(self, session_id: str) -> bool:
        """
        Verifiziert ob eine Zahlung erfolgreich war
        
        Args:
            session_id: Stripe Session ID
            
        Returns:
            True wenn Zahlung erfolgreich
        """
        try:
            session = self.get_session_details(session_id)
            return session["payment_status"] == "paid" and session["status"] == "complete"
            
        except Exception as e:
            logger.error(f"Fehler beim Verifizieren der Zahlung für Session {session_id}: {str(e)}")
            return False

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> stripe.Event:
        """
        Verifiziert die Webhook-Signatur und konstruiert das Event-Objekt.
        Wirft eine Exception bei einem Fehler.
        """
        if not self.webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET ist nicht konfiguriert.")
            raise ValueError("Webhook Secret nicht konfiguriert, kann Event nicht prüfen.")
            
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook Signatur-Verifizierung fehlgeschlagen: {e}")
            raise ValueError("Ungültige Webhook-Signatur") from e
        except Exception as e:
            logger.error(f"Fehler beim Konstruieren des Webhook-Events: {e}")
            raise ValueError("Fehler bei der Webhook-Verarbeitung") from e
    
    def create_test_mode_prices(self) -> Dict[str, str]:
        """
        Erstellt Test-Preise für Entwicklung
        Nur für Testzwecke!
        """
        try:
            # Basic Plan
            basic_price = stripe.Price.create(
                unit_amount=35000,  # €350.00
                currency='eur',
                product_data={
                    'name': 'WCAG Basic Analyse',
                    'description': 'Grundlegende Barrierefreiheits-Analyse'
                },
            )
            
            # Enterprise Plan  
            enterprise_price = stripe.Price.create(
                unit_amount=45000,  # €450.00
                currency='eur',
                product_data={
                    'name': 'WCAG Enterprise Analyse',
                    'description': 'Umfassende Barrierefreiheits-Analyse mit Premium-Features'
                },
            )
            
            logger.info("Test-Preise erstellt")
            
            return {
                "basic": basic_price.id,
                "enterprise": enterprise_price.id
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Test-Preise: {str(e)}")
            raise

    def validate_coupon(self, coupon_code: str) -> Dict[str, Any]:
        """
        Validiert einen Rabattcode und gibt Details zurück
        
        Args:
            coupon_code: Der zu validierende Rabattcode
            
        Returns:
            Dict mit Coupon-Details oder Fehlermeldung
        """
        try:
            coupon = stripe.Coupon.retrieve(coupon_code)
            
            return {
                "valid": True,
                "id": coupon.id,
                "name": coupon.name,
                "percent_off": coupon.percent_off,
                "amount_off": coupon.amount_off,
                "currency": coupon.currency,
                "duration": coupon.duration,
                "description": getattr(coupon, 'description', None)
            }
            
        except stripe.error.InvalidRequestError:
            return {
                "valid": False,
                "error": "Rabattcode nicht gefunden"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Fehler beim Validieren: {str(e)}"
            } 