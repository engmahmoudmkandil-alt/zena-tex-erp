import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Filter, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

const Inventory = () => {
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ product_id: "", warehouse_id: "" });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadInventory();
  }, [filters]);

  const loadData = async () => {
    try {
      const [productsRes, warehousesRes] = await Promise.all([
        axios.get(`${API}/products`, { withCredentials: true }),
        axios.get(`${API}/warehouses`, { withCredentials: true })
      ]);
      setProducts(productsRes.data);
      setWarehouses(warehousesRes.data);
    } catch (error) {
      toast.error("Failed to load data");
    }
  };

  const loadInventory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.product_id) params.append('product_id', filters.product_id);
      if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
      
      const response = await axios.get(`${API}/inventory?${params.toString()}`);
      setInventory(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load inventory");
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadInventory();
    toast.success("Inventory refreshed");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="inventory-title">Inventory</h1>
          <p className="text-slate-600 mt-1">Current stock levels across all locations</p>
        </div>
        <Button onClick={handleRefresh} variant="outline" data-testid="refresh-inventory-btn">
          <RefreshCw size={20} className="mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="flex items-center gap-4">
          <Filter className="text-slate-400" size={20} />
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-600 mb-1 block">Filter by Product</label>
              <select
                data-testid="filter-product-select"
                value={filters.product_id}
                onChange={(e) => setFilters({...filters, product_id: e.target.value})}
                className="w-full border border-slate-300 rounded-md px-3 py-2"
              >
                <option value="">All Products</option>
                {products.map(product => (
                  <option key={product.id} value={product.id}>{product.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-slate-600 mb-1 block">Filter by Warehouse</label>
              <select
                data-testid="filter-warehouse-select"
                value={filters.warehouse_id}
                onChange={(e) => setFilters({...filters, warehouse_id: e.target.value})}
                className="w-full border border-slate-300 rounded-md px-3 py-2"
              >
                <option value="">All Warehouses</option>
                {warehouses.map(warehouse => (
                  <option key={warehouse.id} value={warehouse.id}>{warehouse.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading inventory...</div>
        ) : inventory.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No inventory records found. Create some stock moves to populate inventory.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Product</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Code</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Warehouse</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Bin</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Quantity</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Unit</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item, index) => (
                  <tr 
                    key={item.id} 
                    className={`border-b border-slate-100 hover:bg-slate-50 ${
                      item.quantity < 10 ? 'bg-orange-50' : ''
                    }`}
                    data-testid={`inventory-row-${index}`}
                  >
                    <td className="py-3 px-4 text-sm font-medium text-slate-900">
                      {item.product?.name || 'Unknown'}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {item.product?.code || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700">
                      {item.warehouse?.name || 'Unknown'}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {item.bin?.name || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm font-semibold text-right">
                      <span className={item.quantity < 10 ? 'text-orange-600' : 'text-slate-900'}>
                        {item.quantity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {item.product?.unit || 'pcs'}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {new Date(item.last_updated).toLocaleDateString()}
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

export default Inventory;
