import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { FileText, Filter } from "lucide-react";

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    resource_type: "",
    user_id: ""
  });

  const resourceTypes = ["", "product", "warehouse", "bin", "stock_move", "adjustment", "user"];

  useEffect(() => {
    loadLogs();
  }, [filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.resource_type) params.append('resource_type', filters.resource_type);
      if (filters.user_id) params.append('user_id', filters.user_id);
      
      const response = await axios.get(`${API}/audit-logs?${params.toString()}`, {
        withCredentials: true
      });
      setLogs(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load audit logs");
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'create': return 'bg-green-100 text-green-700';
      case 'update': return 'bg-blue-100 text-blue-700';
      case 'delete': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-600';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800" data-testid="audit-logs-title">
          Audit Logs
        </h1>
        <p className="text-slate-600 mt-1">Track all system activities and changes</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="flex items-center gap-4">
          <Filter className="text-slate-400" size={20} />
          <div className="flex-1">
            <label className="text-sm text-slate-600 mb-1 block">Filter by Resource Type</label>
            <select
              data-testid="filter-resource-type"
              value={filters.resource_type}
              onChange={(e) => setFilters({...filters, resource_type: e.target.value})}
              className="border border-slate-300 rounded-md px-3 py-2"
            >
              <option value="">All Types</option>
              {resourceTypes.filter(t => t).map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading audit logs...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No audit logs found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Timestamp</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">User</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Action</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Resource Type</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Resource ID</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`audit-log-${index}`}>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700">
                      <div>
                        <div className="font-medium">{log.user_email}</div>
                        <div className="text-xs text-slate-500">{log.user_id.substring(0, 8)}...</div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-700">{log.resource_type}</td>
                    <td className="py-3 px-4 text-sm text-slate-600 font-mono">
                      {log.resource_id.substring(0, 8)}...
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">
                      {log.before_data && (
                        <div className="text-xs">
                          <span className="text-slate-500">Before: </span>
                          <span className="text-red-600">{JSON.stringify(log.before_data).substring(0, 50)}...</span>
                        </div>
                      )}
                      {log.after_data && (
                        <div className="text-xs">
                          <span className="text-slate-500">After: </span>
                          <span className="text-green-600">{JSON.stringify(log.after_data).substring(0, 50)}...</span>
                        </div>
                      )}
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

export default AuditLogs;
