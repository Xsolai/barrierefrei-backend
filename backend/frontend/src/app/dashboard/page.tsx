"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/lib/auth-context";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { de } from "date-fns/locale";
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Loader2, 
  ExternalLink,
  Download,
  Eye,
  X,
  BarChart3,
  FileText,
  AlertTriangle,
  TrendingUp,
  Image,
  Palette,
  Navigation,
  Languages,
  Shield,
  ChevronDown,
  ChevronUp,
  Info,
  CheckCircle2,
  XCircle,
  AlertTriangle as Warning
} from "lucide-react";
import Footer from "@/components/footer";
import { api } from "@/lib/api";
import { RoleGuard } from "@/components/role-guard";

interface AnalysisResult {
  summary: {
    score: number;
    compliance_level: string;
    overall_assessment: string;
  };
  priority_actions: {
    immediate: PriorityAction[];
    short_term: PriorityAction[];
    long_term: PriorityAction[];
  };
  criteria_evaluation: CriteriaEvaluation[];
  created_at: string;
}

interface PriorityAction {
  title: string;
  effort: string;
  description: string;
  affected_criteria: string[];
}

interface CriteriaEvaluation {
  name: string;
  impact: string;
  status: string;
  finding: string;
  examples: string[];
  criterion_id: string;
  recommendation: string;
}

interface WCAGViolation {
  criterion?: string;
  title?: string;
  description: string;
  impact?: string;
}

interface AnalysisFinding {
  id?: string; 
  criterion?: string;
  title?: string;
  description?: string; 
  help?: string;
  impact?: string;
  html?: string;
  nodes?: any[];
}

interface WCAGInfo {
  name?: string;
  principle?: string;
  description?: string;
}

interface Gesamtbewertung {
  status?: string;
  score?: number;
  kritische_probleme?: number;
  erfuellte_kriterien?: number;
  gepruefte_kriterien?: number;
}

interface DetailbewertungKriterium {
  kriterium_id?: string;
  kriterium_name?: string;
  bewertung?: string;
  befund?: string;
  auswirkung?: string;
  beispiele?: string[];
  empfehlung?: string;
}

interface Massnahme {
  titel?: string;
  beschreibung?: string;
  aufwand?: string;
  betroffene_kriterien?: string[];
}

interface PriorisierteMassnahmen {
  sofort?: Massnahme[];
  kurzfristig?: Massnahme[];
  langfristig?: Massnahme[];
}

interface ParsedAnalysisData {
  analysis_result?: AnalysisResult;
  zusammenfassung?: string;
  gesamtbewertung?: Gesamtbewertung;
  detailbewertung?: DetailbewertungKriterium[];
  priorisierte_massnahmen?: PriorisierteMassnahmen;
  [key: string]: any; 
}

interface ModuleResult {
  id: string;
  module_name: string;
  status: 'completed' | 'failed' | 'running';
  result?: {
    timestamp?: string;
    wcag_area?: string;
    wcag_info?: WCAGInfo;
    model_used?: string;
    token_usage?: {
      total_tokens?: number;
    };
    analysis_content?: string;
    api_call_successful?: boolean;
    parsed_analysis?: ParsedAnalysisData | null;
    analysis_result?: AnalysisResult;
    gesamtbewertung?: Gesamtbewertung;
    zusammenfassung?: string;
    detailbewertung?: DetailbewertungKriterium[];
    priorisierte_massnahmen?: PriorisierteMassnahmen;
    [key: string]: any;
  };
  error?: string;
  completed_at?: string;
}

interface JobDetails {
  id: string;
  url: string;
  status: string;
  plan: string;
  created_at: string;
  progress: number;
  error?: string;
  user_id?: string;
}

interface AnalysisReport {
  id: string;
  job_id: string;
  summary?: any;
  recommendations?: string[];
  score?: number;
  created_at: string;
}

