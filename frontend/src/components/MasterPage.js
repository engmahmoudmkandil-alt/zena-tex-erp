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

const MasterPage = ({ 
  endpoint, 
  titleKey, 
  subtitleKey, 
  addButtonKey, 
  createTitleKey, 
  fields, 
  columns, 
  searchFields 
}) => {
  const { t } = useTranslation();
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  
  const initialFormData = fields.reduce((acc, field) => {
    acc[field.name] = field.type === "number" ? "0" : "";
    return acc;
  }, { is_active: true });
  
  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (searchFields && searchFields.length > 0) {
      const filtered = data.filter(item => 
        searchFields.some(field => 
          item[field]?.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
      setFilteredData(filtered);
    } else {
      setFilteredData(data);
    }
  }, [searchTerm, data]);

  const loadData = async () => {
    try {
      const response = await axios.get(`${API}/${endpoint}`, { withCredentials: true });
      setData(response.data);
      setFilteredData(response.data);
      setLoading(false);
    } catch (error) {
      toast.error(t('error_load'));
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...formData };
      fields.forEach(field => {
        if (field.type === "number" && payload[field.name]) {
          payload[field.name] = parseFloat(payload[field.name]);
        }
      });
      
      await axios.post(`${API}/${endpoint}`, payload, { withCredentials: true });
      toast.success(t('success_created'));
      setDialogOpen(false);
      setFormData(initialFormData);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || t('error_create'));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800" data-testid={`${endpoint}-title`}>{t(titleKey)}</h1>
          <p className="text-slate-600 mt-1">{t(subtitleKey)}</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid={`add-${endpoint}-btn`} className="bg-blue-600 hover:bg-blue-700">
              <Plus size={20} className="mr-2" />
              {t(addButtonKey)}
            </Button>
          </DialogTrigger>
          <DialogContent data-testid={`${endpoint}-dialog`} aria-describedby={`${endpoint}-dialog-description`}>
            <DialogHeader>
              <DialogTitle>{t(createTitleKey)}</DialogTitle>
            </DialogHeader>
            <p id={`${endpoint}-dialog-description`} className="sr-only">Form to create a new {endpoint}</p>
            <form onSubmit={handleSubmit} className="space-y-4">
              {fields.map(field => (
                <div key={field.name}>
                  <Label htmlFor={field.name}>{t(field.label)}</Label>
                  <Input
                    id={field.name}
                    type={field.type}
                    step={field.step}
                    min={field.min}
                    max={field.max}
                    data-testid={`${field.name}-input`}
                    value={formData[field.name]}
                    onChange={(e) => setFormData({...formData, [field.name]: e.target.value})}
                    required={field.required}
                  />
                </div>
              ))}
              <Button type="submit" className="w-full" data-testid={`submit-${endpoint}-btn`}>{t('create')}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <Input
            data-testid={`search-${endpoint}-input`}
            placeholder={t('search')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">{t('loading')}</div>
        ) : filteredData.length === 0 ? (
          <div className="p-8 text-center text-slate-500">{t('no_data_found')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  {columns.map(col => (
                    <th key={col.key} className="text-left py-3 px-4 text-sm font-semibold text-slate-700">
                      {t(col.label)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredData.map((item, index) => (
                  <tr key={item.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`${endpoint}-row-${index}`}>
                    {columns.map(col => (
                      <td key={col.key} className="py-3 px-4 text-sm text-slate-700">
                        {col.isBadge ? (
                          <span className={`inline-block px-2 py-1 text-xs rounded ${
                            item[col.key] ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {item[col.key] ? t('active') : t('inactive')}
                          </span>
                        ) : col.isDate ? (
                          item[col.key] ? new Date(item[col.key]).toLocaleDateString() : '-'
                        ) : col.isNumber ? (
                          item[col.key]?.toFixed(2) || '0.00'
                        ) : (
                          item[col.key] || '-'
                        )}
                      </td>
                    ))}
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

export default MasterPage;
