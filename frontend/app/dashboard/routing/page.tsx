"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Edit2, Mail, FileText, Route, X, Save, Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";

interface RoutingRule {
    id: string;
    user_id: string;
    transaction_type: string;
    email_addresses: string[];
    is_active: boolean;
    formats: string[];
    created_at?: string;
}

const DOCUMENT_TYPES = [
    { code: "850", name: "Purchase Order" },
    { code: "810", name: "Invoice" },
    { code: "856", name: "Advance Ship Notice" },
    { code: "855", name: "PO Acknowledgment" },
    { code: "997", name: "Functional Acknowledgment" },
    { code: "820", name: "Payment Order/Remittance" },
    { code: "860", name: "PO Change Request" },
    { code: "875", name: "Grocery Purchase Order" },
    { code: "880", name: "Grocery Invoice" },
    { code: "812", name: "Credit/Debit Adjustment" },
];

export default function RoutingPage() {
    const { user } = useAuth();
    const [rules, setRules] = useState<RoutingRule[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Form State
    const [editingRule, setEditingRule] = useState<RoutingRule | null>(null);
    const [selectedType, setSelectedType] = useState(DOCUMENT_TYPES[0].code);
    const [emailInput, setEmailInput] = useState("");
    const [selectedFormats, setSelectedFormats] = useState<string[]>(["pdf"]);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (user) {
            fetchRules();
        } else {
            setLoading(false);
        }
    }, [user]);

    const fetchRules = async () => {
        try {
            const { data, error } = await supabase
                .from("email_routes")
                .select("*")
                .eq("user_id", user?.id)
                .order("created_at", { ascending: false });

            if (error) throw error;
            setRules(data || []);
        } catch (error) {
            console.error("Error fetching rules:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenNewRule = () => {
        setEditingRule(null);
        setSelectedType(DOCUMENT_TYPES[0].code);
        setEmailInput("");
        setSelectedFormats(["pdf"]);
        setIsModalOpen(true);
    };

    const handleEditRule = (rule: RoutingRule) => {
        setEditingRule(rule);
        setSelectedType(rule.transaction_type);
        setEmailInput(rule.email_addresses.join(", "));
        setSelectedFormats(rule.formats || ["pdf"]);
        setIsModalOpen(true);
    };

    const handleFormatToggle = (format: string) => {
        if (selectedFormats.includes(format)) {
            if (selectedFormats.length > 1) {
                setSelectedFormats(selectedFormats.filter(f => f !== format));
            }
        } else {
            setSelectedFormats([...selectedFormats, format]);
        }
    };

    const handleSaveRule = async () => {
        if (!user) return;

        const emails = emailInput.split(",").map(e => e.trim()).filter(e => e);
        if (emails.length === 0) {
            alert("Please enter at least one valid email address.");
            return;
        }

        setSaving(true);
        try {
            const payload = {
                user_id: user.id,
                transaction_type: selectedType,
                email_addresses: emails,
                formats: selectedFormats,
                is_active: editingRule ? editingRule.is_active : true,
            };

            if (editingRule) {
                const { error } = await supabase
                    .from("email_routes")
                    .update(payload)
                    .eq("id", editingRule.id);
                if (error) throw error;
            } else {
                const { error } = await supabase
                    .from("email_routes")
                    .insert(payload);
                if (error) throw error;
            }

            await fetchRules();
            setIsModalOpen(false);
        } catch (error: any) {
            console.error("Error saving rule:", error);
            // Handle unique constraint violation
            if (error.code === '23505') {
                alert("A rule for this document type already exists. Please edit the existing rule instead.");
            } else {
                alert("Failed to save rule. Please try again.");
            }
        } finally {
            setSaving(false);
        }
    };

    const handleToggleRule = async (rule: RoutingRule) => {
        try {
            // Optimistic update
            const updatedRules = rules.map(r => r.id === rule.id ? { ...r, is_active: !r.is_active } : r);
            setRules(updatedRules);

            const { error } = await supabase
                .from("email_routes")
                .update({ is_active: !rule.is_active })
                .eq("id", rule.id);

            if (error) {
                // Revert on error
                setRules(rules);
                console.error("Error toggling rule:", error);
            }
        } catch (error) {
            console.error("Error toggling rule:", error);
        }
    };

    const handleDeleteRule = async (id: string) => {
        if (!confirm("Are you sure you want to delete this routing rule?")) return;

        try {
            const { error } = await supabase
                .from("email_routes")
                .delete()
                .eq("id", id);

            if (error) throw error;
            setRules(rules.filter(r => r.id !== id));
        } catch (error) {
            console.error("Error deleting rule:", error);
            alert("Failed to delete rule.");
        }
    };

    const getDocName = (type: string) => {
        return DOCUMENT_TYPES.find(d => d.code === type)?.name || "Unknown Document";
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold mb-2">Routing Rules</h1>
                    <p className="text-slate-600">Automatically route documents to the right people</p>
                </div>
                <button
                    onClick={handleOpenNewRule}
                    className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    <span className="hidden sm:inline">Add Rule</span>
                </button>
            </div>

            {/* Explanation Card */}
            <div className="bg-gradient-to-r from-primary-50 to-violet-50 border border-primary-100 rounded-2xl p-6 mb-6">
                <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
                        <Route className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-slate-900 mb-1">How Routing Works</h3>
                        <p className="text-slate-600 text-sm">
                            When you forward an EDI file to your email address, we automatically detect the document type
                            and send the converted output to your configured recipients.
                        </p>
                    </div>
                </div>
            </div>

            {/* Rules List */}
            <div className="space-y-4">
                {rules.map((rule) => (
                    <div
                        key={rule.id}
                        className={`bg-white rounded-2xl border p-6 transition-all ${rule.is_active ? "border-slate-200 shadow-sm" : "border-slate-100 opacity-60"
                            }`}
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex items-start gap-4">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${rule.is_active ? "bg-primary-100" : "bg-slate-100"
                                    }`}>
                                    <FileText className={`w-6 h-6 ${rule.is_active ? "text-primary-600" : "text-slate-400"}`} />
                                </div>
                                <div>
                                    <div className="flex items-center gap-3 mb-1">
                                        <span className="font-semibold text-slate-900">{getDocName(rule.transaction_type)}</span>
                                        <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-md font-medium">
                                            {rule.transaction_type}
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-2 mt-2 mb-3">
                                        {rule.email_addresses.map((email, i) => (
                                            <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 rounded-lg text-sm">
                                                <Mail className="w-3.5 h-3.5 text-slate-400" />
                                                <span className="text-slate-600">{email}</span>
                                            </div>
                                        ))}
                                    </div>
                                    {/* Format Badges */}
                                    <div className="flex gap-2">
                                        {(rule.formats || ["pdf"]).map(f => (
                                            <span key={f} className="text-[10px] items-center gap-1 font-semibold uppercase text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {/* Toggle */}
                                <button
                                    onClick={() => handleToggleRule(rule)}
                                    className={`relative w-12 h-6 rounded-full transition-colors ${rule.is_active ? "bg-primary-600" : "bg-slate-200"
                                        }`}
                                    title={rule.is_active ? "Pause Rule" : "Activate Rule"}
                                >
                                    <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${rule.is_active ? "left-7" : "left-1"
                                        }`} />
                                </button>
                                <button
                                    onClick={() => handleEditRule(rule)}
                                    className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                                    title="Edit Rule"
                                >
                                    <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleDeleteRule(rule.id)}
                                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Delete Rule"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}

                {!loading && rules.length === 0 && (
                    <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
                        <Route className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <h3 className="font-semibold text-slate-900 mb-2">No routing rules yet</h3>
                        <p className="text-slate-500 mb-4">Create your first rule to start routing documents automatically.</p>
                        <button
                            onClick={handleOpenNewRule}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            Create Rule
                        </button>
                    </div>
                )}
            </div>

            {/* Add/Edit Rule Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
                    <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold">{editingRule ? "Edit Rule" : "Add Routing Rule"}</h3>
                            <button
                                onClick={() => setIsModalOpen(false)}
                                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Document Type</label>
                                <select
                                    value={selectedType}
                                    onChange={(e) => setSelectedType(e.target.value)}
                                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                                >
                                    {DOCUMENT_TYPES.map(type => (
                                        <option key={type.code} value={type.code}>{type.code} - {type.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Send to (email)</label>
                                <input
                                    type="text"
                                    placeholder="team@company.com, other@example.com"
                                    value={emailInput}
                                    onChange={(e) => setEmailInput(e.target.value)}
                                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                <p className="text-xs text-slate-500 mt-1">Separate multiple emails with commas</p>
                            </div>

                            {/* Formats Selection */}
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">Include Formats</label>
                                <div className="flex gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={selectedFormats.includes('pdf')}
                                            onChange={() => handleFormatToggle('pdf')}
                                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                                        />
                                        <span className="text-sm text-slate-600">PDF</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={selectedFormats.includes('excel')}
                                            onChange={() => handleFormatToggle('excel')}
                                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                                        />
                                        <span className="text-sm text-slate-600">Excel</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={selectedFormats.includes('html')}
                                            onChange={() => handleFormatToggle('html')}
                                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                                        />
                                        <span className="text-sm text-slate-600">HTML</span>
                                    </label>
                                </div>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 py-2.5 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors"
                                    disabled={saving}
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveRule}
                                    disabled={saving}
                                    className="flex-1 py-2.5 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
                                >
                                    {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                                    {editingRule ? "Save Changes" : "Create Rule"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
