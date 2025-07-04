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
        
        # Frontend URL für Redirects - verwende lokale Entwicklung als Fallback
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        logger.info("Stripe Service initialisiert")
    
    def create_checkout_session(
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
        coupon_code: str = None,
        upgrade_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Erstellt eine Stripe Checkout Session mit separaten Line Items für Netto und MwSt
        
        Args:
            plan_id: Plan-Bezeichnung (basic, enterprise, certificate_only, professional_fix)
            price_amount: Gesamtpreis in Cent (inklusive MwSt)
            success_url: Erfolgs-URL
            cancel_url: Abbruch-URL  
            currency: Währung (default: eur)
            url: Website URL (für Beschreibung)
            customer_email: Kunden-E-Mail
            user_id: User ID (für Metadata)
            metadata: Zusätzliche Metadata
            coupon_code: Coupon-Code (optional)
            upgrade_details: Details zu gebuchten Upgrades
            
        Returns:
            Dict mit checkout_url, session_id, expires_at
        """
        try:
            logger.info(f"Erstelle Checkout Session für Plan: {plan_id}, Preis: €{price_amount/100}, URL: {url}")
            
            # Session Metadata erstellen (kompatibel mit Webhook)
            session_metadata = {
                'plan_id': plan_id,
                'website_url': url,  # Wichtig: muss 'website_url' heißen für Webhook!
                'user_id': user_id,
                'original_price_amount': str(price_amount),
                'currency': currency,
                'analysis_type': 'wcag_accessibility'
            }
            
            # Füge zusätzliche Metadata hinzu falls vorhanden
            if metadata:
                session_metadata.update(metadata)
            
            line_items = []
            
            # Spezielle Behandlung für nachträglich gekauftes Zertifikat
            if plan_id == 'certificate_only':
                # Berechne Netto und MwSt separat für nachträglich gekauftes Zertifikat
                net_amount = int((price_amount / 1.19))  # Netto-Betrag
                vat_amount = price_amount - net_amount   # MwSt-Betrag
                
                # Netto Line Item für nachträglich gekauftes Zertifikat
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': 'Offizielles Zertifikat (netto)',
                            'description': f'Rechtswirksames Zertifikat vom vitium e.V. für {url}',
                        },
                        'unit_amount': net_amount,
                    },
                    'quantity': 1,
                })
                
                # MwSt Line Item für nachträglich gekauftes Zertifikat
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': '19% Mehrwertsteuer',
                            'description': 'Gesetzliche Mehrwertsteuer auf Offizielles Zertifikat',
                        },
                        'unit_amount': vat_amount,
                    },
                    'quantity': 1,
                })
                
                logger.info(f"Certificate: Netto €{net_amount/100}, MwSt €{vat_amount/100}, Gesamt €{price_amount/100}")
                
            elif plan_id == 'professional_fix':
                # Spezielle Behandlung für Professionelle Website-Überarbeitung
                net_amount = int((price_amount / 1.19))  # Netto-Betrag
                vat_amount = price_amount - net_amount   # MwSt-Betrag
                
                # Hole Upgrade-Details für bessere Beschreibung
                page_count = upgrade_details.get('detected_pages', 1) if upgrade_details else 1
                
                # Netto Line Item für professionelle Überarbeitung
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': 'Professionelle Website-Überarbeitung (netto)',
                            'description': f'Vollständige Code-Überarbeitung durch zertifizierten Barrierefreiheitsexperten für {url} ({page_count} Seiten)',
                        },
                        'unit_amount': net_amount,
                    },
                    'quantity': 1,
                })
                
                # MwSt Line Item für professionelle Überarbeitung
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': '19% Mehrwertsteuer',
                            'description': 'Gesetzliche Mehrwertsteuer auf Professionelle Website-Überarbeitung',
                        },
                        'unit_amount': vat_amount,
                    },
                    'quantity': 1,
                })
                
                logger.info(f"Professional Fix: Netto €{net_amount/100}, MwSt €{vat_amount/100}, Gesamt €{price_amount/100} ({page_count} Seiten)")
                
            else:
                # Standard WCAG-Analyse (basic/enterprise)
                # Bei Enterprise ist Zertifikat bereits im Preis enthalten
                # Produkt-Name basierend auf Plan
                product_names = {
                    "basic": "WCAG Basic Analyse",
                    "enterprise": "WCAG Enterprise Analyse (inkl. Zertifikat)"
                }
                
                product_name = product_names.get(plan_id, "WCAG Analyse")
                # Berechne Netto und MwSt separat für die Hauptanalyse
                net_amount = int((price_amount / 1.19))  # Netto-Betrag
                vat_amount = price_amount - net_amount   # MwSt-Betrag
                
                # Netto Line Item für die Hauptanalyse
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': f'{product_name} (netto)',
                            'description': f'Barrierefreiheits-Analyse für {url}',
                        },
                        'unit_amount': net_amount,
                    },
                    'quantity': 1,
                })
                
                # MwSt Line Item für die Hauptanalyse
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': '19% Mehrwertsteuer',
                            'description': f'Gesetzliche Mehrwertsteuer auf {product_name}',
                        },
                        'unit_amount': vat_amount,
                    },
                    'quantity': 1,
                })
                
                logger.info(f"{product_name}: Netto €{net_amount/100}, MwSt €{vat_amount/100}, Gesamt €{price_amount/100}")
            
                # Füge separate Line Items für Upgrades hinzu (falls vorhanden)
                if upgrade_details and upgrade_details.get('selected_upgrades'):
                    logger.info(f"Füge Upgrades hinzu zu {product_name}: {upgrade_details}")
                    
                    # Bei Enterprise ist Zertifikat bereits inklusive - nicht nochmal berechnen!
                    if plan_id == 'enterprise' and 'certificate' in upgrade_details.get('selected_upgrades', []):
                        logger.info("Enterprise Plan: Zertifikat ist bereits im Preis enthalten - überspringe separate Berechnung")
                        selected_upgrades_filtered = [u for u in upgrade_details.get('selected_upgrades', []) if u != 'certificate']
                    else:
                        selected_upgrades_filtered = upgrade_details.get('selected_upgrades', [])
                    
                    # Upgrade-Namen und Preise definieren (netto)
                    upgrade_info = {
                        'professional_fix': {
                            'name': 'Professionelle Website-Überarbeitung',
                            'description': 'Vollständige Code-Überarbeitung durch zertifizierten Barrierefreiheitsexperten',
                            'price_net': int(200000)  # €2000 netto in Cent
                        },
                        'certificate': {
                            'name': 'Offizielles Zertifikat',
                            'description': 'Rechtswirksames Zertifikat vom vitium e.V. - geprüft von Menschen mit Behinderungen',
                            'price_net': int(90000)   # €900 netto in Cent
                        }
                    }
                    
                    # Erstelle Line Items für jedes ausgewählte Upgrade (mit separater MwSt)
                    for upgrade_id in selected_upgrades_filtered:
                        if upgrade_id in upgrade_info:
                            upgrade = upgrade_info[upgrade_id]
                            net_upgrade_amount = upgrade['price_net']
                            vat_upgrade_amount = int(net_upgrade_amount * 0.19)
                            
                            # Netto Line Item für Upgrade
                            line_items.append({
                                'price_data': {
                                    'currency': currency,
                                    'product_data': {
                                        'name': f"{upgrade['name']} (netto)",
                                        'description': upgrade['description'],
                                    },
                                    'unit_amount': net_upgrade_amount,
                                },
                                'quantity': 1,
                            })
                            
                            # MwSt Line Item für Upgrade
                            line_items.append({
                                'price_data': {
                                    'currency': currency,
                                    'product_data': {
                                        'name': '19% Mehrwertsteuer',
                                        'description': f'Gesetzliche Mehrwertsteuer auf {upgrade["name"]}',
                                    },
                                    'unit_amount': vat_upgrade_amount,
                                },
                                'quantity': 1,
                            })
                            
                            logger.info(f"Upgrade hinzugefügt: {upgrade['name']} - Netto €{net_upgrade_amount/100}, MwSt €{vat_upgrade_amount/100}")
            
            # Checkout Session Parameter
            session_params = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'customer_email': customer_email,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': session_metadata,
                'automatic_tax': {'enabled': False},
                'invoice_creation': {
                    'enabled': True,
                    'invoice_data': {
                        'description': f'Barrierefreiheits-Services: {url}',
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
    
    def get_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Holt Details einer Checkout Session, inklusive Payment Intent"""
        try:
            logger.info(f"Rufe Session {session_id} von Stripe ab mit expandiertem Payment Intent")
            session = stripe.checkout.Session.retrieve(
                session_id,
                expand=["payment_intent"]
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Fehler beim Abrufen der Session {session_id}: {str(e)}")
            raise Exception(f"Stripe Session nicht gefunden: {str(e)}")

    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """Holt einen Payment Intent"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
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