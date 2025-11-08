import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Plus, Building } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const Warehouses = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [bins, setBins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [warehouseDialogOpen, setWarehouseDialogOpen] = useState(false);
  const [binDialogOpen, setBinDialogOpen] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [warehouseForm, setWarehouseForm] = useState({ code: "", name: "", location: "" });
  const [binForm, setBinForm] = useState({ warehouse_id: "", code: "", name: "" });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [warehousesRes, binsRes] = await Promise.all([
        axios.get(`${API}/warehouses`, { withCredentials: true }),
        axios.get(`${API}/bins`, { withCredentials: true })
      ]);
      setWarehouses(warehousesRes.data);
      setBins(binsRes.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load data");
      setLoading(false);
    }
  };

  const handleWarehouseSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/warehouses`, warehouseForm, { withCredentials: true });
      toast.success("Warehouse created successfully");
      setWarehouseDialogOpen(false);
      setWarehouseForm({ code: "", name: "", location: "" });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create warehouse");
    }
  };

  const handleBinSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/bins`, binForm, { withCredentials: true });
      toast.success("Bin created successfully");
      setBinDialogOpen(false);
      setBinForm({ warehouse_id: "", code: "", name: "" });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create bin");
    }
  };

  const getBinsForWarehouse = (warehouseId) => {
    return bins.filter(bin => bin.warehouse_id === warehouseId);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="warehouses-title">Warehouses & Bins</h1>
          <p className="text-slate-600 mt-1">Manage storage locations</p>
        </div>
        <div className="flex gap-3">
          <Dialog open={warehouseDialogOpen} onOpenChange={setWarehouseDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="add-warehouse-btn" className="bg-blue-600 hover:bg-blue-700">
                <Plus size={20} className="mr-2" />
                Add Warehouse
              </Button>
            </DialogTrigger>
            <DialogContent data-testid="warehouse-dialog" aria-describedby="warehouse-dialog-description">
              <DialogHeader>
                <DialogTitle>Create New Warehouse</DialogTitle>
              </DialogHeader>
              <p id="warehouse-dialog-description" className="sr-only">Form to create a new warehouse with code, name and location</p>
              <form onSubmit={handleWarehouseSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="wh-code">Warehouse Code</Label>
                  <Input
                    id="wh-code"
                    data-testid="warehouse-code-input"
                    value={warehouseForm.code}
                    onChange={(e) => setWarehouseForm({...warehouseForm, code: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="wh-name">Warehouse Name</Label>
                  <Input
                    id="wh-name"
                    data-testid="warehouse-name-input"
                    value={warehouseForm.name}
                    onChange={(e) => setWarehouseForm({...warehouseForm, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="wh-location">Location</Label>
                  <Input
                    id="wh-location"
                    data-testid="warehouse-location-input"
                    value={warehouseForm.location}
                    onChange={(e) => setWarehouseForm({...warehouseForm, location: e.target.value})}
                  />
                </div>
                <Button type="submit" className="w-full" data-testid="submit-warehouse-btn">Create Warehouse</Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={binDialogOpen} onOpenChange={setBinDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="add-bin-btn" variant="outline">
                <Plus size={20} className="mr-2" />
                Add Bin
              </Button>
            </DialogTrigger>
            <DialogContent data-testid="bin-dialog" aria-describedby="bin-dialog-description">
              <DialogHeader>
                <DialogTitle>Create New Bin</DialogTitle>
              </DialogHeader>
              <p id="bin-dialog-description" className="sr-only">Form to create a new bin linked to a warehouse</p>
              <form onSubmit={handleBinSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="bin-warehouse">Warehouse</Label>
                  <select
                    id="bin-warehouse"
                    data-testid="bin-warehouse-select"
                    value={binForm.warehouse_id}
                    onChange={(e) => setBinForm({...binForm, warehouse_id: e.target.value})}
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
                  <Label htmlFor="bin-code">Bin Code</Label>
                  <Input
                    id="bin-code"
                    data-testid="bin-code-input"
                    value={binForm.code}
                    onChange={(e) => setBinForm({...binForm, code: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="bin-name">Bin Name</Label>
                  <Input
                    id="bin-name"
                    data-testid="bin-name-input"
                    value={binForm.name}
                    onChange={(e) => setBinForm({...binForm, name: e.target.value})}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" data-testid="submit-bin-btn">Create Bin</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Warehouses List */}
      {loading ? (
        <div className="p-8 text-center text-slate-600">Loading...</div>
      ) : warehouses.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8 text-center text-slate-500">
          No warehouses found. Create one to get started.
        </div>
      ) : (
        <div className="space-y-4">
          {warehouses.map((warehouse, index) => (
            <div key={warehouse.id} className="bg-white rounded-lg shadow-sm border border-slate-200 p-6" data-testid={`warehouse-card-${index}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <Building className="text-blue-600" size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800">{warehouse.name}</h3>
                    <p className="text-sm text-slate-500">Code: {warehouse.code}</p>
                    {warehouse.location && (
                      <p className="text-sm text-slate-600 mt-1">{warehouse.location}</p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Bins */}
              <div className="mt-4 pt-4 border-t border-slate-200">
                <h4 className="text-sm font-medium text-slate-700 mb-3">Bins ({getBinsForWarehouse(warehouse.id).length})</h4>
                {getBinsForWarehouse(warehouse.id).length === 0 ? (
                  <p className="text-sm text-slate-500">No bins in this warehouse</p>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {getBinsForWarehouse(warehouse.id).map((bin, binIndex) => (
                      <div key={bin.id} className="bg-slate-50 rounded p-3" data-testid={`bin-card-${index}-${binIndex}`}>
                        <p className="text-sm font-medium text-slate-800">{bin.name}</p>
                        <p className="text-xs text-slate-500">{bin.code}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Warehouses;
