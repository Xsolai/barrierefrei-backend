#!/usr/bin/env python3
"""
Script zum Erstellen von Test-Rabattcodes in Stripe
"""
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

def create_test_coupons():
    """Erstellt Test-Rabattcodes für die Entwicklung"""
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe.api_key:
        print("❌ STRIPE_SECRET_KEY nicht gefunden in .env")
        return
    
    print("🎫 Erstelle Test-Rabattcodes...")
    
    coupons = [
        {
            "id": "TEST100",
            "name": "100% Test Rabatt", 
            "percent_off": 100,
            "description": "Für Development-Tests - 100% Rabatt"
        },
        {
            "id": "DEV50",
            "name": "50% Development Rabatt",
            "percent_off": 50, 
            "description": "Für Tests - 50% Rabatt"
        },
        {
            "id": "DEMO90",
            "name": "90% Demo Rabatt",
            "percent_off": 90,
            "description": "Für Demos - 90% Rabatt"
        }
    ]
    
    for coupon_data in coupons:
        try:
            # Prüfe ob Coupon bereits existiert
            try:
                existing = stripe.Coupon.retrieve(coupon_data["id"])
                print(f"✅ Coupon '{coupon_data['id']}' existiert bereits")
                continue
            except stripe.error.InvalidRequestError:
                pass  # Coupon existiert nicht, erstelle ihn
            
            # Erstelle Coupon
            coupon = stripe.Coupon.create(
                id=coupon_data["id"],
                name=coupon_data["name"],
                percent_off=coupon_data["percent_off"],
                duration="once",  # Einmalig verwendbar
                metadata={
                    "type": "test_coupon",
                    "created_by": "development_script"
                }
            )
            
            print(f"✅ Coupon erstellt: {coupon.id} ({coupon.percent_off}% off)")
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen von {coupon_data['id']}: {e}")
    
    print("\n🎉 Test-Coupons erstellt!")
    print("\n📋 Verfügbare Rabattcodes:")
    print("  • TEST100 - 100% Rabatt (kostenlos)")
    print("  • DEV50   - 50% Rabatt") 
    print("  • DEMO90  - 90% Rabatt")
    print("\n💡 Diese Codes können im Checkout eingegeben werden.")

if __name__ == "__main__":
    create_test_coupons() 