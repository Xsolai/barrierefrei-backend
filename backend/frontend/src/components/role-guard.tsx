"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2, Shield, AlertTriangle } from "lucide-react";

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles?: string[]; // Optional - wenn nicht gesetzt, nur Login-Check
  redirectTo?: string;
  fallback?: React.ReactNode;
}

export function RoleGuard({ 
  children, 
  allowedRoles,
  redirectTo = "/", 
}: RoleGuardProps) {
  const { user, userRole, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      // Not logged in - redirect to home
      router.push(redirectTo);
      return;
    }

    // Rollen-Check nur wenn allowedRoles definiert ist
    if (!loading && user && allowedRoles && userRole && !allowedRoles.includes(userRole)) {
      // Logged in but wrong role
      router.push("/dashboard");
      return;
    }
  }, [user, userRole, loading, router, redirectTo, allowedRoles]);

  // Loading state
  if (loading) {
    return (
      <div className="role-guard-loading">
        <div className="loading-content">
          <Loader2 className="loading-spinner" size={48} />
          <h1 className="loading-title">Lade...</h1>
          <p className="loading-subtitle">Bitte warten Sie einen Moment</p>
        </div>
        <style jsx>{`
          .role-guard-loading {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
          }
          
          .loading-content {
            text-align: center;
            color: #6b7280;
          }
          
          .loading-spinner {
            margin: 0 auto 1rem;
            animation: spin 1s linear infinite;
            color: #3b82f6;
          }
          
          .loading-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
          }
          
          .loading-subtitle {
            color: #6b7280;
          }
          
          @keyframes spin {
            from {
              transform: rotate(0deg);
            }
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>
      </div>
    );
  }

  // Not logged in
  if (!user) {
    return null; // Redirect happens in useEffect
  }

  // Wrong role (nur wenn allowedRoles definiert ist)
  if (allowedRoles && userRole && !allowedRoles.includes(userRole)) {
    return (
      <div className="role-guard-denied">
        <div className="denied-content">
          <AlertTriangle className="denied-icon" size={64} />
          <h1 className="denied-title">Zugriff verweigert</h1>
          <p className="denied-subtitle">
            Sie benötigen die Rolle <strong>{allowedRoles.join(' oder ')}</strong> um auf diese Seite zuzugreifen.
          </p>
          <p className="denied-current-role">
            Ihre aktuelle Rolle: <strong>{userRole}</strong>
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="btn-primary"
          >
            <Shield size={16} />
            Zum Dashboard
          </button>
        </div>
        <style jsx>{`
          .role-guard-denied {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            padding: 2rem;
          }
          
          .denied-content {
            text-align: center;
            max-width: 500px;
          }
          
          .denied-icon {
            margin: 0 auto 1.5rem;
            color: #ef4444;
          }
          
          .denied-title {
            font-size: 2rem;
            font-weight: 700;
            color: #dc2626;
            margin-bottom: 1rem;
          }
          
          .denied-subtitle {
            color: #7f1d1d;
            margin-bottom: 1rem;
            font-size: 1.1rem;
          }
          
          .denied-current-role {
            color: #991b1b;
            margin-bottom: 2rem;
            font-style: italic;
          }
          
          .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            text-decoration: none;
          }
          
          .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          }
        `}</style>
      </div>
    );
  }

  // User is logged in and has correct role (or no role check needed)
  return <>{children}</>;
} 