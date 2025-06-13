#!/usr/bin/env python3
"""
Verbessertes WCAG-Scoring-System
Einheitliche und benutzerfreundliche Bewertung der Barrierefreiheit
"""

import logging
from typing import Dict, Any, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    AAA = "AAA"
    AA = "AA" 
    A = "A"
    PARTIAL = "PARTIAL"
    NONE = "NONE"

class WCAGScoringSystem:
    """Einheitliches WCAG-Scoring-System"""
    
    def __init__(self):
        # Gewichtung der WCAG-Prinzipien (Summe = 100%)
        self.principle_weights = {
            "perceivable": 0.30,      # 30% - Wahrnehmbarkeit (kritisch)
            "operable": 0.30,         # 30% - Bedienbarkeit (kritisch) 
            "understandable": 0.25,   # 25% - Verständlichkeit
            "robust": 0.15           # 15% - Robustheit
        }
        
        # Schweregrad-Gewichtung für Verstöße
        self.severity_weights = {
            "CRITICAL": 1.0,    # Vollständiger Punktabzug
            "MAJOR": 0.7,       # 70% Punktabzug
            "MODERATE": 0.4,    # 40% Punktabzug
            "MINOR": 0.2        # 20% Punktabzug
        }
        
        # Verbessertes Compliance-Level-Mapping
        self.compliance_thresholds = {
            90: ComplianceLevel.AAA,
            80: ComplianceLevel.AA,
            65: ComplianceLevel.A,
            40: ComplianceLevel.PARTIAL,
            0: ComplianceLevel.NONE
        }
    
    def calculate_module_score(self, criteria_evaluation: List[Dict[str, Any]], 
                             wcag_principle: str = "") -> Dict[str, Any]:
        """
        Berechnet Score für ein einzelnes WCAG-Modul
        
        Args:
            criteria_evaluation: Liste der bewerteten Kriterien
            wcag_principle: WCAG-Prinzip (perceivable, operable, etc.)
            
        Returns:
            Dict mit Score, Compliance Level und Details
        """
        if not criteria_evaluation:
            return self._create_score_result(0, ComplianceLevel.NONE, "Keine Kriterien bewertet")
        
        total_criteria = len(criteria_evaluation)
        score_sum = 0
        
        # Zähle verschiedene Status-Typen
        passed = 0
        failed = 0
        partial = 0
        warnings = 0
        
        for criteria in criteria_evaluation:
            status = criteria.get('status', 'UNKNOWN').upper()
            
            if status == 'PASSED':
                score_sum += 100
                passed += 1
            elif status == 'FAILED':
                # Berücksichtige Schweregrad
                severity = criteria.get('severity', 'MAJOR').upper()
                penalty = self.severity_weights.get(severity, 0.7) * 100
                score_sum += max(0, 100 - penalty)  # Mindestens 0 Punkte
                failed += 1
            elif status in ['PARTIAL', 'WARNING']:
                score_sum += 65  # Teilweise erfüllt = 65%
                if status == 'PARTIAL':
                    partial += 1
                else:
                    warnings += 1
            else:
                score_sum += 30  # Unbekannt = 30%
        
        # Durchschnittsscore berechnen
        average_score = score_sum / total_criteria if total_criteria > 0 else 0
        
        # Score für bessere Nutzererfahrung anpassen
        adjusted_score = self._adjust_score_for_ux(average_score, failed, total_criteria)
        
        # Compliance Level bestimmen
        compliance_level = self._determine_compliance_level(adjusted_score, failed, total_criteria)
        
        # Assessment-Text generieren
        assessment = self._generate_assessment(adjusted_score, compliance_level, passed, failed, partial, warnings)
        
        return self._create_score_result(adjusted_score, compliance_level, assessment, {
            'passed': passed,
            'failed': failed,
            'partial': partial,
            'warnings': warnings,
            'total': total_criteria
        })
    
    def _adjust_score_for_ux(self, raw_score: float, failed_count: int, total_count: int) -> float:
        """
        Passt den Score für bessere Nutzererfahrung an
        Vermeidet extrem niedrige Scores, die demotivierend sind
        """
        # Basis-Score (Minimum 25 Punkte für jede Analyse)
        base_score = 25
        
        # Skalierter Score (75 Punkte basierend auf Performance)
        scaled_score = (raw_score * 0.75)
        
        final_score = base_score + scaled_score
        
        # Bonus für geringen Anteil kritischer Fehler
        if total_count > 0:
            failure_rate = failed_count / total_count
            if failure_rate < 0.2:  # Weniger als 20% Failures
                final_score += 5
            elif failure_rate < 0.1:  # Weniger als 10% Failures
                final_score += 10
        
        return min(100, max(25, final_score))  # Score zwischen 25-100
    
    def _determine_compliance_level(self, score: float, failed_count: int, total_count: int) -> ComplianceLevel:
        """Bestimmt das Compliance Level basierend auf Score und Fehlern"""
        
        # Automatisch NONE wenn mehr als 50% der Kriterien fehlschlagen
        if total_count > 0 and (failed_count / total_count) > 0.5:
            return ComplianceLevel.NONE
        
        # Score-basierte Bestimmung
        for threshold, level in sorted(self.compliance_thresholds.items(), reverse=True):
            if score >= threshold:
                return level
        
        return ComplianceLevel.NONE
    
    def _generate_assessment(self, score: float, compliance_level: ComplianceLevel, 
                           passed: int, failed: int, partial: int, warnings: int) -> str:
        """Generiert nutzerfreundlichen Assessment-Text"""
        
        total = passed + failed + partial + warnings
        
        if score >= 90:
            return f"Ausgezeichnete Barrierefreiheit! {passed}/{total} Kriterien vollständig erfüllt. Die Website entspricht hohen WCAG-Standards."
        elif score >= 80:
            return f"Gute Barrierefreiheit mit kleineren Verbesserungsmöglichkeiten. {passed}/{total} Kriterien erfüllt, {failed} kritische Probleme identifiziert."
        elif score >= 65:
            return f"Grundlegende Barrierefreiheit vorhanden. {passed}/{total} Kriterien erfüllt. {failed} Probleme sollten behoben werden."
        elif score >= 40:
            return f"Barrierefreiheit teilweise umgesetzt. {failed} kritische Probleme erfordern Aufmerksamkeit, um die Zugänglichkeit zu verbessern."
        else:
            return f"Erhebliche Barrieren identifiziert. {failed} kritische Probleme beeinträchtigen die Nutzbarkeit. Sofortige Maßnahmen empfohlen."
    
    def _create_score_result(self, score: float, compliance_level: ComplianceLevel, 
                           assessment: str, details: Dict[str, int] = None) -> Dict[str, Any]:
        """Erstellt einheitliches Score-Result-Objekt"""
        return {
            'score': round(score, 1),
            'compliance_level': compliance_level.value,
            'overall_assessment': assessment,
            'details': details or {},
            'scoring_version': '2.0'
        }
    
    def calculate_overall_score(self, module_scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Berechnet den Gesamtscore aus allen Modulen
        
        Args:
            module_scores: Dict mit Modul-Namen als Keys und Score-Results als Values
            
        Returns:
            Gesamtscore mit gewichteter Bewertung
        """
        if not module_scores:
            return self._create_score_result(0, ComplianceLevel.NONE, "Keine Module bewertet")
        
        weighted_score = 0
        total_weight = 0
        
        # Sammle Statistiken
        total_passed = 0
        total_failed = 0
        total_partial = 0
        total_warnings = 0
        
        # Gewichtete Berechnung nach WCAG-Prinzipien
        for module_name, module_result in module_scores.items():
            # Bestimme Gewicht basierend auf Modul-Name
            weight = self._get_module_weight(module_name)
            module_score = module_result.get('score', 0)
            
            weighted_score += module_score * weight
            total_weight += weight
            
            # Sammle Details
            details = module_result.get('details', {})
            total_passed += details.get('passed', 0)
            total_failed += details.get('failed', 0)
            total_partial += details.get('partial', 0)
            total_warnings += details.get('warnings', 0)
        
        # Gesamtscore berechnen
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0
        
        # Compliance Level für Gesamtbewertung
        total_criteria = total_passed + total_failed + total_partial + total_warnings
        compliance_level = self._determine_compliance_level(final_score, total_failed, total_criteria)
        
        # Gesamtbewertung generieren
        assessment = self._generate_overall_assessment(final_score, compliance_level, 
                                                     total_passed, total_failed, 
                                                     total_partial, total_warnings, 
                                                     len(module_scores))
        
        return self._create_score_result(final_score, compliance_level, assessment, {
            'total_modules': len(module_scores),
            'passed': total_passed,
            'failed': total_failed,
            'partial': total_partial,
            'warnings': total_warnings,
            'total_criteria': total_criteria
        })
    
    def _get_module_weight(self, module_name: str) -> float:
        """Bestimmt Gewichtung eines Moduls basierend auf WCAG-Prinzip"""
        
        # Mapping von Modul-Namen zu WCAG-Prinzipien
        if any(x in module_name.lower() for x in ['1_1', '1_2', '1_3', '1_4', 'perceivable', 'wahrnehmbar']):
            return self.principle_weights['perceivable']
        elif any(x in module_name.lower() for x in ['2_1', '2_2', '2_3', '2_4', 'operable', 'bedienbar']):
            return self.principle_weights['operable']
        elif any(x in module_name.lower() for x in ['3_1', '3_2', '3_3', 'understandable', 'verständlich']):
            return self.principle_weights['understandable']
        elif any(x in module_name.lower() for x in ['4_1', 'robust', 'kompatibel']):
            return self.principle_weights['robust']
        else:
            # Gleichmäßige Verteilung wenn nicht zuordenbar
            return 1.0 / len(self.principle_weights)
    
    def _generate_overall_assessment(self, score: float, compliance_level: ComplianceLevel,
                                   passed: int, failed: int, partial: int, warnings: int,
                                   module_count: int) -> str:
        """Generiert Gesamtbewertungstext"""
        
        total_criteria = passed + failed + partial + warnings
        
        if score >= 85:
            return f"Hervorragende Barrierefreiheit! {module_count} WCAG-Module analysiert, {passed}/{total_criteria} Kriterien erfüllt. Die Website ist gut zugänglich."
        elif score >= 75:
            return f"Gute Barrierefreiheit mit Verbesserungspotential. {passed}/{total_criteria} Kriterien erfüllt, {failed} kritische Probleme in {module_count} Modulen."
        elif score >= 60:
            return f"Solide Grundlage mit wichtigen Verbesserungen nötig. {failed} kritische Probleme sollten prioritär behandelt werden."
        elif score >= 45:
            return f"Barrierefreiheit teilweise vorhanden. {failed} kritische Probleme beeinträchtigen die Zugänglichkeit erheblich."
        else:
            return f"Umfassende Überarbeitung empfohlen. {failed} kritische Barrieren verhindern eine gute Zugänglichkeit."

# Globale Instanz für einheitliche Nutzung
wcag_scorer = WCAGScoringSystem() 