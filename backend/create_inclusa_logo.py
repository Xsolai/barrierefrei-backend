#!/usr/bin/env python3
"""
Erstellt das echte Inclusa-Logo für PDFs
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_inclusa_logo(output_path="resources/logo_inclusa.png"):
    """Erstellt das echte Inclusa-Logo"""
    
    # Logo-Dimensionen (4:1.6 Ratio für PDF-Kompatibilität)
    width, height = 400, 160
    
    # Erstelle transparentes Bild
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Inclusa Farben (aus dem Screenshot)
    purple_color = (95, 39, 205)      # Hauptlila
    pink_accent = (219, 39, 119)      # Pink/Magenta für den Akzent
    
    # Kreis-Symbol links (O mit Akzent)
    circle_center_x = 50
    circle_center_y = height // 2
    circle_radius = 35
    
    # Äußerer Kreis (lila)
    outer_circle = [
        circle_center_x - circle_radius, 
        circle_center_y - circle_radius,
        circle_center_x + circle_radius, 
        circle_center_y + circle_radius
    ]
    draw.ellipse(outer_circle, fill=purple_color)
    
    # Innerer Kreis (weiß - für das "Loch")
    inner_radius = 20
    inner_circle = [
        circle_center_x - inner_radius,
        circle_center_y - inner_radius, 
        circle_center_x + inner_radius,
        circle_center_y + inner_radius
    ]
    draw.ellipse(inner_circle, fill=(255, 255, 255, 0))  # Transparent
    
    # Pink Akzent (kleiner Bogen/Segment)
    # Zeichne einen kleinen Kreis als Akzent
    accent_radius = 12
    accent_x = circle_center_x + 15
    accent_y = circle_center_y - 15
    accent_circle = [
        accent_x - accent_radius,
        accent_y - accent_radius,
        accent_x + accent_radius, 
        accent_y + accent_radius
    ]
    draw.ellipse(accent_circle, fill=pink_accent)
    
    # "Inclusa" Text
    try:
        # Versuche System-Schriftarten
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
    
    text = "Inclusa"
    text_x = 120  # Rechts vom Kreis
    text_y = circle_center_y - 20  # Zentriert zum Kreis
    
    draw.text((text_x, text_y), text, fill=purple_color, font=font)
    
    # Speichere das Logo
    os.makedirs("resources", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✅ Inclusa-Logo erstellt: {output_path}")
    
    return output_path

def create_inclusa_logo_simple(output_path="resources/logo_inclusa.png"):
    """Einfachere Version des Inclusa-Logos"""
    
    width, height = 300, 100
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Inclusa Farben
    purple = (95, 39, 205)
    
    # Einfacher Kreis links
    circle_size = 40
    margin = 10
    circle_bbox = [margin, height//2 - circle_size//2, 
                   margin + circle_size, height//2 + circle_size//2]
    draw.ellipse(circle_bbox, fill=purple)
    
    # Weißer Kreis in der Mitte (für das "O")
    inner_size = 20
    inner_bbox = [margin + 10, height//2 - inner_size//2,
                  margin + 30, height//2 + inner_size//2] 
    draw.ellipse(inner_bbox, fill=(255, 255, 255, 0))
    
    # Text "Inclusa"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except:
        font = ImageFont.load_default()
    
    text_x = margin + circle_size + 15
    text_y = height//2 - 15
    draw.text((text_x, text_y), "Inclusa", fill=purple, font=font)
    
    os.makedirs("resources", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✅ Einfaches Inclusa-Logo erstellt: {output_path}")
    
    return output_path

if __name__ == "__main__":
    # Erstelle beide Versionen
    create_inclusa_logo()
    create_inclusa_logo_simple("resources/logo_inclusa_simple.png")
    
    print("🎉 Inclusa-Logos erstellt!") 