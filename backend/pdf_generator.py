#!/usr/bin/env python3
"""
PDF-Generator für WCAG-Analyse-Berichte
Verbesserte Version mit professionellem Design und Logo-Unterstützung
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re
import html
import os
import sys

# Füge das parent directory zum Python path hinzu, um config zu importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Importiere das neue Scoring-System
try:
    from .scoring_system import wcag_scorer, ComplianceLevel
except ImportError:
    try:
        from scoring_system import wcag_scorer, ComplianceLevel
    except ImportError:
        # Fallback wenn scoring_system nicht verfügbar
        wcag_scorer = None
        ComplianceLevel = None

class PDFReportGenerator:
    """Generiert professionelle PDF-Berichte aus WCAG-Analyse-Ergebnissen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.use_new_scoring = wcag_scorer is not None
        if self.use_new_scoring:
            self.logger.info("✅ Neues WCAG-Scoring-System aktiviert")
        else:
            self.logger.warning("⚠️ Neues Scoring-System nicht verfügbar - verwende Legacy-Modus")
    
    def _check_reportlab_availability(self):
        """Prüft ob ReportLab verfügbar ist"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm, cm
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
            from reportlab.platypus.flowables import KeepTogether
            return True
        except ImportError as e:
            self.logger.error(f"ReportLab nicht verfügbar: {e}")
            return False
    
    def _clean_text_for_pdf(self, text: str) -> str:
        """Verbesserte Textbereinigung für deutsche PDFs - behält Umlaute bei"""
        if not text:
            return ""
        
        # HTML-Entities dekodieren
        text = html.unescape(text)
        
        # HTML-Tags entfernen
        text = re.sub(r'<[^>]+>', '', text)
        
        # Mehrfache Leerzeichen reduzieren
        text = re.sub(r'\s+', ' ', text)
        
        # Problematische Anführungszeichen ersetzen, aber Umlaute BEHALTEN
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # NICHT mehr: Umlaute explizit handhaben - wir behalten sie bei!
        # ReportLab kann UTF-8 verarbeiten, wenn wir die richtigen Fonts verwenden
        
        return text.strip()
    
    def _create_header_with_logo(self, story, styles):
        """Erstellt professionellen Header mit Logo oben und Titel darunter"""
        from reportlab.platypus import Table, TableStyle, Spacer, Paragraph
        from reportlab.platypus import HRFlowable
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        
        # Logo ganz oben links mit Tabelle für korrekte Positionierung
        logo = self._get_logo_placeholder()
        if logo:
            # Verwende Tabelle um Logo linksbündig zu positionieren
            logo_table = Table([[logo]], colWidths=[4*cm])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('VALIGN', (0, 0), (0, 0), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 0),
                ('TOPPADDING', (0, 0), (0, 0), 0),
                ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            ]))
            story.append(logo_table)
            story.append(Spacer(1, 8))  # Abstand nach Logo
        
        # Titel-Bereich darunter (linksbündig)
        header_content = self._get_header_content(styles)
        for element in header_content:
            story.append(element)
        
        # Trennlinie unter dem Header
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, lineCap='round', 
                               color=colors.Color(0.286, 0.125, 0.788)))  # #4920c9
        story.append(Spacer(1, 15))
    
    def _get_logo_placeholder(self):
        """Erstellt Logo-Platzhalter oder lädt echtes Logo"""
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        
        # Versuche echtes Logo zu laden, sonst Platzhalter  
        logo_paths = ["resources/logo_inclusa.png", "resources/logo_converted.png", "resources/logo.png", "../frontend/public/logo.png"]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    from reportlab.platypus import Image
                    from reportlab.lib.units import cm
                    # Größeres Logo ohne Verzerrung - proportional
                    return Image(logo_path, width=4*cm, height=1.6*cm)
                except Exception as e:
                    self.logger.warning(f"Konnte Logo nicht laden: {logo_path} - {e}")
                    continue
        
        # Fallback: Stylischer Text-Logo-Platzhalter
        logo_style = ParagraphStyle(
            'LogoStyle',
            fontSize=20,
            fontName='Helvetica-Bold',
            textColor=colors.Color(0.286, 0.125, 0.788),  # #4920c9
            alignment=TA_LEFT,  # Linksbündig statt zentriert
            spaceBefore=0,
            spaceAfter=0
        )
        
        return Paragraph("🛡️ <b>Inclusa</b>", logo_style)
    
    def _get_header_content(self, styles):
        """Erstellt Header-Inhalt mit Titel und Branding"""
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            fontSize=24,
            fontName='Helvetica-Bold',
            textColor=colors.Color(0.286, 0.125, 0.788),  # #4920c9
            alignment=TA_LEFT,  # Linksbündig
            spaceBefore=0,
            spaceAfter=8
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            fontSize=12,
            fontName='Helvetica',
            textColor=colors.Color(0.4, 0.4, 0.4),
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0
        )
        
        from reportlab.platypus import Spacer
        from reportlab.lib.units import mm
        
        return [
            Paragraph("<b>BarrierefreiCheck</b>", header_style),
            Spacer(1, 4*mm),  # Mehr Abstand nach dem Haupttitel
            Paragraph("WCAG 2.1 Barrierefreiheits-Analyse", subtitle_style),
            Spacer(1, 2*mm),  # Kleiner Abstand
            Paragraph("Professioneller Prüfbericht", subtitle_style)
        ]
    
    def _create_professional_footer(self, styles):
        """Erstellt professionellen Footer"""
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.lib.units import cm
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=TA_LEFT
        )
        
        date_style = ParagraphStyle(
            'DateStyle',
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        
        footer_data = [
            [
                Paragraph(f"BarrierefreiCheck by {config.COMPANY_NAME}<br/>{config.SUPPORT_EMAIL}", contact_style),
                Paragraph("Automatisierte WCAG-Analyse<br/>Erstellt mit KI-Technologie", footer_style),
                Paragraph(f"Erstellt am<br/>{datetime.now().strftime('%d.%m.%Y %H:%M')}", date_style)
            ]
        ]
        
        footer_table = Table(footer_data, colWidths=[6*cm, 6*cm, 6*cm])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return footer_table

    def generate_pdf_from_job_data(self, job_id: str, job_data: Dict[str, Any], 
                                   modules_data: list, output_path: Optional[str] = None) -> str:
        """
        Generiert professionelles PDF aus Job-Daten und Modul-Ergebnissen
        
        Args:
            job_id: Job-ID
            job_data: Job-Details (URL, Status, etc.)
            modules_data: Liste der Modul-Ergebnisse
            output_path: Optionaler Ausgabepfad
            
        Returns:
            Pfad zur generierten PDF-Datei
        """
        if not self._check_reportlab_availability():
            raise Exception("ReportLab nicht verfügbar. Bitte installieren Sie 'reportlab'.")
        
        # Importiere ReportLab-Module hier
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
        from reportlab.platypus import HRFlowable
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            clean_url = job_data.get('url', 'unknown').replace('https://', '').replace('http://', '').replace('/', '_')
            output_path = f"WCAG_Report_{clean_url}_{timestamp}.pdf"
        
        # Erstelle PDF mit professionellem Layout
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=3*cm
        )
        story = []
        styles = getSampleStyleSheet()
        
        # Professionelle Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            spaceBefore=15,
            alignment=TA_LEFT,
            textColor=colors.Color(0.11, 0.11, 0.11)  # Dunkelgrau
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.Color(0.286, 0.125, 0.788),  # #4920c9
            borderWidth=0,
            borderColor=colors.Color(0.286, 0.125, 0.788),
            borderPadding=0
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.Color(0.2, 0.2, 0.2)
        )
        
        criteria_style = ParagraphStyle(
            'CriteriaStyle',
            parent=styles['Heading4'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.Color(0.6, 0.1, 0.1)  # Dunkles Rot
        )
        
        # Schwarzer Style für bestimmte Überschriften
        black_heading_style = ParagraphStyle(
            'BlackHeadingStyle',
            parent=styles['Heading4'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.black  # Schwarz
        )
        
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            textColor=colors.Color(0.2, 0.2, 0.2)
        )
        
        # Header mit Logo erstellen
        self._create_header_with_logo(story, styles)
        
        # Haupttitel
        story.append(Paragraph("Barrierefreiheits-Prüfbericht", title_style))
        story.append(Spacer(1, 10))
        
        # Übersicht-Sektion in einer Box
        overview_content = []
        overview_content.append(Paragraph("<b>Analyse-Übersicht</b>", heading_style))
        
        # Styling für die Übersichts-Tabelle mit automatischem Textumbruch
        overview_data = [
            ['Website:', Paragraph(self._clean_text_for_pdf(job_data.get('url', 'N/A')), body_style)],
            ['Analysiert am:', Paragraph(datetime.fromisoformat(job_data.get('created_at', '')).strftime('%d.%m.%Y um %H:%M Uhr') if job_data.get('created_at') else 'N/A', body_style)],
            ['Analyse-Status:', Paragraph(self._translate_status(job_data.get('status', 'unknown')), body_style)],
            ['Tarif:', Paragraph(job_data.get('plan', 'basic').upper(), body_style)],
            ['Bericht-ID:', Paragraph(job_id[:8] + '...', body_style)]
        ]
        
        overview_table = Table(overview_data, colWidths=[4*cm, 10*cm])  # Schmaler für bessere Sicherheit
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.97)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.2, 0.2, 0.2)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.85, 0.85, 0.9)),
            ('ROUNDEDCORNERS', [5, 5, 5, 5])
        ]))
        
        overview_content.append(overview_table)
        story.extend(overview_content)
        story.append(Spacer(1, 25))
        
        # Bewertungs-Sektion
        story.append(Paragraph("Gesamtbewertung", heading_style))
        
        # Berechne Gesamtstatistiken
        total_score, passed_criteria, total_violations, total_warnings = self._calculate_overall_stats(modules_data)
        
        # Score-Anzeige mit Farb-Kodierung
        score_color = self._get_score_color(total_score)
        compliance_level = self._get_compliance_level(total_score)
        
        stats_data = [
            ['Gesamtbewertung:', Paragraph(f'{total_score}/100 Punkte', body_style)],
            ['Compliance-Level:', Paragraph(f'{compliance_level}', body_style)],
            ['Erfüllte Kriterien:', Paragraph(str(passed_criteria), body_style)],
            ['Kritische Verstöße:', Paragraph(str(total_violations), body_style)],
            ['Warnungen:', Paragraph(str(total_warnings), body_style)]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 7*cm])  # Schmaler für bessere Sicherheit
        # Score-Farben definieren
        score_color_obj = colors.green if total_score >= 80 else colors.orange if total_score >= 60 else colors.red
        violation_color = colors.red if total_violations > 0 else colors.black
        warning_color = colors.orange if total_warnings > 0 else colors.black
        
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.94, 0.97, 1.0)),  # Hellblau
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.2, 0.2, 0.2)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Labels fett
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),       # Werte normal
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.7, 0.8, 0.95)),
            # Score-Zeilen einfärben
            ('TEXTCOLOR', (1, 0), (1, 0), score_color_obj),    # Gesamtbewertung
            ('TEXTCOLOR', (1, 1), (1, 1), score_color_obj),    # Compliance-Level
            ('TEXTCOLOR', (1, 3), (1, 3), violation_color),    # Verstöße
            ('TEXTCOLOR', (1, 4), (1, 4), warning_color),      # Warnungen
            ('FONTNAME', (1, 0), (1, 1), 'Helvetica-Bold'),    # Score und Level fett
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # Seitenumbruch vor der detaillierten Analyse
        story.append(PageBreak())
        
        # WCAG-Module Details mit verbessertem Design  
        story.append(Paragraph("Detaillierte Analyse nach WCAG-Kriterien", heading_style))
        story.append(Spacer(1, 15))
        
        # Sicherheitsüberprüfung für modules_data
        if not modules_data:
            story.append(Paragraph("Keine Modulergebnisse verfügbar.", body_style))
        else:
            valid_modules = []  # Sammle Module mit Inhalt
            
            for module in modules_data:
                if not module or not isinstance(module, dict):
                    continue
                    
                result = module.get('result', {})
                if not result or not isinstance(result, dict):
                    continue
                
                # Generiere vollständigen Modulinhalt mit Sicherheitsüberprüfungen
                try:
                    module_content = self._generate_complete_module_content(
                        module, subheading_style, criteria_style, styles, 
                        Paragraph, Spacer, PageBreak, body_style
                    )
                    if module_content and len(module_content) > 2:  # Nur wenn substantieller Inhalt
                        valid_modules.append(module_content)
                except Exception as e:
                    self.logger.error(f"Fehler bei der Generierung des Modulinhalts: {str(e)}")
                    continue
            
            # Füge Module mit korrekten PageBreaks hinzu
            for i, module_content in enumerate(valid_modules):
                story.extend(module_content)
                # PageBreak nur zwischen Modulen, nicht nach dem letzten
                if i < len(valid_modules) - 1:
                    story.append(PageBreak())
        
        # Empfehlungen-Sektion (kleinere Abstände)
        story.append(Spacer(1, 20))  # Abstand vor Empfehlungen
        # Schwarzer Style für "Prioritäre Handlungsempfehlungen"
        black_main_heading_style = ParagraphStyle(
            'BlackMainHeadingStyle',
            parent=styles['Heading2'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.black  # Schwarz statt lila
        )
        story.append(Paragraph("Prioritäre Handlungsempfehlungen", black_main_heading_style))
        story.append(Spacer(1, 10))
        
        try:
            recommendations = self._generate_comprehensive_recommendations(modules_data)
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    if not isinstance(rec, dict):
                        continue
                    title = rec.get('title', '')
                    description = rec.get('description', '')
                    if title and description:
                        # Bessere Formatierung der Empfehlungen
                        rec_title = Paragraph(f"<b>{i}. {self._clean_text_for_pdf(title)}</b>", criteria_style)
                        rec_desc = Paragraph(self._clean_text_for_pdf(description), body_style)
                        
                        story.append(KeepTogether([rec_title, rec_desc, Spacer(1, 10)]))
            else:
                story.append(Paragraph("Keine spezifischen Empfehlungen erforderlich.", body_style))
        except Exception as e:
            self.logger.error(f"Fehler bei der Generierung der Empfehlungen: {str(e)}")
            story.append(Paragraph("Empfehlungen konnten nicht generiert werden.", body_style))
        
        story.append(Spacer(1, 20))
        
        # Professioneller Footer
        story.append(self._create_professional_footer(styles))
        
        # PDF erstellen
        try:
            doc.build(story)
            self.logger.info(f"PDF-Bericht erfolgreich erstellt: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der PDF: {str(e)}")
            raise

    def _get_score_color(self, score: int) -> str:
        """Bestimmt die Farbe basierend auf dem Score"""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "orange"
        else:
            return "red"
    
    def _get_compliance_level(self, score: int) -> str:
        """Bestimmt das Compliance-Level basierend auf dem Score"""
        if score >= 90:
            return "Ausgezeichnet (AAA-Level erreicht)"
        elif score >= 80:
            return "Gut (AA-Level erreicht)"
        elif score >= 60:
            return "Verbesserungsfähig (A-Level erreicht)"
        else:
            return "Nicht konform (erhebliche Mängel)"

    def _generate_complete_module_content(self, module: Dict[str, Any], subheading_style, 
                                        criteria_style, styles, Paragraph, Spacer, PageBreak, body_style) -> list:
        """Generiert vollständigen Modulinhalt mit verbessertem Design"""
        content = []
        
        module_name = module.get('module_name', 'Unbekannt')
        result = module.get('result', {})
        
        # Modul-Titel mit Box-Design
        module_title = self._format_module_title(module_name)
        
        # Erstelle eine Box um den Modultitel
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        
        title_data = [[Paragraph(f"<b>{module_title}</b>", subheading_style)]]
        title_table = Table(title_data, colWidths=[16*cm])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 1.0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [5, 5, 5, 5])
        ]))
        
        content.append(title_table)
        content.append(Spacer(1, 15))
        
        # Überprüfe auf analysis_result (neues Format)
        analysis_result = result.get('analysis_result')
        if analysis_result:
            content.extend(self._generate_analysis_result_content(
                analysis_result, criteria_style, styles, Paragraph, Spacer, body_style
            ))
        else:
            # Fallback für alte oder fehlende Daten
            content.append(Paragraph("Keine detaillierten Analyseergebnisse verfügbar.", body_style))
        
        content.append(Spacer(1, 25))
        return content

    def _generate_analysis_result_content(self, analysis_result: Dict[str, Any], criteria_style, 
                                        styles, Paragraph, Spacer, body_style) -> list:
        """Generiert Inhalt aus analysis_result mit verbessertem Design"""
        content = []
        
        # Schwarzer Style für Überschriften
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        
        black_heading_style = ParagraphStyle(
            'BlackHeadingStyle',
            parent=styles['Heading4'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.black
        )
        
        # 1. Zusammenfassung mit Box-Design
        summary = analysis_result.get('summary', {})
        if summary:
            content.append(Paragraph("<b>Modulbewertung</b>", black_heading_style))
            
            # Score und Compliance Level
            score = summary.get('score', 0)
            compliance_level = summary.get('compliance_level', 'N/A')
            score_color = self._get_score_color(score)
            
            # Erstelle eine Bewertungs-Box
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            
            score_data = [
                [Paragraph(f'Score: {score}/100 Punkte', body_style)],
                [Paragraph(f'Compliance Level: {compliance_level}', body_style)]
            ]
            
            # Gesamtbewertung hinzufügen falls vorhanden
            overall_assessment = summary.get('overall_assessment', '')
            if overall_assessment:
                clean_assessment = self._clean_text_for_pdf(overall_assessment)
                # Verwende Paragraph mit automatischem Textumbruch
                score_data.append([Paragraph(f'Bewertung: {clean_assessment}', body_style)])
            
            score_table = Table(score_data, colWidths=[13*cm])  # Etwas schmaler für bessere Sicherheit
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.99, 1.0)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.95))
            ]))
            
            content.append(score_table)
            content.append(Spacer(1, 15))
        
        # 2. Kriterien-Bewertung mit verbessertem Design
        criteria_evaluation = analysis_result.get('criteria_evaluation', [])
        if criteria_evaluation:
            content.append(Paragraph("<b>Kriterien-Details</b>", black_heading_style))
            content.append(Spacer(1, 10))
            
            for i, criteria in enumerate(criteria_evaluation, 1):
                # Kriterium Header mit Status-Farben
                criterion_id = criteria.get('criterion_id', '')
                name = self._clean_text_for_pdf(criteria.get('name', 'Unbekannt'))
                status = criteria.get('status', 'UNKNOWN')
                
                status_mapping = {
                    'FAILED': ('NICHT ERFÜLLT', 'red'),
                    'PARTIAL': ('TEILWEISE ERFÜLLT', 'orange'), 
                    'WARNING': ('WARNUNG', 'orange'),
                    'PASSED': ('ERFÜLLT', 'green')
                }
                
                status_text, status_color = status_mapping.get(status, (status, 'black'))
                
                # Kriterium-Box erstellen
                criterion_header = f'<b>{criterion_id} {name}</b> - <font color="{status_color}"><i>{status_text}</i></font>'
                content.append(Paragraph(criterion_header, styles['Heading4']))
                
                # Details in strukturierter Form
                details = []
                
                # Befund - nur wenn nicht leer
                finding = criteria.get('finding', '')
                if finding and finding.strip() and finding.strip() != '-':
                    clean_finding = self._clean_text_for_pdf(finding)
                    if clean_finding and clean_finding.strip():
                        details.append(f"<b>Befund:</b> {clean_finding}")
                
                # Auswirkung - nur wenn nicht leer
                impact = criteria.get('impact', '')
                if impact and impact.strip() and impact.strip() != '-':
                    clean_impact = self._clean_text_for_pdf(impact)
                    if clean_impact and clean_impact.strip():
                        details.append(f"<b>Auswirkung:</b> {clean_impact}")
                
                # Beispiele - nur wenn nicht leer
                examples = criteria.get('examples', [])
                valid_examples = [ex for ex in examples if ex and str(ex).strip() and str(ex).strip() != '-']
                if valid_examples:
                    examples_text = "<b>Beispiele:</b><br/>"
                    for example in valid_examples[:3]:  # Maximal 3 Beispiele
                        clean_example = self._clean_text_for_pdf(str(example))
                        if clean_example and clean_example.strip():
                            examples_text += f"• {clean_example}<br/>"
                    # Nur hinzufügen wenn tatsächlich Beispiele vorhanden
                    if "•" in examples_text:
                        details.append(examples_text)
                
                # Empfehlung - nur wenn nicht leer
                recommendation = criteria.get('recommendation', '')
                if recommendation and recommendation.strip() and recommendation.strip() != '-':
                    clean_recommendation = self._clean_text_for_pdf(recommendation)
                    if clean_recommendation and clean_recommendation.strip():
                        details.append(f"<b>Empfehlung:</b> {clean_recommendation}")
                
                # Details als Box anzeigen
                if details:
                    for detail in details:
                        content.append(Paragraph(detail, body_style))
                        content.append(Spacer(1, 6))
                
                content.append(Spacer(1, 15))
        
        # 3. Priorisierte Maßnahmen mit verbessertem Design - nur wenn nicht leer
        priority_actions = analysis_result.get('priority_actions', {})
        has_valid_actions = False
        
        # Prüfe ob tatsächlich valide Aktionen vorhanden sind
        for priority, actions in priority_actions.items():
            if actions and isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get('title', '').strip():
                        has_valid_actions = True
                        break
                if has_valid_actions:
                    break
        
        if has_valid_actions:
            content.append(Paragraph("<b>Handlungsempfehlungen</b>", black_heading_style))
            content.append(Spacer(1, 10))
            
            # Prioritäts-Mapping - alle schwarz
            priority_colors = {
                'immediate': ('black', 'Sofortige Maßnahmen'),
                'short_term': ('black', 'Kurzfristige Maßnahmen'),
                'long_term': ('black', 'Langfristige Maßnahmen')
            }
            
            for priority, actions in priority_actions.items():
                if not actions or not isinstance(actions, list):
                    continue
                
                color, priority_text = priority_colors.get(priority, ('black', priority.title()))
                
                # Prioritäts-Header schwarz
                priority_header = f'<font color="{color}"><b>{priority_text}:</b></font>'
                content.append(Paragraph(priority_header, styles['Heading4']))
                
                # Maßnahmen in strukturierter Form - nur valide Aktionen
                valid_actions_for_priority = []
                for action in actions:
                    if isinstance(action, dict) and action.get('title', '').strip():
                        valid_actions_for_priority.append(action)
                
                if valid_actions_for_priority:
                    for action in valid_actions_for_priority:
                        title = self._clean_text_for_pdf(action.get('title', ''))
                        if not title or not title.strip():
                            continue
                            
                        effort = action.get('effort', '')
                        description = self._clean_text_for_pdf(action.get('description', ''))
                        affected_criteria = action.get('affected_criteria', [])
                        
                        # Maßnahmen-Box erstellen
                        action_content = f"<b>• {title}</b>"
                        if effort and effort.strip():
                            action_content += f" <i>(Aufwand: {effort})</i>"
                        
                        content.append(Paragraph(action_content, body_style))
                        
                        if description and description.strip():
                            content.append(Paragraph(f"  {description}", body_style))
                        
                        if affected_criteria and len(affected_criteria) > 0:
                            criteria_list = ', '.join([c for c in affected_criteria if c and c.strip()])
                            if criteria_list:
                                content.append(Paragraph(f"  <i>Betroffene Kriterien: {criteria_list}</i>", body_style))
                        
                        content.append(Spacer(1, 8))
                
                content.append(Spacer(1, 15))
        
        return content

    def _generate_comprehensive_recommendations(self, modules_data: list) -> list:
        """Generiert umfassende Empfehlungen aus allen Modulen"""
        recommendations = []
        
        # Sammle alle sofortigen Maßnahmen aus allen Modulen
        immediate_actions = []
        short_term_actions = []
        high_priority_criteria = []
        
        for module in modules_data:
            result = module.get('result', {})
            analysis_result = result.get('analysis_result', {})
            
            if analysis_result:
                priority_actions = analysis_result.get('priority_actions', {})
                
                # Sammle sofortige Maßnahmen
                if priority_actions.get('immediate'):
                    immediate_actions.extend(priority_actions['immediate'])
                
                # Sammle kurzfristige Maßnahmen
                if priority_actions.get('short_term'):
                    short_term_actions.extend(priority_actions['short_term'])
                
                # Sammle kritische Kriterien
                criteria_evaluation = analysis_result.get('criteria_evaluation', [])
                for criteria in criteria_evaluation:
                    if criteria.get('status') == 'FAILED':
                        high_priority_criteria.append({
                            'module': self._format_module_title(module.get('module_name', '')),
                            'criterion': criteria.get('criterion_id', ''),
                            'name': criteria.get('name', ''),
                            'finding': criteria.get('finding', '')[:150] + '...' if len(criteria.get('finding', '')) > 150 else criteria.get('finding', '')
                        })
        
        # Erstelle Empfehlungen
        if high_priority_criteria:
            title = f'Kritische WCAG-Verstoesse beheben ({len(high_priority_criteria)} Kriterien)'
            description = f'Es wurden {len(high_priority_criteria)} kritische WCAG-Verstoesse identifiziert, die sofort behoben werden muessen: ' + \
                         ', '.join([f"{c['criterion']} ({c['module']})" for c in high_priority_criteria[:5]]) + \
                         ('...' if len(high_priority_criteria) > 5 else '')
            recommendations.append({
                'title': self._clean_text_for_pdf(title),
                'description': self._clean_text_for_pdf(description)
            })
        
        if immediate_actions:
            top_immediate = immediate_actions[:3]  # Top 3 sofortige Maßnahmen
            title = 'Sofortige Massnahmen umsetzen'
            description = 'Folgende Massnahmen sollten umgehend umgesetzt werden: ' + \
                         ', '.join([self._clean_text_for_pdf(action.get('title', '')) for action in top_immediate])
            recommendations.append({
                'title': self._clean_text_for_pdf(title),
                'description': self._clean_text_for_pdf(description)
            })
        
        if short_term_actions:
            title = 'Kurzfristige Verbesserungen planen'
            description = f'{len(short_term_actions)} kurzfristige Verbesserungsmasnahmen wurden identifiziert. Diese sollten in den naechsten 2-4 Wochen umgesetzt werden.'
            recommendations.append({
                'title': self._clean_text_for_pdf(title),
                'description': self._clean_text_for_pdf(description)
            })
        
        # Standard-Empfehlungen wenn wenig Probleme
        if not recommendations:
            title = 'Regelmaessige Barrierefreiheitspruefungen'
            description = 'Ihre Website zeigt eine gute WCAG-Compliance. Fuehren Sie regelmaessige Analysen durch, um diese Standards aufrechtzuerhalten und bei Aenderungen sicherzustellen, dass die Barrierefreiheit gewaehrleistet bleibt.'
            recommendations.append({
                'title': self._clean_text_for_pdf(title),
                'description': self._clean_text_for_pdf(description)
            })
        
        return recommendations[:5]  # Maximal 5 Empfehlungen
    
    def _translate_status(self, status: str) -> str:
        """Übersetzt Status ins Deutsche"""
        translations = {
            'completed': 'Abgeschlossen',
            'running': 'Läuft',
            'failed': 'Fehlgeschlagen',
            'pending': 'Wartend'
        }
        return translations.get(status, status)
    
    def _format_module_title(self, module_name: str) -> str:
        """Formatiert Modul-Namen für bessere Lesbarkeit"""
        name_mappings = {
            '1_1_textalternativen': '1.1 Textalternativen',
            '1_2_zeitbasierte_medien': '1.2 Zeitbasierte Medien',
            '1_3_anpassbare_darstellung': '1.3 Anpassbare Darstellung',
            '1_4_wahrnehmbare_unterscheidungen': '1.4 Wahrnehmbare Unterscheidungen',
            '2_1_tastaturbedienung': '2.1 Tastaturbedienung',
            '2_2_genuegend_zeit': '2.2 Genügend Zeit',
            '2_3_anfaelle_vermeiden': '2.3 Anfälle vermeiden',
            '2_4_navigation': '2.4 Navigation',
            '3_1_lesbarkeit_sprache': '3.1 Lesbarkeit und Sprache',
            '3_2_vorhersehbarkeit': '3.2 Vorhersehbarkeit',
            '3_3_eingabeunterstuetzung': '3.3 Eingabeunterstützung',
            '4_1_robustheit_kompatibilitaet': '4.1 Robustheit und Kompatibilität'
        }
        return name_mappings.get(module_name, module_name.replace('_', ' ').title())
    
    def _extract_module_info(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert relevante Informationen aus einem Modul"""
        result = module.get('result', {})
        parsed_analysis = result.get('parsed_analysis', {})
        
        info = {
            'status': 'Unbekannt',
            'score': 0,
            'violations': 0,
            'warnings': 0,
            'compliance_level': '',
            'summary': '',
            'findings': []
        }
        
        # Neues Format
        if parsed_analysis and parsed_analysis.get('analysis_result'):
            analysis = parsed_analysis['analysis_result']
            
            if analysis.get('summary'):
                info['score'] = analysis['summary'].get('score', 0)
                info['compliance_level'] = analysis['summary'].get('compliance_level', '')
                info['summary'] = analysis['summary'].get('overall_assessment', '')
                info['status'] = 'Bestanden' if info['score'] >= 80 else 'Nicht bestanden'
            
            if analysis.get('criteria_evaluation'):
                for criteria in analysis['criteria_evaluation']:
                    if criteria.get('status') == 'FAILED':
                        info['violations'] += 1
                        if criteria.get('finding'):
                            info['findings'].append(criteria['finding'])
                    elif criteria.get('status') in ['PARTIAL', 'WARNING']:
                        info['warnings'] += 1
        
        # Legacy Format
        elif parsed_analysis and parsed_analysis.get('gesamtbewertung'):
            gesamtbewertung = parsed_analysis['gesamtbewertung']
            info['score'] = gesamtbewertung.get('score', 0)
            info['violations'] = gesamtbewertung.get('kritische_probleme', 0)
            info['status'] = 'Bestanden' if gesamtbewertung.get('status') == 'GRÜN' else 'Nicht bestanden'
            info['summary'] = parsed_analysis.get('zusammenfassung', '')
            
            if parsed_analysis.get('detailbewertung'):
                for detail in parsed_analysis['detailbewertung']:
                    if detail.get('bewertung') == 'NICHT_ERFUELLT' and detail.get('befund'):
                        info['findings'].append(detail['befund'])
                    elif detail.get('bewertung') == 'TEILWEISE':
                        info['warnings'] += 1
        
        return info
    
    def _calculate_overall_stats(self, modules_data: list) -> tuple:
        """Berechnet Gesamtstatistiken mit dem neuen Scoring-System"""
        if self.use_new_scoring:
            return self._calculate_overall_stats_new_system(modules_data)
        else:
            return self._calculate_overall_stats_legacy(modules_data)
    
    def _calculate_overall_stats_new_system(self, modules_data: list) -> tuple:
        """Berechnet Gesamtstatistiken mit dem neuen WCAG-Scoring-System"""
        module_scores = {}
        
        for module in modules_data:
            if not module.get('result'):
                continue
            
            result = module.get('result', {})
            analysis_result = result.get('analysis_result')
            
            if analysis_result and analysis_result.get('criteria_evaluation'):
                # Verwende das neue Scoring-System
                module_name = module.get('module_name', 'unknown')
                wcag_principle = self._get_wcag_principle_from_module(module_name)
                
                score_result = wcag_scorer.calculate_module_score(
                    analysis_result['criteria_evaluation'],
                    wcag_principle
                )
                
                module_scores[module_name] = score_result
        
        if module_scores:
            # Berechne Gesamtscore mit Gewichtung
            overall_result = wcag_scorer.calculate_overall_score(module_scores)
            
            return (
                overall_result['score'],
                overall_result['details']['passed'],
                overall_result['details']['failed'],
                overall_result['details']['warnings']
            )
        else:
            return (0, 0, 0, 0)
    
    def _calculate_overall_stats_legacy(self, modules_data: list) -> tuple:
        """Legacy-Berechnung für Rückwärtskompatibilität"""
        total_score = 0
        passed_criteria = 0
        total_violations = 0
        total_warnings = 0
        valid_modules = 0
        
        for module in modules_data:
            info = self._extract_module_info(module)
            if info['score'] > 0:
                total_score += info['score']
                valid_modules += 1
            
            if info['status'] == 'Bestanden':
                passed_criteria += 1
            
            total_violations += info['violations']
            total_warnings += info['warnings']
        
        avg_score = total_score // valid_modules if valid_modules > 0 else 0
        return avg_score, passed_criteria, total_violations, total_warnings
    
    def _get_wcag_principle_from_module(self, module_name: str) -> str:
        """Bestimmt das WCAG-Prinzip basierend auf dem Modul-Namen"""
        if any(x in module_name.lower() for x in ['1_1', '1_2', '1_3', '1_4']):
            return 'perceivable'
        elif any(x in module_name.lower() for x in ['2_1', '2_2', '2_3', '2_4']):
            return 'operable'
        elif any(x in module_name.lower() for x in ['3_1', '3_2', '3_3']):
            return 'understandable'
        elif any(x in module_name.lower() for x in ['4_1']):
            return 'robust'
        else:
            return 'unknown' 