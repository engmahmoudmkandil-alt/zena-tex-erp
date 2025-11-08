import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const StockMoves = () => {
  const [moves, setMoves] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [bins, setBins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    product_id: "",
    move_type: "receipt",
    from_warehouse_id: "",
    from_bin_id: "",
    to_warehouse_id: "",
    to_bin_id: "",
    quantity: "",
    reference: "",
    notes: ""
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [movesRes, productsRes, warehousesRes, binsRes] = await Promise.all([
        axios.get(`${API}/stock-moves`),
        axios.get(`${API}/products`),
        axios.get(`${API}/warehouses`),
        axios.get(`${API}/bins`)
      ]);
      setMoves(movesRes.data);
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
        quantity: parseFloat(formData.quantity),
        from_warehouse_id: formData.from_warehouse_id || null,
        from_bin_id: formData.from_bin_id || null,
        to_warehouse_id: formData.to_warehouse_id || null,
        to_bin_id: formData.to_bin_id || null,
        reference: formData.reference || null,
        notes: formData.notes || null
      };
      
      await axios.post(`${API}/stock-moves`, payload);
      toast.success("Stock move created successfully");
      setDialogOpen(false);
      setFormData({
        product_id: "",
        move_type: "receipt",
        from_warehouse_id: "",
        from_bin_id: "",
        to_warehouse_id: "",
        to_bin_id: "",
        quantity: "",
        reference: "",
        notes: ""
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create stock move");
    }
  };

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId);
    return product ? product.name : 'Unknown';
  };

  const getWarehouseName = (warehouseId) => {
    if (!warehouseId) return '-';
    const warehouse = warehouses.find(w => w.id === warehouseId);
    return warehouse ? warehouse.name : 'Unknown';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="stock-moves-title">Stock Moves</h1>
          <p className="text-slate-600 mt-1">Track all inventory transactions</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-stock-move-btn" className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              Create Stock Move
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="stock-move-dialog" aria-describedby="stock-move-dialog-description">
            <DialogHeader>
              <DialogTitle>Create Stock Move</DialogTitle>
            </DialogHeader>
            <p id="stock-move-dialog-description" className="sr-only">Form to create stock movements including receipts, issues, and transfers</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="product">Product</Label>
                  <select
                    id="product"
                    data-testid="move-product-select"
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

                <div className="col-span-2">
                  <Label htmlFor="move_type">Move Type</Label>
                  <select
                    id="move_type"
                    data-testid="move-type-select"
                    value={formData.move_type}
                    onChange={(e) => setFormData({...formData, move_type: e.target.value})}
                    className="w-full border border-slate-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="receipt">Receipt (Incoming)</option>
                    <option value="issue">Issue (Outgoing)</option>
                    <option value="transfer">Transfer (Between locations)</option>
                  </select>
                </div>

                {(formData.move_type === 'issue' || formData.move_type === 'transfer') && (
                  <>
                    <div>
                      <Label htmlFor="from_warehouse">From Warehouse</Label>
                      <select
                        id="from_warehouse"
                        data-testid="from-warehouse-select"
                        value={formData.from_warehouse_id}
                        onChange={(e) => setFormData({...formData, from_warehouse_id: e.target.value})}
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
                      <Label htmlFor="from_bin">From Bin (Optional)</Label>
                      <select
                        id="from_bin"
                        data-testid="from-bin-select"
                        value={formData.from_bin_id}
                        onChange={(e) => setFormData({...formData, from_bin_id: e.target.value})}
                        className="w-full border border-slate-300 rounded-md px-3 py-2"
                      >
                        <option value="">No specific bin</option>
                        {bins.filter(b => b.warehouse_id === formData.from_warehouse_id).map(bin => (
                          <option key={bin.id} value={bin.id}>{bin.name}</option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                {(formData.move_type === 'receipt' || formData.move_type === 'transfer') && (
                  <>
                    <div>
                      <Label htmlFor="to_warehouse">To Warehouse</Label>
                      <select
                        id="to_warehouse"
                        data-testid="to-warehouse-select"
                        value={formData.to_warehouse_id}
                        onChange={(e) => setFormData({...formData, to_warehouse_id: e.target.value})}
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
                      <Label htmlFor="to_bin">To Bin (Optional)</Label>
                      <select
                        id="to_bin"
                        data-testid="to-bin-select"
                        value={formData.to_bin_id}
                        onChange={(e) => setFormData({...formData, to_bin_id: e.target.value})}
                        className="w-full border border-slate-300 rounded-md px-3 py-2"
                      >
                        <option value="">No specific bin</option>
                        {bins.filter(b => b.warehouse_id === formData.to_warehouse_id).map(bin => (
                          <option key={bin.id} value={bin.id}>{bin.name}</option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                <div>
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    data-testid="move-quantity-input"
                    type="number"
                    step="0.01"
                    value={formData.quantity}
                    onChange={(e) => setFormData({...formData, quantity: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="reference">Reference</Label>
                  <Input
                    id="reference"
                    data-testid="move-reference-input"
                    value={formData.reference}
                    onChange={(e) => setFormData({...formData, reference: e.target.value})}
                    placeholder="PO#, SO#, etc."
                  />
                </div>

                <div className="col-span-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Input
                    id="notes"
                    data-testid="move-notes-input"
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" data-testid="submit-move-btn">Create Stock Move</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stock Moves Table */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading stock moves...</div>
        ) : moves.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No stock moves recorded yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Type</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Product</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">From</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">To</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Quantity</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Reference</th>
                </tr>
              </thead>
              <tbody>
                {moves.map((move, index) => (
                  <tr key={move.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`move-row-${index}`}>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {new Date(move.created_at).toLocaleDateString()}
                    </td>
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
                    <td className="py-3 px-4 text-sm text-slate-900 font-medium">
                      {getProductName(move.product_id)}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {getWarehouseName(move.from_warehouse_id)}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {getWarehouseName(move.to_warehouse_id)}
                    </td>
                    <td className="py-3 px-4 text-sm font-semibold text-slate-900 text-right">
                      {move.quantity}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {move.reference || '-'}
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

export default StockMoves;
