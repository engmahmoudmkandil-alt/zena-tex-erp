import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const Adjustments = () => {
  const [adjustments, setAdjustments] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [bins, setBins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    product_id: "",
    warehouse_id: "",
    bin_id: "",
    quantity_change: "",
    reason: ""
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [adjustmentsRes, productsRes, warehousesRes, binsRes] = await Promise.all([
        axios.get(`${API}/adjustments`, { withCredentials: true }),
        axios.get(`${API}/products`, { withCredentials: true }),
        axios.get(`${API}/warehouses`, { withCredentials: true }),
        axios.get(`${API}/bins`, { withCredentials: true })
      ]);
      setAdjustments(adjustmentsRes.data);
      setProducts(productsRes.data);
      setWarehouses(warehousesRes.data);
      setBins(binsRes.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load data");
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        quantity_change: parseFloat(formData.quantity_change),
        bin_id: formData.bin_id || null
      };
      
      await axios.post(`${API}/adjustments`, payload, { withCredentials: true });
      toast.success("Inventory adjusted successfully");
      setDialogOpen(false);
      setFormData({
        product_id: "",
        warehouse_id: "",
        bin_id: "",
        quantity_change: "",
        reason: ""
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create adjustment");
    }
  };

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId);
    return product ? product.name : 'Unknown';
  };

  const getWarehouseName = (warehouseId) => {
    const warehouse = warehouses.find(w => w.id === warehouseId);
    return warehouse ? warehouse.name : 'Unknown';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="adjustments-title">Inventory Adjustments</h1>
          <p className="text-slate-600 mt-1">Record inventory corrections and adjustments</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-adjustment-btn" className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              Create Adjustment
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="adjustment-dialog" aria-describedby="adjustment-dialog-description">
            <DialogHeader>
              <DialogTitle>Create Inventory Adjustment</DialogTitle>
            </DialogHeader>
            <p id="adjustment-dialog-description" className="sr-only">Form to create inventory adjustments for stock corrections</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="product">Product</Label>
                <select
                  id="product"
                  data-testid="adjustment-product-select"
                  value={formData.product_id}
                  onChange={(e) => setFormData({...formData, product_id: e.target.value})}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select Product</option>
                  {products.map(product => (
                    <option key={product.id} value={product.id}>{product.name} ({product.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="warehouse">Warehouse</Label>
                <select
                  id="warehouse"
                  data-testid="adjustment-warehouse-select"
                  value={formData.warehouse_id}
                  onChange={(e) => setFormData({...formData, warehouse_id: e.target.value})}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select Warehouse</option>
                  {warehouses.map(wh => (
                    <option key={wh.id} value={wh.id}>{wh.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="bin">Bin (Optional)</Label>
                <select
                  id="bin"
                  data-testid="adjustment-bin-select"
                  value={formData.bin_id}
                  onChange={(e) => setFormData({...formData, bin_id: e.target.value})}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                >
                  <option value="">No specific bin</option>
                  {bins.filter(b => b.warehouse_id === formData.warehouse_id).map(bin => (
                    <option key={bin.id} value={bin.id}>{bin.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="quantity_change">Quantity Change</Label>
                <Input
                  id="quantity_change"
                  data-testid="adjustment-quantity-input"
                  type="number"
                  step="0.01"
                  value={formData.quantity_change}
                  onChange={(e) => setFormData({...formData, quantity_change: e.target.value})}
                  placeholder="Use negative for decrease"
                  required
                />
                <p className="text-xs text-slate-500 mt-1">Use positive numbers to add stock, negative to remove</p>
              </div>

              <div>
                <Label htmlFor="reason">Reason</Label>
                <Input
                  id="reason"
                  data-testid="adjustment-reason-input"
                  value={formData.reason}
                  onChange={(e) => setFormData({...formData, reason: e.target.value})}
                  placeholder="e.g., Physical count correction, Damage, etc."
                  required
                />
              </div>

              <Button type="submit" className="w-full" data-testid="submit-adjustment-btn">Create Adjustment</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Adjustments Table */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading adjustments...</div>
        ) : adjustments.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No adjustments recorded yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Product</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Warehouse</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Change</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Reason</th>
                </tr>
              </thead>
              <tbody>
                {adjustments.map((adjustment, index) => (
                  <tr key={adjustment.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`adjustment-row-${index}`}>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {new Date(adjustment.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-900 font-medium">
                      {getProductName(adjustment.product_id)}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {getWarehouseName(adjustment.warehouse_id)}
                    </td>
                    <td className="py-3 px-4 text-sm font-semibold text-right">
                      <span className={adjustment.quantity_change >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {adjustment.quantity_change >= 0 ? '+' : ''}{adjustment.quantity_change}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {adjustment.reason}
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

export default Adjustments;
