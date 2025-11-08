import { useState, useEffect, createContext, useContext } from "react";
import { useTranslation } from "react-i18next";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { Package, Warehouse, TrendingUp, History, Settings, Menu, X, LogOut, Users, FileText, Layers, Factory, UserCog, Truck, UserSquare2 } from "lucide-react";
import Dashboard from "@/pages/Dashboard";
import Products from "@/pages/Products";
import Warehouses from "@/pages/Warehouses";
import Inventory from "@/pages/Inventory";
import StockMoves from "@/pages/StockMoves";
import Adjustments from "@/pages/Adjustments";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import UserManagement from "@/pages/UserManagement";
import AuditLogs from "@/pages/AuditLogs";
import BOMs from "@/pages/BOMs";
import WorkCenters from "@/pages/WorkCenters";
import Employees from "@/pages/Employees";
import Suppliers from "@/pages/Suppliers";
import Customers from "@/pages/Customers";
import LanguageSwitcher from "@/components/LanguageSwitcher";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    const hash = window.location.hash;
    if (hash && hash.includes("session_id=")) {
      const sessionId = hash.split("session_id=")[1].split("&")[0];
      
      try {
        const response = await axios.get(`${API}/auth/session`, {
          headers: { "X-Session-ID": sessionId }
        });
        
        // Store session token in cookie (backend handles this)
        setUser(response.data.user);
        
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
        
        toast.success("Logged in successfully");
        navigate("/");
      } catch (error) {
        console.error("OAuth error:", error);
        toast.error("Authentication failed");
      }
    }
  };

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true
      });
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password }, {
      withCredentials: true
    });
    
    if (response.data.requires_otp) {
      return response.data;
    }
    
    setUser(response.data.user);
    return response.data;
  };

  const verifyOTP = async (userId, otpCode) => {
    const response = await axios.post(
      `${API}/auth/verify-otp?user_id=${userId}&otp_code=${otpCode}`,
      {},
      { withCredentials: true }
    );
    setUser(response.data.user);
    return response.data;
  };

  const register = async (data) => {
    await axios.post(`${API}/auth/register`, data);
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {
      console.error("Logout error:", error);
    }
    setUser(null);
    navigate("/login");
  };

  const loginWithGoogle = () => {
    const redirectUrl = `${window.location.origin}/`;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, loginWithGoogle, verifyOTP, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-slate-600">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    toast.error("You don't have permission to access this page");
    return <Navigate to="/" />;
  }

  return children;
};

const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const menuItems = [
    { path: "/", label: "Dashboard", icon: TrendingUp, roles: [] },
    { path: "/products", label: "Products", icon: Package, roles: [] },
    { path: "/warehouses", label: "Warehouses", icon: Warehouse, roles: [] },
    { path: "/inventory", label: "Inventory", icon: Settings, roles: [] },
    { path: "/stock-moves", label: "Stock Moves", icon: History, roles: [] },
    { path: "/adjustments", label: "Adjustments", icon: Settings, roles: [] },
    { path: "/users", label: "User Management", icon: Users, roles: ["Admin"] },
    { path: "/audit-logs", label: "Audit Logs", icon: FileText, roles: ["Admin", "Accountant", "CEO/Viewer"] },
  ];

  const filteredMenuItems = menuItems.filter(item => {
    if (item.roles.length === 0) return true;
    return item.roles.includes(user?.role);
  });

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      <div className={`
        fixed top-0 left-0 h-full bg-slate-900 text-white z-50 transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
        w-64 flex flex-col
      `}>
        <div className="p-6 flex-1">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-xl font-bold" data-testid="app-title">InventoryPro</h1>
            <button 
              className="lg:hidden"
              onClick={() => setIsOpen(false)}
              data-testid="close-sidebar-btn"
            >
              <X size={24} />
            </button>
          </div>
          
          {user && (
            <div className="mb-6 pb-6 border-b border-slate-700">
              <div className="flex items-center space-x-3">
                {user.picture ? (
                  <img src={user.picture} alt={user.name} className="w-10 h-10 rounded-full" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {user.name.charAt(0)}
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium">{user.name}</p>
                  <p className="text-xs text-slate-400">{user.role}</p>
                </div>
              </div>
            </div>
          )}
          
          <nav className="space-y-2">
            {filteredMenuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase().replace(/ /g, '-')}`}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-blue-600 text-white' 
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }
                  `}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6 border-t border-slate-700">
          <button
            onClick={logout}
            data-testid="logout-btn"
            className="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-slate-300 hover:bg-slate-800 hover:text-white w-full"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </>
  );
};

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <button 
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
            data-testid="open-sidebar-btn"
          >
            <Menu size={24} />
          </button>
        </div>
        
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout><Dashboard /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute>
                <Layout><Products /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/warehouses" element={
              <ProtectedRoute>
                <Layout><Warehouses /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/inventory" element={
              <ProtectedRoute>
                <Layout><Inventory /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/stock-moves" element={
              <ProtectedRoute>
                <Layout><StockMoves /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/adjustments" element={
              <ProtectedRoute>
                <Layout><Adjustments /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/users" element={
              <ProtectedRoute allowedRoles={["Admin"]}>
                <Layout><UserManagement /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/audit-logs" element={
              <ProtectedRoute allowedRoles={["Admin", "Accountant", "CEO/Viewer"]}>
                <Layout><AuditLogs /></Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
