import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const Products = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    code: "",
    name: "",
    description: "",
    unit: "pcs"
  });

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    const filtered = products.filter(product => 
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredProducts(filtered);
  }, [searchTerm, products]);

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`, { withCredentials: true });
      setProducts(response.data);
      setFilteredProducts(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load products");
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/products`, formData, { withCredentials: true });
      toast.success("Product created successfully");
      setDialogOpen(false);
      setFormData({ code: "", name: "", description: "", unit: "pcs" });
      loadProducts();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create product");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="products-title">Products</h1>
          <p className="text-slate-600 mt-1">Manage your product catalog</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-product-btn" className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              Add Product
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="product-dialog" aria-describedby="product-dialog-description">
            <DialogHeader>
              <DialogTitle>Create New Product</DialogTitle>
            </DialogHeader>
            <p id="product-dialog-description" className="sr-only">Form to create a new product with code, name, description and unit</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="code">Product Code</Label>
                <Input
                  id="code"
                  data-testid="product-code-input"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="name">Product Name</Label>
                <Input
                  id="name"
                  data-testid="product-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  data-testid="product-description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="unit">Unit of Measure</Label>
                <Input
                  id="unit"
                  data-testid="product-unit-input"
                  value={formData.unit}
                  onChange={(e) => setFormData({...formData, unit: e.target.value})}
                  required
                />
              </div>
              <Button type="submit" className="w-full" data-testid="submit-product-btn">Create Product</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <Input
            data-testid="search-products-input"
            placeholder="Search products by name or code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading products...</div>
        ) : filteredProducts.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No products found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Code</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Description</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Unit</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Created</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product, index) => (
                  <tr key={product.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`product-row-${index}`}>
                    <td className="py-3 px-4 text-sm font-medium text-slate-900">{product.code}</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{product.name}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{product.description || "-"}</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{product.unit}</td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {new Date(product.created_at).toLocaleDateString()}
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

export default Products;
