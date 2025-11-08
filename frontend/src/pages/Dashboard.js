import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { Package, Warehouse, TrendingUp, AlertTriangle } from "lucide-react";

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalWarehouses: 0,
    totalStockValue: 0,
    lowStockItems: 0
  });
  const [recentMoves, setRecentMoves] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [products, warehouses, inventory, moves] = await Promise.all([
        axios.get(`${API}/products`, { withCredentials: true }),
        axios.get(`${API}/warehouses`, { withCredentials: true }),
        axios.get(`${API}/inventory`, { withCredentials: true }),
        axios.get(`${API}/stock-moves`, { withCredentials: true })
      ]);

      setStats({
        totalProducts: products.data.length,
        totalWarehouses: warehouses.data.length,
        totalStockValue: inventory.data.reduce((sum, item) => sum + item.quantity, 0),
        lowStockItems: inventory.data.filter(item => item.quantity < 10).length
      });

      setRecentMoves(moves.data.slice(0, 5));
      setLoading(false);
    } catch (error) {
      console.error("Error loading dashboard:", error);
      setLoading(false);
    }
  };

  const statCards = [
    { label: "Total Products", value: stats.totalProducts, icon: Package, color: "bg-blue-500" },
    { label: "Warehouses", value: stats.totalWarehouses, icon: Warehouse, color: "bg-green-500" },
    { label: "Total Stock Units", value: stats.totalStockValue, icon: TrendingUp, color: "bg-purple-500" },
    { label: "Low Stock Items", value: stats.lowStockItems, icon: AlertTriangle, color: "bg-orange-500" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-lg text-slate-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800" data-testid="dashboard-title">Dashboard</h1>
        <p className="text-slate-600 mt-1">Overview of your inventory system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div 
              key={index}
              className="bg-white rounded-lg shadow-sm border border-slate-200 p-6"
              data-testid={`stat-card-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">{stat.label}</p>
                  <p className="text-3xl font-bold text-slate-800 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon size={24} className="text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Stock Moves */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4" data-testid="recent-moves-title">Recent Stock Moves</h2>
        {recentMoves.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No recent stock moves</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Type</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Product ID</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-slate-600">Quantity</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Date</th>
                </tr>
              </thead>
              <tbody>
                {recentMoves.map((move, index) => (
                  <tr key={move.id} className="border-b border-slate-100" data-testid={`recent-move-${index}`}>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${
                        move.move_type === 'receipt' ? 'bg-green-100 text-green-700' :
                        move.move_type === 'issue' ? 'bg-red-100 text-red-700' :
                        move.move_type === 'transfer' ? 'bg-blue-100 text-blue-700' :
                        'bg-purple-100 text-purple-700'
                      }`}>
                        {move.move_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700">{move.product_id.substring(0, 8)}...</td>
                    <td className="py-3 px-4 text-sm text-slate-700 text-right">{move.quantity}</td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {new Date(move.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
