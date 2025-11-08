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

const WorkCenters = () => {
  const { t } = useTranslation();
  const [workCenters, setWorkCenters] = useState([]);
  const [filteredWorkCenters, setFilteredWorkCenters] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    code: "",
    name: "",
    description: "",
    capacity: "1.0",
    efficiency: "100",
    cost_per_hour: "0",
    is_active: true
  });

  useEffect(() => {
    loadWorkCenters();
  }, []);

  useEffect(() => {
    const filtered = workCenters.filter(wc => 
      wc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      wc.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredWorkCenters(filtered);
  }, [searchTerm, workCenters]);

  const loadWorkCenters = async () => {
    try {
      const response = await axios.get(`${API}/work-centers`, { withCredentials: true });
      setWorkCenters(response.data);
      setFilteredWorkCenters(response.data);
      setLoading(false);
    } catch (error) {
      toast.error(t('error_load'));
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/work-centers`, {
        ...formData,
        capacity: parseFloat(formData.capacity),
        efficiency: parseFloat(formData.efficiency),
        cost_per_hour: parseFloat(formData.cost_per_hour)
      }, { withCredentials: true });
      toast.success(t('success_created'));
      setDialogOpen(false);
      setFormData({ code: "", name: "", description: "", capacity: "1.0", efficiency: "100", cost_per_hour: "0", is_active: true });
      loadWorkCenters();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('error_create'));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid="work-centers-title">{t('work_centers_title')}</h1>
          <p className="text-slate-600 mt-1">{t('work_centers_subtitle')}</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-work-center-btn" className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              {t('add_work_center')}
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="work-center-dialog" aria-describedby="wc-dialog-description">
            <DialogHeader>
              <DialogTitle>{t('create_new_work_center')}</DialogTitle>
            </DialogHeader>
            <p id="wc-dialog-description" className="sr-only">Form to create a new work center</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="code">{t('work_center_code')}</Label>
                <Input id="code" data-testid="wc-code-input" value={formData.code} onChange={(e) => setFormData({...formData, code: e.target.value})} required />
              </div>
              <div>
                <Label htmlFor="name">{t('work_center_name')}</Label>
                <Input id="name" data-testid="wc-name-input" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div>
                <Label htmlFor="description">{t('description')}</Label>
                <Input id="description" data-testid="wc-description-input" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="capacity">{t('capacity')}</Label>
                  <Input id="capacity" type="number" step="0.01" data-testid="wc-capacity-input" value={formData.capacity} onChange={(e) => setFormData({...formData, capacity: e.target.value})} required />
                </div>
                <div>
                  <Label htmlFor="efficiency">{t('efficiency')} (%)</Label>
                  <Input id="efficiency" type="number" step="0.1" data-testid="wc-efficiency-input" value={formData.efficiency} onChange={(e) => setFormData({...formData, efficiency: e.target.value})} required />
                </div>
                <div>
                  <Label htmlFor="cost">{t('cost_per_hour')}</Label>
                  <Input id="cost" type="number" step="0.01" data-testid="wc-cost-input" value={formData.cost_per_hour} onChange={(e) => setFormData({...formData, cost_per_hour: e.target.value})} required />
                </div>
              </div>
              <Button type="submit" className="w-full" data-testid="submit-wc-btn">{t('create')}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <Input data-testid="search-wc-input" placeholder={t('search')} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">{t('loading')}</div>
        ) : filteredWorkCenters.length === 0 ? (
          <div className="p-8 text-center text-slate-500">{t('no_data_found')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('work_center_code')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('work_center_name')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('capacity')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('efficiency')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('cost_per_hour')}</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">{t('status')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredWorkCenters.map((wc, index) => (
                  <tr key={wc.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`wc-row-${index}`}>
                    <td className="py-3 px-4 text-sm font-medium text-slate-900">{wc.code}</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{wc.name}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{wc.capacity}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{wc.efficiency}%</td>
                    <td className="py-3 px-4 text-sm text-slate-600">${wc.cost_per_hour}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${wc.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                        {wc.is_active ? t('active') : t('inactive')}
                      </span>
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

export default WorkCenters;