function DashboardContent() {
  const { user, userRole } = useAuth();
  const [jobs, setJobs] = useState<JobDetails[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedJobDetails, setSelectedJobDetails] = useState<JobDetails | null>(null);
  const [selectedJobModules, setSelectedJobModules] = useState<ModuleResult[]>([]);
  const [selectedJobReport, setSelectedJobReport] = useState<AnalysisReport | null>(null);
  const [isLoadingResults, setIsLoadingResults] = useState(false);
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());
  const [overallStats, setOverallStats] = useState({
    passedCriteria: 0,
    totalWarnings: 0,
    totalViolations: 0,
    overallScore: 0
  });
  const searchParams = useSearchParams();
  const highlightJobId = searchParams.get("job");
  const [showResultsModal, setShowResultsModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    const fetchJobs = async () => {
      if (!user?.id) return;

      setIsLoading(true);
      try {
        console.log(`👤 Lade Jobs für User: ${user.id} mit Rolle: ${userRole}`);
        
        let query = supabase.from('analysis_jobs').select('*');

        if (userRole !== 'admin') {
          query = query.eq('user_id', user.id);
        }
        
        const { data, error } = await query.order('created_at', { ascending: false });

        if (error) {
          console.error("❌ Supabase error:", error);
          throw error;
        }

        console.log(`✅ ${data?.length || 0} Jobs gefunden.`);
        setJobs(data || []);

      } catch (error) {
        console.error("❌ Error fetching jobs:", error);
        toast.error("Fehler beim Laden der Analysen");
        setJobs([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobs();
  }, [user, userRole]);

  useEffect(() => {
    calculateOverallScore();
  }, [selectedJobModules]);

  const handleViewResults = async (jobId: string) => {
    if (!supabase) {
      toast.error("Supabase-Verbindung nicht verfügbar");
      return;
    }

    setIsLoadingResults(true);
    setSelectedJobId(jobId);
    setExpandedModules(new Set());

    try {
      const { data: jobData, error: jobError } = await supabase
        .from('analysis_jobs')
        .select('*')
        .eq('id', jobId)
        .single();
      if (jobError) throw jobError;
      setSelectedJobDetails(jobData);

      const { data: modulesData, error: modulesError } = await supabase
        .from('analysis_results')
        .select('*')
        .eq('job_id', jobId)
        .order('created_at', { ascending: true });
      if (modulesError) throw modulesError;

      const processedModules = (modulesData || []).map((mod: any) => {
        console.log("Verarbeite Modul:", mod.module_name, "Rohdaten:", mod);
        console.log("Modul result:", mod.result);
        console.log("Modul analysis_content:", mod.result?.analysis_content);
        
        let parsed = null;
        
        if (mod.result?.analysis_content) {
          parsed = parseAnalysisContent(mod.result.analysis_content);
        }
        
        if (!parsed && mod.result) {
          if (mod.result.analysis_result || mod.result.gesamtbewertung || mod.result.zusammenfassung) {
            console.log("Verwende result direkt als parsed_analysis für", mod.module_name);
            parsed = mod.result;
          }
          else if (typeof mod.result === 'string') {
            console.log("Versuche result als String zu parsen für", mod.module_name);
            parsed = parseAnalysisContent(mod.result);
          }
        }
        
        console.log("Parsed result für", mod.module_name, ":", parsed);
        
        return {
          ...mod,
          result: {
            ...mod.result,
            parsed_analysis: parsed,
          },
        };
      });
      setSelectedJobModules(processedModules as ModuleResult[]);

      const { data: reportData, error: reportError } = await supabase
        .from('analysis_reports')
        .select('*')
        .eq('job_id', jobId)
        .single();
      if (reportError && reportError.code !== 'PGRST116') throw reportError;
      setSelectedJobReport(reportData);

      let totalPassed = 0;
      let totalWarnings = 0;
      let totalViolations = 0;
      let scoreSum = 0;
      let validScores = 0;

      processedModules.forEach((module: any) => {
        const parsed = module.result?.parsed_analysis;
        if (parsed) {
          if (parsed.analysis_result?.summary) {
            const score = parsed.analysis_result.summary.score || 0;
            if (score > 0) {
              scoreSum += score;
              validScores++;
            }
            if (score >= 70) totalPassed++;
            
            parsed.analysis_result.criteria_evaluation?.forEach((criteria: any) => {
              if (criteria.status === 'FAILED') totalViolations++;
              if (criteria.status === 'WARNING' || criteria.status === 'PARTIAL') totalWarnings++;
            });
          }
          else if (parsed.gesamtbewertung) {
            const score = parsed.gesamtbewertung.score || 0;
            if (score > 0) {
              scoreSum += score;
              validScores++;
            }
            if (parsed.gesamtbewertung.status === 'GRÜN') totalPassed++;
            totalViolations += parsed.gesamtbewertung.kritische_probleme || 0;
            
            parsed.detailbewertung?.forEach((detail: any) => {
              if (detail.bewertung === 'TEILWEISE') totalWarnings++;
            });
          }
        }
      });

      setOverallStats({
        passedCriteria: totalPassed,
        totalWarnings,
        totalViolations,
        overallScore: validScores > 0 ? Math.round(scoreSum / validScores) : 0
      });

    } catch (error) {
      console.error("Fehler beim Laden der Ergebnisse:", error);
      toast.error("Fehler beim Laden der Ergebnisse");
    } finally {
      setIsLoadingResults(false);
    }
  };

  const handleDownloadPDF = async (jobId: string, event?: React.MouseEvent) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';
      const response = await fetch(`${apiUrl}/download-pdf/${jobId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `WCAG_Bericht_${jobId.slice(0, 8)}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success("PDF-Bericht wurde heruntergeladen!");
    } catch (error) {
      console.error("Fehler beim PDF-Download:", error);
      toast.error("Fehler beim Herunterladen des PDF-Berichts");
    }
  };

  const toggleModule = (moduleName: string) => {
    setExpandedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleName)) {
        newSet.delete(moduleName);
      } else {
        newSet.add(moduleName);
      }
      return newSet;
    });
  };

  const calculateOverallScore = () => {
    if (!selectedJobModules || selectedJobModules.length === 0) {
      setOverallStats({ passedCriteria: 0, totalWarnings: 0, totalViolations: 0, overallScore: 0 });
      return 0;
    }
    
    let totalScoreSum = 0;
    let validModulesCount = 0;
    let totalViolations = 0;
    let totalWarnings = 0;
    let totalPassedCriteria = 0;
    
    selectedJobModules.forEach(module => {
      const parsedAnalysis = module.result?.parsed_analysis;

      if (parsedAnalysis) {
        if (parsedAnalysis.analysis_result) {
          const analysisResult = parsedAnalysis.analysis_result;
          
          const moduleScore = analysisResult.summary?.score || 0;
          if (moduleScore > 0) {
            totalScoreSum += moduleScore;
            validModulesCount++;
          }
          
          if (analysisResult.criteria_evaluation) {
            analysisResult.criteria_evaluation.forEach((criteria: CriteriaEvaluation) => {
              if (criteria.status === "FAILED") {
                totalViolations++;
              } else if (criteria.status === "PARTIAL" || criteria.status === "WARNING") {
                totalWarnings++;
              } else if (criteria.status === "PASSED") {
                totalPassedCriteria++;
              }
            });
          }
          
          if (analysisResult.summary?.compliance_level === "AAA" || 
              analysisResult.summary?.compliance_level === "AA" ||
              (analysisResult.summary?.score && analysisResult.summary.score >= 80)) {
          }
        }
        else if (parsedAnalysis.gesamtbewertung) {
          totalViolations += parsedAnalysis.gesamtbewertung.kritische_probleme || 0;
          
          if (parsedAnalysis.detailbewertung) {
            parsedAnalysis.detailbewertung.forEach(item => {
              if (item.bewertung === "TEILWEISE") {
                totalWarnings++;
              } else if (item.bewertung === "ERFUELLT") {
                totalPassedCriteria++;
              }
            });
          }

          if (parsedAnalysis.gesamtbewertung.status === "GRÜN" || 
              parsedAnalysis.gesamtbewertung.status === "PASSED" || 
              (parsedAnalysis.gesamtbewertung.score !== undefined && parsedAnalysis.gesamtbewertung.score >= 90)) {
            totalPassedCriteria++;
          }
          
          const currentModuleScore = calculateModuleScore(module.result);
          if (currentModuleScore > 0) { 
            totalScoreSum += currentModuleScore;
            validModulesCount++;
          }
        }
      }
    });
    
    const averageScore = validModulesCount > 0 ? Math.round(totalScoreSum / validModulesCount) : 0;
    
    setOverallStats({
      passedCriteria: totalPassedCriteria,
      totalWarnings: totalWarnings,
      totalViolations: totalViolations,
      overallScore: averageScore
    });
    
    return averageScore;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return (
          <span className="status-badge running">
            <Loader2 size={12} />
            Läuft
          </span>
        );
      case "completed":
        return (
          <span className="status-badge completed">
            <CheckCircle size={12} />
            Abgeschlossen
          </span>
        );
      case "failed":
        return (
          <span className="status-badge failed">
            <AlertCircle size={12} />
            Fehlgeschlagen
          </span>
        );
      default:
        return (
          <span className="status-badge pending">
            <Clock size={12} />
            Unbekannt
          </span>
        );
    }
  };

  const getPlanBadge = (plan: string) => {
    const planConfig = {
      basic: { label: "Basic", class: "plan-badge basic" },
      pro: { label: "Pro", class: "plan-badge pro" },
      enterprise: { label: "Enterprise", class: "plan-badge enterprise" },
    };
    
    const config = planConfig[plan as keyof typeof planConfig] || planConfig.basic;
    
    return (
      <span className={config.class}>
        {config.label}
      </span>
    );
  };

  const formatModuleName = (moduleName: string) => {
    const nameMap: { [key: string]: string } = {
      '1_1_textalternativen': '1.1 Textalternativen',
      '1_2_zeitbasierte_medien': '1.2 Zeitbasierte Medien',
      '1_3_anpassbare_darstellung': '1.3 Anpassbare Darstellung',
      '2_4_navigation': '2.4 Navigation',
      '3_1_lesbarkeit_sprache': '3.1 Lesbarkeit & Sprache',
      '4_1_robustheit_kompatibilitaet': '4.1 Robustheit & Kompatibilität'
    };
    
    return nameMap[moduleName] || moduleName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/(\d+)\.(\d+)/, '$1.$2 ');
  };

  const getModuleIcon = (moduleName: string) => {
    if (moduleName.includes('text') || moduleName.includes('alt')) return <Image size={20} />;
    if (moduleName.includes('medien')) return <FileText size={20} />;
    if (moduleName.includes('darstellung')) return <Palette size={20} />;
    if (moduleName.includes('navigation')) return <Navigation size={20} />;
    if (moduleName.includes('sprache')) return <Languages size={20} />;
    if (moduleName.includes('robust') || moduleName.includes('kompatibil')) return <Shield size={20} />;
    return <AlertTriangle size={20} />;
  };

  const getModuleDescription = (moduleName: string): string => {
    const descriptions: { [key: string]: string } = {
      '1_1_textalternativen': 'Prüfung von Alternativtexten für Bilder, Icons und andere visuelle Inhalte',
      '1_2_zeitbasierte_medien': 'Analyse von Videos, Audios und anderen zeitbasierten Medieninhalten',
      '1_3_anpassbare_darstellung': 'Bewertung der Anpassbarkeit und Strukturierung von Inhalten',
      '2_4_navigation': 'Überprüfung der Navigationsstruktur und Bedienbarkeit',
      '3_1_lesbarkeit_sprache': 'Analyse der Sprachverwendung und Lesbarkeit',
      '4_1_robustheit_kompatibilitaet': 'Test der technischen Kompatibilität mit Assistenztechnologien'
    };
    
    return descriptions[moduleName] || 'Detaillierte Analyse dieses WCAG-Kriteriums';
  };

  const calculateModuleScore = (moduleResultData: ModuleResult['result'] | undefined): number => {
    if (!moduleResultData?.parsed_analysis) {
      return 0;
    }

    const parsedAnalysis = moduleResultData.parsed_analysis;
    
    if (parsedAnalysis.analysis_result?.summary?.score !== undefined) {
      const score = parsedAnalysis.analysis_result.summary.score;
      return Math.max(25, Math.min(100, score));
    }
    
    if (parsedAnalysis.gesamtbewertung?.score !== undefined) {
      const score = parsedAnalysis.gesamtbewertung.score;
      return Math.max(25, Math.min(100, score));
    }
    
    return 25;
  };

  const getComplianceLevel = (score: number): string => {
    if (score >= 90) return "AAA";
    if (score >= 80) return "AA";  
    if (score >= 65) return "A";
    if (score >= 40) return "PARTIAL";
    return "NONE";
  };

  const getComplianceColor = (level: string): string => {
    switch (level) {
      case "AAA": return "#059669";
      case "AA": return "#10b981";  
      case "A": return "#fbbf24";   
      case "PARTIAL": return "#f59e0b";
      case "NONE": return "#dc2626";
      default: return "#6b7280";    
    }
  };

  const getScoreDescription = (score: number): string => {
    if (score >= 85) return "Hervorragende Barrierefreiheit";
    if (score >= 75) return "Gute Barrierefreiheit"; 
    if (score >= 60) return "Solide Grundlage";
    if (score >= 45) return "Verbesserungsbedarf";
    return "Umfassende Überarbeitung empfohlen";
  };

  const parseAnalysisContent = (analysisContent: string | undefined | null | any): any | null => {
    if (!analysisContent) {
      console.log("parseAnalysisContent: Kein analysisContent vorhanden");
      return null;
    }
    
    console.log("parseAnalysisContent: Original analysisContent:", analysisContent);
    console.log("parseAnalysisContent: Type:", typeof analysisContent);
    
    if (typeof analysisContent === 'object' && analysisContent !== null) {
      console.log("parseAnalysisContent: analysisContent ist bereits ein Objekt:", analysisContent);
      return analysisContent;
    }
    
    if (typeof analysisContent === 'string') {
      try {
        const cleanedJsonString = analysisContent.replace(/^```json\n|\n```$/g, '');
        console.log("parseAnalysisContent: Nach Bereinigung:", cleanedJsonString);
        
        const parsed = JSON.parse(cleanedJsonString);
        console.log("parseAnalysisContent: Erfolgreich geparst:", parsed);
        return parsed;
      } catch (error) {
        console.error("parseAnalysisContent: Fehler beim Parsen:", error);
        console.error("parseAnalysisContent: Original String:", analysisContent);
        
        try {
          const directParsed = JSON.parse(analysisContent);
          console.log("parseAnalysisContent: Direktes Parsen erfolgreich:", directParsed);
          return directParsed;
        } catch (directError) {
          console.error("parseAnalysisContent: Auch direktes Parsen fehlgeschlagen:", directError);
          return null;
        }
      }
    }
    
    console.log("parseAnalysisContent: Unbekannter Datentyp, gebe null zurück");
    return null;
  };

  const renderModuleDetails = (module: ModuleResult) => {
    const isExpanded = expandedModules.has(module.module_name);
    const rawResult = module.result || {};
    const wcagInfo = rawResult.wcag_info || {};
    const parsedAnalysis = rawResult.parsed_analysis;

    console.log('Render Modul:', module.module_name);
    console.log('Raw Result:', rawResult);
    console.log('Parsed Analysis:', parsedAnalysis);
    console.log('WCAG Info:', wcagInfo);

    const moduleScore = calculateModuleScore(rawResult);
    
    let displayViolations = 0;
    let displayWarnings = 0;
    let displayPassed = false;
    let displaySummary = wcagInfo.description || 'Keine Zusammenfassung oder Analyse vorhanden.';
    let complianceLevel = '';

    if (parsedAnalysis) {
      if (parsedAnalysis.analysis_result) {
        const analysisResult = parsedAnalysis.analysis_result;
        
        displaySummary = analysisResult.summary?.overall_assessment || displaySummary;
        complianceLevel = analysisResult.summary?.compliance_level || '';
        
        if (analysisResult.criteria_evaluation) {
          analysisResult.criteria_evaluation.forEach((criteria: CriteriaEvaluation) => {
            if (criteria.status === "FAILED") {
              displayViolations++;
            } else if (criteria.status === "PARTIAL" || criteria.status === "WARNING") {
              displayWarnings++;
            } else if (criteria.status === "PASSED") {
              displayPassed = true;
            }
          });
        }
        
        displayPassed = analysisResult.summary?.score >= 70 || 
                       complianceLevel === "AA" || 
                       complianceLevel === "AAA" ||
                       displayViolations === 0;
      }
      else if (parsedAnalysis.gesamtbewertung) {
        displayViolations = parsedAnalysis.gesamtbewertung.kritische_probleme || 0;
        displayPassed = parsedAnalysis.gesamtbewertung.status === "GRÜN" || 
                        parsedAnalysis.gesamtbewertung.status === "PASSED" || 
                        (parsedAnalysis.gesamtbewertung.score !== undefined && parsedAnalysis.gesamtbewertung.score >= 90); 
        displaySummary = parsedAnalysis.zusammenfassung || displaySummary;

        if (parsedAnalysis.detailbewertung) {
          parsedAnalysis.detailbewertung.forEach(item => {
            if (item.bewertung === "TEILWEISE") {
              displayWarnings++;
            }
          });
        }
      }
      else if (rawResult.analysis_result || rawResult.gesamtbewertung) {
        console.log('Verwende rawResult direkt für', module.module_name);
        if (rawResult.analysis_result) {
          const analysisResult = rawResult.analysis_result;
          displaySummary = analysisResult.summary?.overall_assessment || displaySummary;
          complianceLevel = analysisResult.summary?.compliance_level || '';
          
          if (analysisResult.criteria_evaluation) {
            analysisResult.criteria_evaluation.forEach((criteria: CriteriaEvaluation) => {
              if (criteria.status === "FAILED") {
                displayViolations++;
              } else if (criteria.status === "PARTIAL" || criteria.status === "WARNING") {
                displayWarnings++;
              } else if (criteria.status === "PASSED") {
                displayPassed = true;
              }
            });
          }
          
          displayPassed = analysisResult.summary?.score >= 70 || 
                         complianceLevel === "AA" || 
                         complianceLevel === "AAA" ||
                         displayViolations === 0;
        }
      }
    } else {
      console.log('Keine parsed_analysis für', module.module_name, '- verwende Fallback');
      displaySummary = `Analyse für ${module.module_name} konnte nicht geladen oder verarbeitet werden.`;
    }

    const status = {
      passed: displayPassed,
      violations: displayViolations,
      warnings: displayWarnings, 
      score: moduleScore,
      complianceLevel: complianceLevel || getComplianceLevel(moduleScore)
    };

    const moduleDisplayTitle = wcagInfo.name || formatModuleName(module.module_name);
    const moduleDisplayDescription = wcagInfo.description || getModuleDescription(module.module_name);

    return (
      <div className="module-details">
        <button
          className="module-header-button"
          onClick={() => toggleModule(module.module_name)}
          aria-expanded={isExpanded}
        >
          <div className="module-header-content">
            <div className="module-info">
              <div className="module-title-row">
                <h4 className="module-title">{moduleDisplayTitle}</h4>
                <div className="module-badges">
                  <div 
                    className="compliance-badge"
                    style={{
                      backgroundColor: getComplianceColor(status.complianceLevel),
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}
                  >
                    {status.complianceLevel}
                  </div>
                  <div className={`module-score ${status.score >= 70 ? 'good' : status.score >= 40 ? 'warning' : 'poor'}`}>
                    {status.score}/100
                  </div>
                </div>
              </div>
              <p className="module-description">{moduleDisplayDescription}</p>
              <div className="module-status-summary">
                <span className="status-description">{getScoreDescription(status.score)}</span>
                <div className="status-indicators">
                  {status.violations > 0 && (
                    <span className="status-indicator error">
                      <XCircle size={16} />
                      {status.violations} Verstöße
                    </span>
                  )}
                  {status.warnings > 0 && (
                    <span className="status-indicator warning">
                      <AlertTriangle size={16} />
                      {status.warnings} Warnungen
                    </span>
                  )}
                  {status.passed && (
                    <span className="status-indicator success">
                      <CheckCircle size={16} />
                      Bestanden
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="module-expand-icon">
              {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
          </div>
        </button>
        
        {isExpanded && parsedAnalysis && (
          <div className="module-expanded-content">
            {parsedAnalysis.analysis_result && (
              <>
                <div className="module-section">
                  <h5 className="section-title">
                    <Info size={16} />
                    Gesamtbewertung
                  </h5>
                  <div className="summary-content">
                    <div className="summary-stats">
                      <div className="stat-item">
                        <span className="stat-label">Score:</span>
                        <span className="stat-value">{parsedAnalysis.analysis_result.summary.score}/100</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Compliance Level:</span>
                        <span className="stat-value">{parsedAnalysis.analysis_result.summary.compliance_level}</span>
                      </div>
                    </div>
                    <p className="section-content">{parsedAnalysis.analysis_result.summary.overall_assessment}</p>
                  </div>
                </div>

                {parsedAnalysis.analysis_result.criteria_evaluation && parsedAnalysis.analysis_result.criteria_evaluation.length > 0 && (
                  <div className="module-section">
                    <h5 className="section-title">
                      <AlertCircle size={16} />
                      Kriterien-Bewertung
                    </h5>
                    <ul className="violations-list">
                      {parsedAnalysis.analysis_result.criteria_evaluation.map((criteria: CriteriaEvaluation, idx: number) => (
                        <li key={idx} className={`violation-item ${criteria.status === 'FAILED' ? 'is-violation' : criteria.status === 'PARTIAL' || criteria.status === 'WARNING' ? 'is-warning' : 'is-ok'}`}>
                          <div className="violation-header">
                            <strong>{criteria.criterion_id} {criteria.name}</strong>
                            <span className={`status-badge ${criteria.status.toLowerCase()}`}>
                              {criteria.status === 'FAILED' ? 'Nicht erfüllt' : 
                               criteria.status === 'PARTIAL' ? 'Teilweise' : 
                               criteria.status === 'WARNING' ? 'Warnung' : 'Erfüllt'}
                            </span>
                          </div>
                          
                          {criteria.finding && (
                            <div className="criteria-section">
                              <strong>Befund:</strong>
                              <p>{criteria.finding}</p>
                            </div>
                          )}
                          
                          {criteria.impact && (
                            <div className="criteria-section">
                              <strong>Auswirkung:</strong>
                              <p>{criteria.impact}</p>
                            </div>
                          )}
                          
                          {criteria.recommendation && (
                            <div className="criteria-section">
                              <strong>Empfehlung:</strong>
                              <p>{criteria.recommendation}</p>
                            </div>
                          )}
                          
                          {criteria.examples && criteria.examples.length > 0 && (
                            <div className="criteria-section">
                              <strong>Beispiele:</strong>
                              <ul className="examples-list">
                                {criteria.examples.map((example, eIdx) => (
                                  <li key={eIdx}>{example}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {parsedAnalysis.analysis_result.priority_actions && (
                  <div className="module-section">
                    <h5 className="section-title">
                      <TrendingUp size={16} />
                      Priorisierte Maßnahmen
                    </h5>
                    {Object.entries(parsedAnalysis.analysis_result.priority_actions).map(([priority, actions]) => (
                      actions && actions.length > 0 && (
                        <div key={priority} className="massnahmen-block">
                          <h6>{priority === 'immediate' ? 'Sofort' : priority === 'short_term' ? 'Kurzfristig' : 'Langfristig'}</h6>
                          <ul>
                            {(actions as PriorityAction[]).map((action: PriorityAction, aIdx: number) => (
                              <li key={aIdx}>
                                <strong>{action.title}</strong> (Aufwand: {action.effort})
                                <p>{action.description}</p>
                                {action.affected_criteria && action.affected_criteria.length > 0 && (
                                  <p><strong>Betroffene Kriterien:</strong> {action.affected_criteria.join(', ')}</p>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )
                    ))}
                  </div>
                )}
              </>
            )}

            {!parsedAnalysis.analysis_result && (
              <>
                {parsedAnalysis.zusammenfassung && (
                  <div className="module-section">
                    <h5 className="section-title">
                      <Info size={16} />
                      Zusammenfassung (Legacy)
                    </h5>
                    <p className="section-content">{parsedAnalysis.zusammenfassung}</p>
                  </div>
                )}
                
                {parsedAnalysis.detailbewertung && parsedAnalysis.detailbewertung.length > 0 && (
                  <div className="module-section">
                    <h5 className="section-title">
                      <AlertCircle size={16} />
                      Detail-Bewertung (Legacy)
                    </h5>
                    <ul className="violations-list">
                      {parsedAnalysis.detailbewertung.map((item: DetailbewertungKriterium, idx: number) => (
                        <li key={idx} className={`violation-item ${item.bewertung === 'NICHT_ERFUELLT' ? 'is-violation' : item.bewertung === 'TEILWEISE' ? 'is-warning' : 'is-ok'}`}>
                          <div className="violation-header">
                            <strong>{item.kriterium_id} {item.kriterium_name}</strong>
                            <span className={`status-badge ${item.bewertung === 'NICHT_ERFUELLT' ? 'failed' : item.bewertung === 'TEILWEISE' ? 'partial' : 'passed'}`}>
                              {item.bewertung === 'NICHT_ERFUELLT' ? 'Nicht erfüllt' : 
                               item.bewertung === 'TEILWEISE' ? 'Teilweise' : 'Erfüllt'}
                            </span>
                          </div>
                          
                          {item.befund && (
                            <div className="criteria-section">
                              <strong>Befund:</strong>
                              <p>{item.befund}</p>
                            </div>
                          )}
                          
                          {item.auswirkung && (
                            <div className="criteria-section">
                              <strong>Auswirkung:</strong>
                              <p>{item.auswirkung}</p>
                            </div>
                          )}
                          
                          {item.empfehlung && (
                            <div className="criteria-section">
                              <strong>Empfehlung:</strong>
                              <p>{item.empfehlung}</p>
                            </div>
                          )}
                          
                          {item.beispiele && item.beispiele.length > 0 && (
                            <div className="criteria-section">
                              <strong>Beispiele:</strong>
                              <ul className="examples-list">
                                {item.beispiele.map((bsp, bIdx) => (
                                  <li key={bIdx}>{bsp}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {parsedAnalysis.priorisierte_massnahmen && (
                  <div className="module-section">
                    <h5 className="section-title">
                      <TrendingUp size={16} />
                      Priorisierte Maßnahmen (Legacy)
                    </h5>
                    {Object.entries(parsedAnalysis.priorisierte_massnahmen).map(([prioritaet, massnahmen]) => (
                      massnahmen && massnahmen.length > 0 && (
                        <div key={prioritaet} className="massnahmen-block">
                          <h6>{prioritaet.charAt(0).toUpperCase() + prioritaet.slice(1)}</h6>
                          <ul>
                            {(massnahmen as Massnahme[]).map((massnahme: Massnahme, mIdx: number) => (
                              <li key={mIdx}>
                                <strong>{massnahme.titel}</strong> (Aufwand: {massnahme.aufwand || 'N/A'})
                                <p>{massnahme.beschreibung}</p>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )
                    ))}
                  </div>
                )}
              </>
            )}

            {!parsedAnalysis.analysis_result && !parsedAnalysis.detailbewertung && !parsedAnalysis.priorisierte_massnahmen && !parsedAnalysis.zusammenfassung && (
              <div className="module-section">
                <h5 className="section-title">
                  <Info size={16} />
                  Keine Analyse-Details
                </h5>
                <p className="section-content">Für dieses Modul wurden keine detaillierten Analyseergebnisse im erwarteten Format gefunden.</p>
              </div>
            )}
          </div>
        )}
        
        {isExpanded && !parsedAnalysis && (
          <div className="module-expanded-content">
            <div className="module-section">
              <h5 className="section-title">
                <Info size={16} />
                Analyse nicht verfügbar
              </h5>
              <p className="section-content">{displaySummary}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
  };

  const createDemoJobs = async () => {
    if (!user?.id) {
      toast.error("Bitte melden Sie sich zuerst an");
      return;
    }

    try {
      const demoJobs = [
        {
          id: crypto.randomUUID(),
          url: 'https://example.com',
          status: 'completed',
          progress: 100,
          plan: 'basic',
          user_id: user.id,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: new Date().toISOString()
        },
        {
          id: crypto.randomUUID(),
          url: 'https://demo-site.de',
          status: 'running',
          progress: 75,
          plan: 'pro',
          user_id: user.id,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: crypto.randomUUID(),
          url: 'https://test-website.com',
          status: 'failed',
          progress: 40,
          plan: 'enterprise',
          user_id: user.id,
          created_at: new Date(Date.now() - 7200000).toISOString(),
          updated_at: new Date().toISOString(),
          error: 'Website nicht erreichbar'
        }
      ];

      console.log("🎭 Erstelle Demo-Jobs für User:", user.id);

      for (const job of demoJobs) {
        const { error } = await supabase
          .from('analysis_jobs')
          .insert(job);

        if (error) {
          console.error("❌ Fehler beim Erstellen des Demo-Jobs:", error);
        } else {
          console.log("✅ Demo-Job erstellt:", job.url);
        }
      }

      toast.success("Demo-Jobs erfolgreich erstellt!");
      
      const { data, error } = await supabase
        .from('analysis_jobs')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      if (!error) {
        setJobs(data || []);
      }

    } catch (error) {
      console.error("❌ Fehler beim Erstellen der Demo-Jobs:", error);
      toast.error("Fehler beim Erstellen der Demo-Jobs");
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-content">
          <Loader2 className="loading-spinner" size={48} />
          <h1 className="loading-title">Jobs werden geladen...</h1>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dashboard-loading">
        <div className="loading-content">
          <AlertCircle className="loading-spinner" size={48} />
          <h1 className="loading-title">Bitte anmelden</h1>
          <p className="loading-subtitle">Sie müssen angemeldet sein, um das Dashboard zu sehen</p>
          <a href="/analyze" className="btn-primary">
            Zur Anmeldung
          </a>
        </div>
      </div>
    );
  }

  return (
    <>
    <div className="dashboard">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Analyse-Dashboard</h1>
          <p className="dashboard-subtitle">
            Übersicht Ihrer Barrierefreiheits-Analysen und Berichte
          </p>
        </div>

        {jobs.length === 0 ? (
          <div className="empty-state">
            <Clock className="empty-icon" size={48} />
            <h3 className="empty-title">Noch keine Analysen</h3>
            <p className="empty-description">
              Starten Sie Ihre erste Website-Analyse
            </p>
              <div className="empty-actions">
            <a href="/analyze" className="btn-primary">
              Erste Analyse starten
            </a>
                <button onClick={createDemoJobs} className="btn-secondary">
                  🎭 Demo-Daten erstellen
                </button>
              </div>
              <div className="debug-info">
                <p style={{color: '#666', fontSize: '0.9rem', marginTop: '1rem'}}>
                  Debug: User ID = {user?.id} | User Email = {user?.email}
                </p>
              </div>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map((job) => (
              <div
                key={job.id}
                className={`job-card ${highlightJobId === job.id ? 'highlighted' : ''}`}
              >
                <div className="job-header">
                  <div className="job-info">
                    <h3 className="job-url">{job.url}</h3>
                    <p className="job-date">
                      Erstellt {formatDistanceToNow(new Date(job.created_at), { 
                        addSuffix: true, 
                        locale: de 
                      })}
                    </p>
                  </div>
                  <div className="job-badges">
                    {getPlanBadge(job.plan)}
                    {getStatusBadge(job.status)}
                  </div>
                </div>

                {job.error && (
                  <div className="error-message">
                    <AlertCircle size={16} />
                    <p>{job.error}</p>
                  </div>
                )}

                <div className="job-actions">
                  <div className="job-id">
                    Job ID: {job.id.slice(0, 8)}...
                  </div>
                  <div className="action-buttons">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary small"
                    >
                      <ExternalLink size={14} />
                      Website
                    </a>
                    
                    {job.status === "running" && (
                      <a
                        href={`/analyze/progress/${job.id}`}
                        className="btn-primary small"
                      >
                        <Loader2 size={14} />
                        Fortschritt
                      </a>
                    )}
                    
                    {job.status === "completed" && (
                      <>
                        <button
                          onClick={() => handleViewResults(job.id)}
                          disabled={isLoadingResults}
                          className="btn-primary small"
                        >
                          {isLoadingResults ? (
                            <Loader2 className="animate-spin" size={14} />
                          ) : (
                            <Eye size={14} />
                          )}
                          Ergebnisse
                        </button>
                        <button
                          onClick={(event) => handleDownloadPDF(job.id, event)}
                          className="btn-secondary small"
                        >
                          <Download size={14} />
                          PDF
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {selectedJobId && selectedJobDetails && (
          <div className="modal-overlay">
            <div className="modal premium-modal">
              <div className="modal-header premium">
                <div className="modal-header-info">
                  <h2 className="modal-title">Detaillierte Analyse-Ergebnisse</h2>
                  <p className="modal-subtitle">{selectedJobDetails.url}</p>
                  <div className="modal-meta">
                    <span className="meta-item">
                      <Clock size={14} />
                      Analysiert am {new Date(selectedJobDetails.created_at).toLocaleDateString('de-DE')}
                    </span>
                    <span className="meta-item">
                      {getPlanBadge(selectedJobDetails.plan)}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectedJobId(null);
                    setSelectedJobDetails(null);
                    setSelectedJobModules([]);
                    setSelectedJobReport(null);
                  }}
                  className="modal-close"
                >
                  <X size={20} />
                </button>
              </div>
              
              <div className="modal-content premium">
                <div className="overall-score-section">
                  <div className="score-card">
                    <h3 className="score-title">Gesamt-Bewertung</h3>
                    <div className="score-display">
                      <div className="score-circle">
                        <svg className="score-ring" viewBox="0 0 120 120">
                          <defs>
                            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" style={{stopColor: getComplianceColor(getComplianceLevel(overallStats.overallScore)), stopOpacity: 1}} />
                              <stop offset="100%" style={{stopColor: getComplianceColor(getComplianceLevel(overallStats.overallScore)), stopOpacity: 0.8}} />
                            </linearGradient>
                          </defs>
                          <circle
                            className="score-ring-bg"
                            cx="60"
                            cy="60"
                            r="54"
                            fill="none"
                          />
                          <circle
                            className="score-ring-progress"
                            cx="60"
                            cy="60"
                            r="54"
                            fill="none"
                            strokeDasharray={`${2 * Math.PI * 54}`}
                            strokeDashoffset={`${2 * Math.PI * 54 * (1 - overallStats.overallScore / 100)}`}
                          />
                        </svg>
                        <div className="score-text">
                          <span className="score-number">{overallStats.overallScore}</span>
                          <span className="score-label">Punkte</span>
                        </div>
                      </div>
                      
                      <div className="score-details">
                        <div className="score-item">
                          <div 
                            className="compliance-badge"
                            style={{
                              backgroundColor: getComplianceColor(getComplianceLevel(overallStats.overallScore)),
                              color: 'white',
                              padding: '4px 12px',
                              borderRadius: '6px',
                              fontWeight: 'bold',
                              fontSize: '14px'
                            }}
                          >
                            {getComplianceLevel(overallStats.overallScore)} Konformität
                          </div>
                        </div>
                        <div className="score-item">
                          <span style={{fontSize: '16px', fontWeight: '600', color: '#374151'}}>
                            {getScoreDescription(overallStats.overallScore)}
                          </span>
                        </div>
                        <div className="score-item">
                          <CheckCircle2 className="score-icon success" size={20} />
                          <span>{overallStats.passedCriteria} Kriterien bestanden</span>
                        </div>
                        <div className="score-item">
                          <Warning className="score-icon warning" size={20} />
                          <span>{overallStats.totalWarnings} Warnungen</span>
                        </div>
                        <div className="score-item">
                          <XCircle className="score-icon error" size={20} />
                          <span>{overallStats.totalViolations} Verstöße</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {selectedJobModules.length > 0 ? (
                  <div className="modules-analysis-section">
                    <h3 className="section-header">
                      <BarChart3 size={24} />
                      Detaillierte Analyse nach WCAG-Kriterien
                    </h3>
                    <div className="modules-list premium">
                      {selectedJobModules.map((module) => (
                        <div key={module.id} className="module-container">
                          {renderModuleDetails(module)}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="no-results">
                    <AlertTriangle size={48} />
                    <h3>Keine detaillierten Ergebnisse verfügbar</h3>
                    <p>Die Analyse-Ergebnisse werden noch verarbeitet oder sind nicht verfügbar.</p>
                  </div>
                )}

                <div className="export-actions">
                  <button 
                    onClick={() => handleDownloadPDF(selectedJobId)}
                    className="btn-primary export"
                  >
                    <Download size={18} />
                    Vollständigen Bericht als PDF exportieren
                  </button>
                  <button className="btn-secondary export">
                    <FileText size={18} />
                    Executive Summary herunterladen
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>

      <Footer />
    </>
  );
}

export default function DashboardPage() {
  return (
    <RoleGuard>
      <Suspense fallback={
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <div>Dashboard wird geladen...</div>
        </div>
      }>
        <DashboardContent />
      </Suspense>
    </RoleGuard>
  );
} 