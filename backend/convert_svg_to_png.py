#!/usr/bin/env python3
"""
SVG zu PNG Konverter für das BarrierefreiCheck Logo
"""

import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def convert_svg_to_png_simple(svg_path, png_path, width=300, height=120):
    """
    Einfache SVG zu PNG Konvertierung mit System-Tools
    """
    try:
        # Versuche mit rsvg-convert (falls installiert)
        result = subprocess.run([
            'rsvg-convert', '-w', str(width), '-h', str(height),
            svg_path, '-o', png_path
        ], capture_output=True)
        
        if result.returncode == 0:
            print(f"✅ SVG mit rsvg-convert konvertiert: {png_path}")
            return True
    except FileNotFoundError:
        pass
    
    try:
        # Versuche mit Inkscape (falls installiert)
        result = subprocess.run([
            'inkscape', '--export-type=png', f'--export-width={width}',
            f'--export-filename={png_path}', svg_path
        ], capture_output=True)
        
        if result.returncode == 0:
            print(f"✅ SVG mit Inkscape konvertiert: {png_path}")
            return True
    except FileNotFoundError:
        pass
    
    try:
        # Versuche mit ImageMagick convert (falls installiert)
        result = subprocess.run([
            'convert', '-size', f'{width}x{height}', svg_path, png_path
        ], capture_output=True)
        
        if result.returncode == 0:
            print(f"✅ SVG mit ImageMagick konvertiert: {png_path}")
            return True
    except FileNotFoundError:
        pass
    
    return False

def create_text_logo_png(png_path, width=300, height=120):
    """
    Erstellt ein einfaches Text-Logo als PNG-Fallback
    """
    try:
        # Erstelle ein PNG mit dem Inclusa-Branding
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Inclusa Farben
        primary_color = (73, 32, 201)  # #4920c9
        text_color = (31, 41, 55)     # Dunkelgrau
        
        # Versuche eine bessere Schriftart
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
            font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            try:
                font_title = ImageFont.truetype("arial.ttf", 32)
                font_subtitle = ImageFont.truetype("arial.ttf", 16)
            except:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
        
        # Zeichne Inclusa Logo
        # Haupttext
        text1 = "Inclusa"
        bbox1 = draw.textbbox((0, 0), text1, font=font_title)
        text1_width = bbox1[2] - bbox1[0]
        text1_x = (width - text1_width) // 2
        
        draw.text((text1_x, 25), text1, fill=primary_color, font=font_title)
        
        # Untertitel
        text2 = "BarrierefreiCheck"
        bbox2 = draw.textbbox((0, 0), text2, font=font_subtitle)
        text2_width = bbox2[2] - bbox2[0]
        text2_x = (width - text2_width) // 2
        
        draw.text((text2_x, 70), text2, fill=text_color, font=font_subtitle)
        
        # Kleiner Akzent
        draw.rectangle([text1_x, 65, text1_x + text1_width, 68], fill=primary_color)
        
        img.save(png_path, "PNG")
        print(f"✅ Text-Logo erstellt: {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Text-Logos: {e}")
        return False

def main():
    """Hauptfunktion"""
    svg_path = "resources/logo.svg"
    png_path = "resources/logo_converted.png"
    
    if not os.path.exists(svg_path):
        print(f"❌ SVG-Datei nicht gefunden: {svg_path}")
        return False
    
    print(f"🔄 Konvertiere {svg_path} zu {png_path}...")
    
    # Versuche SVG-Konvertierung
    if convert_svg_to_png_simple(svg_path, png_path, 300, 120):
        return True
    
    # Fallback: Erstelle Text-Logo
    print("⚠️ Keine SVG-Konverter gefunden, erstelle Text-Logo...")
    return create_text_logo_png(png_path, 300, 120)

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Logo-Konvertierung abgeschlossen!")
    else:
        print("❌ Logo-Konvertierung fehlgeschlagen") 