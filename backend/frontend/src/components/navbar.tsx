"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { LogOut, User, LayoutDashboard, AlertTriangle, Gavel, Clock, Euro, Code, Shield } from "lucide-react";
import { toast } from "sonner";
import AuthModal from "./auth-modal";

const newsItems = [
  {
    icon: AlertTriangle,
    text: "BFSG: Ab Juni 2025 sind alle Online-Shops zur Barrierefreiheit verpflichtet",
    color: "text-red-600"
  },
  {
    icon: Euro,
    text: "Bußgelder bis zu 100.000€ bei Verstößen gegen das Barrierefreiheitsstärkungsgesetz",
    color: "text-orange-600"
  },
  {
    icon: Gavel,
    text: "Neue EU-Richtlinie: Barrierefreiheit wird zum Wettbewerbsvorteil",
    color: "text-blue-600"
  },
  {
    icon: Clock,
    text: "Nur noch 6 Monate bis zur BFSG-Deadline - Jetzt handeln!",
    color: "text-red-600"
  },
  {
    icon: AlertTriangle,
    text: "15% der Bevölkerung sind auf barrierefreie Websites angewiesen",
    color: "text-green-600"
  }
];

export default function Navbar() {
  const { user, signOut, userRole, loading } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [currentNewsIndex, setCurrentNewsIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Auto-rotate news items
  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentNewsIndex((prev) => (prev + 1) % newsItems.length);
        setIsAnimating(false);
      }, 300);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const handleSignOut = async () => {
    try {
      await signOut();
      setShowUserMenu(false);
    } catch (error) {
      toast.error("Fehler beim Abmelden");
    }
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
  };

  const getRoleDisplay = () => {
    switch (userRole) {
      case 'admin':
        return { name: 'Administrator', color: 'text-red-600' };
      case 'developer':
        return { name: 'Entwickler', color: 'text-blue-600' };
      case 'certifier':
        return { name: 'Zertifizierer', color: 'text-green-600' };
      default:
        return { name: 'Kunde', color: 'text-gray-600' };
    }
  };

  const roleInfo = getRoleDisplay();
  const currentNews = newsItems[currentNewsIndex];
  const CurrentIcon = currentNews.icon;

  return (
    <>
    <nav className="navbar">
      <div className="nav-container-full">
        <a href="/" className="logo">
          <img 
            src="/logo.svg" 
            alt="BarrierefreiCheck Logo" 
            className="logo-svg"
          />
        </a>
        
          {/* News Ticker */}
          <div className="news-ticker">
            <div className={`news-item ${isAnimating ? 'fade-out' : 'fade-in'}`}>
              <CurrentIcon size={16} className={`news-icon ${currentNews.color}`} />
              <span className="news-text">{currentNews.text}</span>
            </div>
          </div>
          
          <div className="nav-links">
          {user ? (
            <div className="user-menu">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="user-button flex items-center justify-center p-2 hover:bg-gray-100 rounded-full"
              >
                <User size={24} />
              </button>
              
              {showUserMenu && (
                <div className="user-dropdown">
                  {/* Dashboard Links - für Admins alle Dashboards zeigen */}
                  {userRole === 'admin' ? (
                    <>
                      <a href="/dashboard" className="dashboard-link">
                        <LayoutDashboard size={16} />
                        Kunden Dashboard
                      </a>
                      <a href="/dashboard/developer" className="dashboard-link">
                        <Code size={16} />
                        Entwickler Dashboard
                      </a>
                      <a href="/dashboard/certifier" className="dashboard-link">
                        <Shield size={16} />
                        Zertifizierer Dashboard
                      </a>
                    </>
                  ) : userRole === 'developer' ? (
                    <a href="/dashboard/developer" className="dashboard-link">
                      <Code size={16} />
                      Entwickler Dashboard
                    </a>
                  ) : userRole === 'certifier' ? (
                    <a href="/dashboard/certifier" className="dashboard-link">
                      <Shield size={16} />
                      Zertifizierer Dashboard
                    </a>
                  ) : (
                    <a href="/dashboard" className="dashboard-link">
                      <LayoutDashboard size={16} />
                      Dashboard
                    </a>
                  )}
                  
                  <div className="dropdown-divider"></div>
                  
                  <div className="user-info">
                    <p className="user-name">
                      {user.user_metadata?.first_name || user.email?.split('@')[0] || 'User'}
                    </p>
                    <p className="user-email">{user.email}</p>
                    {userRole && (
                      <p className={`user-role ${roleInfo.color}`}>
                        {roleInfo.name}
                      </p>
                    )}
                    {/* Debug Info */}
                    <p style={{ fontSize: '10px', color: '#888', marginTop: '4px' }}>
                      ID: {user.id?.slice(0, 8)}... | Role: {userRole || 'loading...'}
                    </p>
                  </div>
                  
                  <button onClick={handleSignOut} className="sign-out-button">
                    <LogOut size={16} />
                    Abmelden
                  </button>
                </div>
              )}
            </div>
          ) : (
              <button onClick={() => setShowAuthModal(true)} className="btn-primary">
                Anmelden
              </button>
          )}
        </div>
      </div>
    </nav>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
        mode="signin"
      />

      <style jsx>{`
        .user-dropdown {
          min-width: 250px;
        }

        .dashboard-link {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          color: #374151;
          text-decoration: none;
          transition: all 0.2s;
          font-weight: 500;
        }

        .dashboard-link:hover {
          background-color: #f3f4f6;
          color: #1f2937;
        }

        .dropdown-divider {
          height: 1px;
          background-color: #e5e7eb;
          margin: 0.5rem 0;
        }

        .user-info {
          padding: 1rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .user-name {
          font-weight: 600;
          color: #1f2937;
          margin: 0 0 0.25rem 0;
        }

        .user-email {
          color: #6b7280;
          font-size: 0.875rem;
          margin: 0;
        }

        .user-role {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-top: 0.25rem;
        }
      `}</style>
    </>
  );
} 