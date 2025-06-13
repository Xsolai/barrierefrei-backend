#!/usr/bin/env python3
"""
PDF-Generator für WCAG-Analyse-Berichte
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re
import html

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
    """Generiert PDF-Berichte aus WCAG-Analyse-Ergebnissen"""
    
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
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            return True
        except ImportError as e:
            self.logger.error(f"ReportLab nicht verfügbar: {e}")
            return False
    
    def _clean_text_for_pdf(self, text: str) -> str:
        """Bereinigt Text von HTML-Tags und problematischen Zeichen für PDF-Generation"""
        if not text:
            return ""
        
        # HTML-Entities dekodieren
        text = html.unescape(text)
        
        # HTML-Tags entfernen
        text = re.sub(r'<[^>]+>', '', text)
        
        # Mehrfache Leerzeichen reduzieren
        text = re.sub(r'\s+', ' ', text)
        
        # Problematische Zeichen ersetzen
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Umlaute explizit handhaben
        text = text.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
        text = text.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')
        text = text.replace('ß', 'ss')
        
        return text.strip()
    
    def generate_pdf_from_job_data(self, job_id: str, job_data: Dict[str, Any], 
                                   modules_data: list, output_path: Optional[str] = None) -> str:
        """
        Generiert PDF aus Job-Daten und Modul-Ergebnissen
        
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
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            clean_url = job_data.get('url', 'unknown').replace('https://', '').replace('http://', '').replace('/', '_')
            output_path = f"WCAG_Report_{clean_url}_{timestamp}.pdf"
        
        # Erstelle PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.black
        )
        
        criteria_style = ParagraphStyle(
            'CriteriaStyle',
            parent=styles['Heading4'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.darkred
        )
        
        # Titel
        story.append(Paragraph("🎯 WCAG Barrierefreiheits-Analyse", title_style))
        story.append(Spacer(1, 20))
        
        # Übersicht-Tabelle
        overview_data = [
            ['URL:', job_data.get('url', 'N/A')],
            ['Analysiert am:', datetime.fromisoformat(job_data.get('created_at', '')).strftime('%d.%m.%Y %H:%M') if job_data.get('created_at') else 'N/A'],
            ['Status:', self._translate_status(job_data.get('status', 'unknown'))],
            ['Plan:', job_data.get('plan', 'basic').upper()],
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 30))
        
        # Gesamtbewertung
        story.append(Paragraph("Gesamt-Bewertung", heading_style))
        
        # Berechne Gesamtstatistiken
        total_score, passed_criteria, total_violations, total_warnings = self._calculate_overall_stats(modules_data)
        
        stats_data = [
            ['Gesamt-Score:', f"{total_score} Punkte"],
            ['Kriterien bestanden:', str(passed_criteria)],
            ['Verstöße:', str(total_violations)],
            ['Warnungen:', str(total_warnings)]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # WCAG-Module Details
        story.append(Paragraph("Detaillierte Analyse nach WCAG-Kriterien", heading_style))
        story.append(Spacer(1, 15))
        
        # Sicherheitsüberprüfung für modules_data
        if not modules_data:
            story.append(Paragraph("Keine Modulergebnisse verfügbar.", styles['Normal']))
        else:
            for module in modules_data:
                if not module or not isinstance(module, dict):
                    continue
                    
                result = module.get('result', {})
                if not result or not isinstance(result, dict):
                    continue
                
                # Generiere vollständigen Modulinhalt mit Sicherheitsüberprüfungen
                try:
                    module_content = self._generate_complete_module_content(module, subheading_style, criteria_style, styles, Paragraph, Spacer, PageBreak)
                    if module_content:
                        story.extend(module_content)
                        story.append(PageBreak())
                except Exception as e:
                    self.logger.error(f"Fehler bei der Generierung des Modulinhalts: {str(e)}")
                    continue
        
        # Empfehlungen
        story.append(Paragraph("Prioritäre Empfehlungen", heading_style))
        story.append(Spacer(1, 15))
        
        try:
            recommendations = self._generate_comprehensive_recommendations(modules_data)
            for i, rec in enumerate(recommendations, 1):
                if not isinstance(rec, dict):
                    continue
                title = rec.get('title', '')
                description = rec.get('description', '')
                if title and description:
                    story.append(Paragraph(f"<b>{i}. {title}</b>", styles['Normal']))
                    story.append(Paragraph(description, styles['Normal']))
                    story.append(Spacer(1, 10))
        except Exception as e:
            self.logger.error(f"Fehler bei der Generierung der Empfehlungen: {str(e)}")
            story.append(Paragraph("Keine Empfehlungen verfügbar.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M')} | WCAG Barrierefreiheits-Analyse", footer_style))
        
        # PDF erstellen
        try:
            doc.build(story)
            self.logger.info(f"PDF-Bericht erfolgreich erstellt: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der PDF: {str(e)}")
            raise

    def _generate_complete_module_content(self, module: Dict[str, Any], subheading_style, criteria_style, styles, Paragraph, Spacer, PageBreak) -> list:
        """Generiert vollständigen Modulinhalt wie im Frontend"""
        content = []
        
        module_name = module.get('module_name', 'Unbekannt')
        result = module.get('result', {})
        
        # Modul-Titel
        module_title = self._format_module_title(module_name)
        content.append(Paragraph(module_title, subheading_style))
        content.append(Spacer(1, 10))
        
        # Überprüfe auf analysis_result (neues Format)
        analysis_result = result.get('analysis_result')
        if analysis_result:
            content.extend(self._generate_analysis_result_content(analysis_result, criteria_style, styles, Paragraph, Spacer))
        else:
            # Fallback für alte oder fehlende Daten
            content.append(Paragraph("Keine detaillierten Analyseergebnisse verfügbar.", styles['Normal']))
        
        content.append(Spacer(1, 20))
        return content
    
    def _generate_analysis_result_content(self, analysis_result: Dict[str, Any], criteria_style, styles, Paragraph, Spacer) -> list:
        """Generiert Inhalt aus analysis_result (wie Frontend)"""
        content = []
        
        # 1. Zusammenfassung
        summary = analysis_result.get('summary', {})
        if summary:
            content.append(Paragraph("<b>Gesamtbewertung</b>", criteria_style))
            
            # Score und Compliance Level
            score = summary.get('score', 0)
            compliance_level = summary.get('compliance_level', 'N/A')
            content.append(Paragraph(f"<b>Score:</b> {score}/100 Punkte", styles['Normal']))
            content.append(Paragraph(f"<b>Compliance Level:</b> {compliance_level}", styles['Normal']))
            
            # Gesamtbewertung
            overall_assessment = summary.get('overall_assessment', '')
            if overall_assessment:
                clean_assessment = self._clean_text_for_pdf(overall_assessment)
                content.append(Paragraph(f"<b>Bewertung:</b> {clean_assessment}", styles['Normal']))
            
            content.append(Spacer(1, 15))
        
        # 2. Kriterien-Bewertung
        criteria_evaluation = analysis_result.get('criteria_evaluation', [])
        if criteria_evaluation:
            content.append(Paragraph("<b>Kriterien-Bewertung</b>", criteria_style))
            content.append(Spacer(1, 10))
            
            for i, criteria in enumerate(criteria_evaluation, 1):
                # Kriterium Header
                criterion_id = criteria.get('criterion_id', '')
                name = self._clean_text_for_pdf(criteria.get('name', 'Unbekannt'))
                status = criteria.get('status', 'UNKNOWN')
                
                status_text = {
                    'FAILED': 'NICHT ERFUELLT',
                    'PARTIAL': 'TEILWEISE ERFUELLT', 
                    'WARNING': 'WARNUNG',
                    'PASSED': 'ERFUELLT'
                }.get(status, status)
                
                content.append(Paragraph(f"<b>{criterion_id} {name}</b> - <i>{status_text}</i>", styles['Heading4']))
                
                # Befund
                finding = criteria.get('finding', '')
                if finding:
                    clean_finding = self._clean_text_for_pdf(finding)
                    content.append(Paragraph(f"<b>Befund:</b> {clean_finding}", styles['Normal']))
                
                # Auswirkung
                impact = criteria.get('impact', '')
                if impact:
                    clean_impact = self._clean_text_for_pdf(impact)
                    content.append(Paragraph(f"<b>Auswirkung:</b> {clean_impact}", styles['Normal']))
                
                # Beispiele
                examples = criteria.get('examples', [])
                if examples:
                    content.append(Paragraph("<b>Beispiele:</b>", styles['Normal']))
                    for example in examples[:3]:  # Maximal 3 Beispiele
                        clean_example = self._clean_text_for_pdf(str(example))
                        content.append(Paragraph(f"• {clean_example}", styles['Normal']))
                
                # Empfehlung
                recommendation = criteria.get('recommendation', '')
                if recommendation:
                    clean_recommendation = self._clean_text_for_pdf(recommendation)
                    content.append(Paragraph(f"<b>Empfehlung:</b> {clean_recommendation}", styles['Normal']))
                
                content.append(Spacer(1, 12))
        
        # 3. Priorisierte Maßnahmen
        priority_actions = analysis_result.get('priority_actions', {})
        if priority_actions:
            content.append(Paragraph("<b>Priorisierte Massnahmen</b>", criteria_style))
            content.append(Spacer(1, 10))
            
            for priority, actions in priority_actions.items():
                if not actions:
                    continue
                    
                priority_text = {
                    'immediate': 'Sofortige Massnahmen',
                    'short_term': 'Kurzfristige Massnahmen',
                    'long_term': 'Langfristige Massnahmen'
                }.get(priority, priority.title())
                
                content.append(Paragraph(f"<b>{priority_text}:</b>", styles['Heading4']))
                
                for action in actions:
                    title = self._clean_text_for_pdf(action.get('title', ''))
                    effort = action.get('effort', '')
                    description = self._clean_text_for_pdf(action.get('description', ''))
                    affected_criteria = action.get('affected_criteria', [])
                    
                    content.append(Paragraph(f"<b>• {title}</b> (Aufwand: {effort})", styles['Normal']))
                    if description:
                        content.append(Paragraph(f"  {description}", styles['Normal']))
                    if affected_criteria:
                        criteria_list = ', '.join(affected_criteria)
                        content.append(Paragraph(f"  <i>Betroffene Kriterien: {criteria_list}</i>", styles['Normal']))
                    content.append(Spacer(1, 8))
                
                content.append(Spacer(1, 10))
        
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
                info['status'] = 'Bestanden' if info['score'] >= 70 else 'Nicht bestanden'
            
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