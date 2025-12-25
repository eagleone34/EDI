"use client";

import { useState } from "react";
import {
    Plus,
    Trash2,
    Edit2,
    Route,
    FileText,
    Mail,
    X
} from "lucide-react";

interface RoutingRule {
    id: string;
    documentType: string;
    documentName: string;
    recipients: string[];
    enabled: boolean;
}

const mockRules: RoutingRule[] = [
    { id: "1", documentType: "850", documentName: "Purchase Order", recipients: ["procurement@company.com"], enabled: true },
    { id: "2", documentType: "810", documentName: "Invoice", recipients: ["accounting@company.com", "ap@company.com"], enabled: true },
    { id: "3", documentType: "856", documentName: "Advance Ship Notice", recipients: ["warehouse@company.com"], enabled: false },
];

export default function RoutingPage() {
    const [rules, setRules] = useState<RoutingRule[]>(mockRules);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingRule, setEditingRule] = useState<RoutingRule | null>(null);

    const handleToggleRule = (id: string) => {
        setRules(rules.map(rule =>
            rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
        ));
    };

    const handleDeleteRule = (id: string) => {
        setRules(rules.filter(rule => rule.id !== id));
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold mb-2">Routing Rules</h1>
                    <p className="text-slate-600">Automatically route documents to the right people</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
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
                            and send the converted output to your configured recipients. Set up rules below to customize
                            where each document type goes.
                        </p>
                    </div>
                </div>
            </div>

            {/* Rules List */}
            <div className="space-y-4">
                {rules.map((rule) => (
                    <div
                        key={rule.id}
                        className={`bg-white rounded-2xl border p-6 transition-all ${rule.enabled ? "border-slate-200 shadow-sm" : "border-slate-100 opacity-60"
                            }`}
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex items-start gap-4">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${rule.enabled ? "bg-primary-100" : "bg-slate-100"
                                    }`}>
                                    <FileText className={`w-6 h-6 ${rule.enabled ? "text-primary-600" : "text-slate-400"}`} />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-semibold text-slate-900">{rule.documentName}</span>
                                        <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-md font-medium">
                                            {rule.documentType}
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {rule.recipients.map((email, i) => (
                                            <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 rounded-lg text-sm">
                                                <Mail className="w-3.5 h-3.5 text-slate-400" />
                                                <span className="text-slate-600">{email}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {/* Toggle */}
                                <button
                                    onClick={() => handleToggleRule(rule.id)}
                                    className={`relative w-12 h-6 rounded-full transition-colors ${rule.enabled ? "bg-primary-600" : "bg-slate-200"
                                        }`}
                                >
                                    <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${rule.enabled ? "left-7" : "left-1"
                                        }`} />
                                </button>
                                <button
                                    onClick={() => setEditingRule(rule)}
                                    className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                                >
                                    <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => handleDeleteRule(rule.id)}
                                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}

                {rules.length === 0 && (
                    <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
                        <Route className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <h3 className="font-semibold text-slate-900 mb-2">No routing rules yet</h3>
                        <p className="text-slate-500 mb-4">Create your first rule to start routing documents automatically.</p>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            Create Rule
                        </button>
                    </div>
                )}
            </div>

            {/* Add Rule Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
                    <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold">Add Routing Rule</h3>
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
                                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500">
                                    <option>850 - Purchase Order</option>
                                    <option>810 - Invoice</option>
                                    <option>856 - Advance Ship Notice</option>
                                    <option>855 - PO Acknowledgment</option>
                                    <option>997 - Functional Acknowledgment</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Send to (email)</label>
                                <input
                                    type="email"
                                    placeholder="team@company.com"
                                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 py-2.5 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button className="flex-1 py-2.5 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors">
                                    Save Rule
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
