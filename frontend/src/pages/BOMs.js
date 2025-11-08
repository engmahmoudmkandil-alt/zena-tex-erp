import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const BOMs = () => {
  const { t } = useTranslation();
  const [boms, setBoms] = useState([]);
  const [products, setProducts] = useState([]);
  const [filteredBoms, setFilteredBoms] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    product_id: "",
    version: "1.0",
    components: [],
    is_active: true
  });
  const [componentForm, setComponentForm] = useState({
    product_id: "",
    quantity: "",
    unit: "pcs"
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const filtered = boms.filter(bom => 
      bom.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredBoms(filtered);
  }, [searchTerm, boms]);

  const loadData = async () => {
    try {
      const [bomsRes, productsRes] = await Promise.all([
        axios.get(`${API}/boms`, { withCredentials: true }),
        axios.get(`${API}/products`, { withCredentials: true })
      ]);
      setBoms(bomsRes.data);
      setProducts(productsRes.data);
      setFilteredBoms(bomsRes.data);
      setLoading(false);
    } catch (error) {
      toast.error(t('error_load'));
      setLoading(false);
    }
  };

  const addComponent = () => {
    if (!componentForm.product_id || !componentForm.quantity) {
      toast.error("Please fill all component fields");
      return;
    }
    setFormData({
      ...formData,
      components: [...formData.components, {
        product_id: componentForm.product_id,
        quantity: parseFloat(componentForm.quantity),
        unit: componentForm.unit
      }]
    });
    setComponentForm({ product_id: "", quantity: "", unit: "pcs" });
  };

  const removeComponent = (index) => {
    const newComponents = formData.components.filter((_, i) => i !== index);
    setFormData({ ...formData, components: newComponents });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/boms`, formData, { withCredentials: true });
      toast.success(t('success_created'));
      setDialogOpen(false);
      setFormData({ name: "", product_id: "", version: "1.0", components: [], is_active: true });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('error_create'));
    }
  };

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId);
    return product ? product.name : '-';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="boms-title">{t('boms_title')}</h1>
          <p className="text-slate-600 mt-1">{t('boms_subtitle')}</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-bom-btn" className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              {t('add_bom')}
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="bom-dialog" aria-describedby="bom-dialog-description">
            <DialogHeader>
              <DialogTitle>{t('create_new_bom')}</DialogTitle>
            </DialogHeader>
            <p id="bom-dialog-description" className="sr-only">Form to create a new bill of materials</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="bom-name">{t('bom_name')}</Label>
                <Input
                  id="bom-name"
                  data-testid="bom-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="finished-product">{t('finished_product')}</Label>
                <select
                  id="finished-product"
                  data-testid="bom-product-select"
                  value={formData.product_id}
                  onChange={(e) => setFormData({...formData, product_id: e.target.value})}
                  className="w-full border border-slate-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">{t('select_product')}</option>
                  {products.map(product => (
                    <option key={product.id} value={product.id}>{product.name} ({product.code})</option>
                  ))}
                </select>
              </div>
              <div>
                <Label htmlFor="version">{t('version')}</Label>
                <Input
                  id="version"
                  data-testid="bom-version-input"
                  value={formData.version}
                  onChange={(e) => setFormData({...formData, version: e.target.value})}
                  required
                />
              </div>
              
              <div className="border-t pt-4">
                <Label className="text-lg font-semibold">{t('components')}</Label>
                <div className="grid grid-cols-3 gap-2 mt-2">
                  <select
                    data-testid="component-product-select"
                    value={componentForm.product_id}
                    onChange={(e) => setComponentForm({...componentForm, product_id: e.target.value})}
                    className="border border-slate-300 rounded-md px-3 py-2"
                  >
                    <option value="">{t('select_product')}</option>
                    {products.map(product => (
                      <option key={product.id} value={product.id}>{product.name}</option>
                    ))}
                  </select>
                  <Input
                    type="number"
                    step="0.01"
                    data-testid="component-quantity-input"
                    placeholder={t('quantity_required')}
                    value={componentForm.quantity}
                    onChange={(e) => setComponentForm({...componentForm, quantity: e.target.value})}
                  />
                  <Button type="button" onClick={addComponent} data-testid="add-component-btn">
                    {t('add_component')}
                  </Button>
                </div>
                
                {formData.components.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {formData.components.map((comp, index) => (
                      <div key={index} className="flex items-center justify-between bg-slate-50 p-2 rounded" data-testid={`component-${index}`}>
                        <span>{getProductName(comp.product_id)} - {comp.quantity} {comp.unit}</span>
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          onClick={() => removeComponent(index)}
                          data-testid={`remove-component-${index}`}
                        >
                          {t('delete')}
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <Button type="submit" className="w-full" data-testid="submit-bom-btn">{t('create')}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <Input
            data-testid="search-boms-input"
            placeholder={t('search')})
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">{t('loading')}</div>
        ) : filteredBoms.length === 0 ? (
          <div className="p-8 text-center text-slate-500">{t('no_data_found')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('bom_name')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('finished_product')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('version')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('components')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('status')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('created')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredBoms.map((bom, index) => (
                  <tr key={bom.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`bom-row-${index}`}>
                    <td className="py-3 px-4 text-sm font-medium text-slate-900">{bom.name}</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{getProductName(bom.product_id)}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{bom.version}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{bom.components.length}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${
                        bom.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {bom.is_active ? t('active') : t('inactive')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {new Date(bom.created_at).toLocaleDateString()}
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

export default BOMs;