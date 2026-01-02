"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";
import { Plus, Trash2, Mail, AlertCircle, Check, Loader2 } from "lucide-react";

interface EmailRoute {
    id: string;
    transaction_type: string;
    email_addresses: string[];
    is_active: boolean;
}

const TRANSACTION_TYPES = [
    { code: "850", name: "Purchase Order" },
    { code: "810", name: "Invoice" },
    { code: "812", name: "Credit/Debit" },
    { code: "856", name: "ASN" },
    { code: "855", name: "PO Ack" },
    { code: "997", name: "Func Ack" },
];

export default function EmailRoutesSettings() {
    const { user } = useAuth();
    const [routes, setRoutes] = useState<EmailRoute[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // New route form
    const [newType, setNewType] = useState("850");
    const [newEmails, setNewEmails] = useState("");
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        fetchRoutes();
    }, [user?.id]);

    const fetchRoutes = async () => {
        if (!user?.id) {
            setLoading(false);
            return;
        }

        try {
            const { data, error } = await supabase
                .from("email_routes")
                .select("*")
                .eq("user_id", user.id)
                .order("transaction_type");

            if (error) {
                console.error("Error fetching email routes:", error);
                setError("Failed to load email routes");
            } else {
                setRoutes(data || []);
            }
        } catch (err) {
            console.error("Failed to fetch email routes:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddRoute = async () => {
        if (!user?.id || !newEmails.trim()) return;

        // Parse emails (comma or newline separated)
        const emails = newEmails
            .split(/[,\n]/)
            .map(e => e.trim())
            .filter(e => e && e.includes("@"));

        if (emails.length === 0) {
            setError("Please enter at least one valid email address");
            return;
        }

        // Check if route for this type already exists
        const existingRoute = routes.find(r => r.transaction_type === newType);
        if (existingRoute) {
            setError(`A route for ${newType} already exists. Delete it first or edit it.`);
            return;
        }

        setSaving(true);
        setError(null);

        try {
            const { data, error } = await supabase
                .from("email_routes")
                .insert({
                    user_id: user.id,
                    transaction_type: newType,
                    email_addresses: emails,
                    is_active: true,
                })
                .select()
                .single();

            if (error) {
                console.error("Error adding route:", error);
                setError("Failed to add email route");
            } else {
                setRoutes([...routes, data]);
                setNewEmails("");
                setShowForm(false);
                setSuccess("Email route added successfully!");
                setTimeout(() => setSuccess(null), 3000);
            }
        } catch (err) {
            console.error("Failed to add route:", err);
            setError("Failed to add email route");
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteRoute = async (id: string) => {
        if (!confirm("Are you sure you want to delete this email route?")) return;

        try {
            const { error } = await supabase
                .from("email_routes")
                .delete()
                .eq("id", id);

            if (error) {
                console.error("Error deleting route:", error);
                setError("Failed to delete email route");
            } else {
                setRoutes(routes.filter(r => r.id !== id));
                setSuccess("Email route deleted");
                setTimeout(() => setSuccess(null), 3000);
            }
        } catch (err) {
            console.error("Failed to delete route:", err);
        }
    };

    const handleToggleRoute = async (route: EmailRoute) => {
        try {
            const { error } = await supabase
                .from("email_routes")
                .update({ is_active: !route.is_active })
                .eq("id", route.id);

            if (error) {
                console.error("Error toggling route:", error);
            } else {
                setRoutes(routes.map(r =>
                    r.id === route.id ? { ...r, is_active: !r.is_active } : r
                ));
            }
        } catch (err) {
            console.error("Failed to toggle route:", err);
        }
    };

    const getTypeName = (code: string) => {
        const type = TRANSACTION_TYPES.find(t => t.code === code);
        return type ? `${type.code} - ${type.name}` : code;
    };

    if (loading) {
        return (
            <div className="p-6 text-center text-slate-500">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                Loading email routes...
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <Mail className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-800">Email Routing</h2>
                            <p className="text-sm text-slate-500">Auto-send converted documents to recipients</p>
                        </div>
                    </div>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                        <Plus className="w-4 h-4" />
                        Add Rule
                    </button>
                </div>
            </div>

            {/* Alerts */}
            {error && (
                <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                    <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">×</button>
                </div>
            )}
            {success && (
                <div className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700 text-sm">
                    <Check className="w-4 h-4 flex-shrink-0" />
                    {success}
                </div>
            )}

            {/* Add Form */}
            {showForm && (
                <div className="p-6 bg-slate-50 border-b border-slate-100">
                    <div className="max-w-xl space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Transaction Type
                            </label>
                            <select
                                value={newType}
                                onChange={(e) => setNewType(e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                            >
                                {TRANSACTION_TYPES.map((type) => (
                                    <option key={type.code} value={type.code}>
                                        {type.code} - {type.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Email Addresses
                            </label>
                            <textarea
                                value={newEmails}
                                onChange={(e) => setNewEmails(e.target.value)}
                                placeholder="Enter email addresses, separated by commas or new lines"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                                rows={3}
                            />
                            <p className="text-xs text-slate-500 mt-1">
                                All converted {getTypeName(newType)} documents will be emailed to these addresses.
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={handleAddRoute}
                                disabled={saving || !newEmails.trim()}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50"
                            >
                                {saving ? "Adding..." : "Add Route"}
                            </button>
                            <button
                                onClick={() => {
                                    setShowForm(false);
                                    setNewEmails("");
                                }}
                                className="px-4 py-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Routes List */}
            <div className="divide-y divide-slate-100">
                {routes.length === 0 ? (
                    <div className="p-8 text-center text-slate-500">
                        <Mail className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                        <p className="font-medium">No email routes configured</p>
                        <p className="text-sm mt-1">Click "Add Rule" to auto-send documents to recipients</p>
                    </div>
                ) : (
                    routes.map((route) => (
                        <div key={route.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors">
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-bold">
                                        {route.transaction_type}
                                    </span>
                                    <span className="text-slate-600 text-sm">
                                        {TRANSACTION_TYPES.find(t => t.code === route.transaction_type)?.name}
                                    </span>
                                    {!route.is_active && (
                                        <span className="px-2 py-0.5 bg-slate-200 text-slate-500 rounded text-xs">
                                            Paused
                                        </span>
                                    )}
                                </div>
                                <div className="text-sm text-slate-500 mt-1">
                                    → {route.email_addresses.join(", ")}
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => handleToggleRoute(route)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${route.is_active
                                            ? "bg-slate-100 text-slate-600 hover:bg-slate-200"
                                            : "bg-green-100 text-green-700 hover:bg-green-200"
                                        }`}
                                >
                                    {route.is_active ? "Pause" : "Resume"}
                                </button>
                                <button
                                    onClick={() => handleDeleteRoute(route.id)}
                                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
