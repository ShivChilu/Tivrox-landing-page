import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LogOut, Download, Trash2, RefreshCw, Filter,
  Inbox, Clock, MessageCircle, CheckCircle2, Users,
  ArrowLeft, Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const statusColors = {
  "New": "bg-blue-50 text-blue-700 border-blue-200",
  "Contacted": "bg-amber-50 text-amber-700 border-amber-200",
  "In Progress": "bg-purple-50 text-purple-700 border-purple-200",
  "Completed": "bg-emerald-50 text-emerald-700 border-emerald-200"
};

const statusIcons = {
  "New": Inbox,
  "Contacted": MessageCircle,
  "In Progress": Clock,
  "Completed": CheckCircle2
};

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [serviceFilter, setServiceFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const token = localStorage.getItem("tivrox_admin_token");
  const adminUser = localStorage.getItem("tivrox_admin_user") || "Admin";

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    if (!token) { navigate("/admin"); return; }
    setLoading(true);
    try {
      const params = {};
      if (serviceFilter !== "all") params.service = serviceFilter;
      if (statusFilter !== "all") params.status = statusFilter;

      const [bookingsRes, statsRes] = await Promise.all([
        axios.get(`${API}/admin/bookings`, { headers: authHeaders, params }),
        axios.get(`${API}/admin/stats`, { headers: authHeaders })
      ]);
      setBookings(bookingsRes.data.bookings);
      setStats(statsRes.data);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("tivrox_admin_token");
        localStorage.removeItem("tivrox_admin_user");
        navigate("/admin");
        toast.error("Session expired. Please login again.");
      } else {
        toast.error("Failed to load data");
      }
    } finally {
      setLoading(false);
    }
  }, [token, serviceFilter, statusFilter, navigate]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const updateStatus = async (bookingId, newStatus) => {
    try {
      await axios.put(`${API}/admin/bookings/${bookingId}/status`, { status: newStatus }, { headers: authHeaders });
      toast.success(`Status updated to ${newStatus}`);
      fetchData();
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const deleteBooking = async (bookingId) => {
    if (!window.confirm("Are you sure you want to delete this booking?")) return;
    try {
      await axios.delete(`${API}/admin/bookings/${bookingId}`, { headers: authHeaders });
      toast.success("Booking deleted");
      fetchData();
    } catch (err) {
      toast.error("Failed to delete booking");
    }
  };

  const exportCSV = async () => {
    try {
      const res = await axios.get(`${API}/admin/bookings/export`, {
        headers: authHeaders,
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `tivrox_bookings_${new Date().toISOString().split("T")[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("CSV exported successfully");
    } catch (err) {
      toast.error("Failed to export CSV");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("tivrox_admin_token");
    localStorage.removeItem("tivrox_admin_user");
    navigate("/admin");
  };

  const statCards = stats ? [
    { label: "Total Requests", value: stats.total, icon: Users, color: "bg-blue-50 text-blue-600" },
    { label: "New", value: stats.new, icon: Inbox, color: "bg-blue-50 text-blue-600" },
    { label: "Contacted", value: stats.contacted, icon: MessageCircle, color: "bg-amber-50 text-amber-600" },
    { label: "In Progress", value: stats.in_progress, icon: Clock, color: "bg-purple-50 text-purple-600" },
    { label: "Completed", value: stats.completed, icon: CheckCircle2, color: "bg-emerald-50 text-emerald-600" },
  ] : [];

  return (
    <div className="min-h-screen bg-slate-50" data-testid="admin-dashboard">
      {/* Top bar */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate("/")}
              data-testid="dashboard-back-btn"
              className="text-slate-400 hover:text-blue-600 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                TIVROX Admin
              </h1>
              <p className="text-xs text-slate-500">Welcome, {adminUser}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              data-testid="refresh-btn"
              variant="outline"
              size="sm"
              onClick={fetchData}
              className="border-slate-200 text-slate-600"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              data-testid="export-csv-btn"
              variant="outline"
              size="sm"
              onClick={exportCSV}
              className="border-slate-200 text-slate-600"
            >
              <Download className="h-4 w-4 mr-1" />
              Export CSV
            </Button>
            <Button
              data-testid="logout-btn"
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="border-red-200 text-red-600 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4 mr-1" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 py-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            {statCards.map((s) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                data-testid={`stat-card-${s.label.toLowerCase().replace(/\s/g, '-')}`}
                className="bg-white rounded-xl border border-slate-200 p-4"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${s.color}`}>
                    <s.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                    <p className="text-xs text-slate-500">{s.label}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6 items-center">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-600">Filters:</span>
          </div>
          <Select value={serviceFilter} onValueChange={setServiceFilter}>
            <SelectTrigger data-testid="filter-service" className="w-48 h-9 rounded-lg border-slate-200 text-sm">
              <SelectValue placeholder="All Services" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Services</SelectItem>
              <SelectItem value="Web Development">Web Development</SelectItem>
              <SelectItem value="App Development">App Development</SelectItem>
              <SelectItem value="Video Editing">Video Editing</SelectItem>
              <SelectItem value="Logo & Poster Design">Logo & Poster Design</SelectItem>
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger data-testid="filter-status" className="w-40 h-9 rounded-lg border-slate-200 text-sm">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="New">New</SelectItem>
              <SelectItem value="Contacted">Contacted</SelectItem>
              <SelectItem value="In Progress">In Progress</SelectItem>
              <SelectItem value="Completed">Completed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20" data-testid="loading-indicator">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : bookings.length === 0 ? (
            <div className="text-center py-20" data-testid="empty-state">
              <Inbox className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500 font-medium">No bookings found</p>
              <p className="text-sm text-slate-400 mt-1">Requests will appear here when clients submit the form</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50">
                    <TableHead className="font-semibold text-slate-600">Name</TableHead>
                    <TableHead className="font-semibold text-slate-600">Email</TableHead>
                    <TableHead className="font-semibold text-slate-600">Phone</TableHead>
                    <TableHead className="font-semibold text-slate-600">Service</TableHead>
                    <TableHead className="font-semibold text-slate-600">Status</TableHead>
                    <TableHead className="font-semibold text-slate-600">Date</TableHead>
                    <TableHead className="font-semibold text-slate-600 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {bookings.map((b) => (
                    <TableRow key={b.id} data-testid={`booking-row-${b.id}`} className="group">
                      <TableCell className="font-medium text-slate-900">{b.full_name}</TableCell>
                      <TableCell className="text-slate-600 text-sm">{b.email}</TableCell>
                      <TableCell className="text-slate-600 text-sm">{b.phone}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="text-xs font-medium bg-slate-100 text-slate-700">
                          {b.service}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={b.status}
                          onValueChange={(val) => updateStatus(b.id, val)}
                        >
                          <SelectTrigger
                            data-testid={`status-select-${b.id}`}
                            className={`w-32 h-8 rounded-lg text-xs font-medium border ${statusColors[b.status] || ''}`}
                          >
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="New">New</SelectItem>
                            <SelectItem value="Contacted">Contacted</SelectItem>
                            <SelectItem value="In Progress">In Progress</SelectItem>
                            <SelectItem value="Completed">Completed</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell className="text-slate-500 text-sm">
                        {new Date(b.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          data-testid={`delete-btn-${b.id}`}
                          variant="ghost"
                          size="icon"
                          onClick={() => deleteBooking(b.id)}
                          className="h-8 w-8 text-slate-400 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
