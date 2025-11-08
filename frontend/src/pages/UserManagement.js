import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import { Users } from "lucide-react";
import { Button } from "@/components/ui/button";

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const roles = [
    "Admin",
    "Production Manager",
    "Inventory Officer",
    "HR Officer",
    "Accountant",
    "CEO/Viewer"
  ];

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`, {
        withCredentials: true
      });
      setUsers(response.data);
      setLoading(false);
    } catch (error) {
      toast.error("Failed to load users");
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await axios.patch(
        `${API}/users/${userId}/role?role=${encodeURIComponent(newRole)}`,
        {},
        { withCredentials: true }
      );
      toast.success("Role updated successfully");
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update role");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-800" data-testid="users-title">
          User Management
        </h1>
        <p className="text-slate-600 mt-1">Manage user roles and permissions</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-8 text-center text-slate-600">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No users found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Email</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Phone</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Role</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">2FA</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Created</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <tr key={user.id} className="border-b border-slate-100 hover:bg-slate-50" data-testid={`user-row-${index}`}>
                    <td className="py-3 px-4 text-sm font-medium text-slate-900">{user.name}</td>
                    <td className="py-3 px-4 text-sm text-slate-700">{user.email}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{user.phone || "-"}</td>
                    <td className="py-3 px-4">
                      <select
                        value={user.role}
                        onChange={(e) => handleRoleChange(user.id, e.target.value)}
                        className="text-sm border border-slate-300 rounded px-2 py-1"
                        data-testid={`role-select-${index}`}
                      >
                        {roles.map(role => (
                          <option key={role} value={role}>{role}</option>
                        ))}
                      </select>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${
                        user.otp_enabled ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {user.otp_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-1 text-xs rounded ${
                        user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-500">
                      {new Date(user.created_at).toLocaleDateString()}
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

export default UserManagement;
