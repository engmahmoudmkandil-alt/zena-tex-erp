import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { Package, Warehouse, TrendingUp, History, Settings, Menu, X } from "lucide-react";
import Dashboard from "@/pages/Dashboard";
import Products from "@/pages/Products";
import Warehouses from "@/pages/Warehouses";
import Inventory from "@/pages/Inventory";
import StockMoves from "@/pages/StockMoves";
import Adjustments from "@/pages/Adjustments";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  
  const menuItems = [
    { path: "/", label: "Dashboard", icon: TrendingUp },
    { path: "/products", label: "Products", icon: Package },
    { path: "/warehouses", label: "Warehouses", icon: Warehouse },
    { path: "/inventory", label: "Inventory", icon: Settings },
    { path: "/stock-moves", label: "Stock Moves", icon: History },
    { path: "/adjustments", label: "Adjustments", icon: Settings },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full bg-slate-900 text-white z-50 transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
        w-64
      `}>
        <div className="p-6">
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
          <nav className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
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
        {/* Top bar */}
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <button 
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
            data-testid="open-sidebar-btn"
          >
            <Menu size={24} />
          </button>
        </div>
        
        {/* Main content */}
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
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/warehouses" element={<Warehouses />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/stock-moves" element={<StockMoves />} />
            <Route path="/adjustments" element={<Adjustments />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </div>
  );
}

export default App;
