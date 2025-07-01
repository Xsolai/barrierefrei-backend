#!/usr/bin/env python3
"""
Logo-Generator für BarrierefreiCheck PDF-Berichte
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(output_path="logo.png"):
    """Erstellt ein einfaches Logo für die PDF-Berichte"""
    
    # Logo-Dimensionen
    width, height = 200, 200
    
    # Erstelle ein neues Bild mit transparentem Hintergrund
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Farben (BarrierefreiCheck Branding)
    primary_color = (73, 32, 201)  # #4920c9
    secondary_color = (107, 70, 193)  # #6b46c1
    text_color = (255, 255, 255)
    
    # Zeichne einen Kreis als Hintergrund
    margin = 20
    circle_bbox = [margin, margin, width-margin, height-margin]
    
    # Gradient-Effekt durch zwei überlappende Kreise
    draw.ellipse(circle_bbox, fill=primary_color)
    
    # Zeichne das "B" in der Mitte
    try:
        # Versuche eine größere Schrift zu verwenden
        font_size = 80
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback auf default Font
        font = ImageFont.load_default()
    
    # Text zentrieren
    text = "B"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Zeichne den Text
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    # Speichere das Logo
    img.save(output_path, "PNG")
    print(f"Logo erstellt: {output_path}")
    
    return output_path

def create_shield_logo(output_path="shield_logo.png"):
    """Erstellt ein Schild-Logo für Barrierefreiheit"""
    
    width, height = 200, 240
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Farben
    primary_color = (73, 32, 201)
    accent_color = (16, 185, 129)  # Grün für Accessibility
    
    # Schild-Form zeichnen
    margin = 20
    shield_points = [
        (width//2, margin),  # Spitze oben
        (width-margin, margin + 40),  # Rechts oben
        (width-margin, height - 60),  # Rechts unten
        (width//2, height - margin),  # Spitze unten
        (margin, height - 60),  # Links unten
        (margin, margin + 40),  # Links oben
    ]
    
    draw.polygon(shield_points, fill=primary_color)
    
    # Accessibility-Symbol (vereinfacht)
    center_x, center_y = width//2, height//2 - 10
    
    # Kreis für Kopf
    head_radius = 15
    draw.ellipse([center_x-head_radius, center_y-40, 
                  center_x+head_radius, center_y-10], fill=accent_color)
    
    # Körper
    draw.rectangle([center_x-8, center_y-10, center_x+8, center_y+30], fill=accent_color)
    
    # Rollstuhl-Rad (vereinfacht)
    wheel_radius = 20
    draw.ellipse([center_x-wheel_radius, center_y+10, 
                  center_x+wheel_radius, center_y+50], outline=accent_color, width=4)
    
    # Speichere das Logo
    img.save(output_path, "PNG")
    print(f"Schild-Logo erstellt: {output_path}")
    
    return output_path

if __name__ == "__main__":
    # Erstelle beide Logos
    create_logo("logo.png")
    create_shield_logo("shield_logo.png")
    
    print("Logos erfolgreich erstellt!") 