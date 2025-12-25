"use client";

import { useState } from "react";
import { FileUploader } from "@/components/FileUploader";
import {
    FileUp,
    Mail,
    FileText,
    TrendingUp,
    Clock,
    ArrowUpRight,
    Download,
    Copy,
    CheckCircle
} from "lucide-react";

// Mock data for demo
const mockConversions = [
    {
        id: "1",
        filename: "walmart_po_12345.edi",
        type: "850",
        typeName: "Purchase Order",
        date: "2024-12-24T10:30:00",
        status: "completed"
    },
    {
        id: "2",
        filename: "target_invoice_67890.edi",
        type: "810",
        typeName: "Invoice",
        date: "2024-12-24T09:15:00",
        status: "completed"
    },
    {
        id: "3",
        filename: "amazon_asn_11111.edi",
        type: "856",
        typeName: "Advance Ship Notice",
        date: "2024-12-23T16:45:00",
        status: "completed"
    }
];

export default function DashboardPage() {
    const [emailCopied, setEmailCopied] = useState(false);
    const userEmail = "user-demo@edi.email";

    const handleCopyEmail = () => {
        navigator.clipboard.writeText(userEmail);
        setEmailCopied(true);
        setTimeout(() => setEmailCopied(false), 2000);
    };

    return (
        <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl lg:text-3xl font-bold mb-2">Dashboard</h1>
                <p className="text-slate-600">Welcome back! Here&apos;s your conversion summary.</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
                <div className="bg-white rounded-2xl p-5 lg:p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-slate-500 text-sm font-medium">This Month</span>
                        <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
                            <TrendingUp className="w-4 h-4 text-emerald-600" />
                        </div>
                    </div>
                    <div className="text-2xl lg:text-3xl font-bold">3</div>
                    <div className="text-slate-500 text-sm">conversions</div>
                </div>

                <div className="bg-white rounded-2xl p-5 lg:p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-slate-500 text-sm font-medium">Remaining</span>
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <FileText className="w-4 h-4 text-blue-600" />
                        </div>
                    </div>
                    <div className="text-2xl lg:text-3xl font-bold">7</div>
                    <div className="text-slate-500 text-sm">free conversions</div>
                </div>

                <div className="bg-white rounded-2xl p-5 lg:p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-slate-500 text-sm font-medium">Avg. Time</span>
                        <div className="w-8 h-8 bg-violet-100 rounded-lg flex items-center justify-center">
                            <Clock className="w-4 h-4 text-violet-600" />
                        </div>
                    </div>
                    <div className="text-2xl lg:text-3xl font-bold">1.2s</div>
                    <div className="text-slate-500 text-sm">processing</div>
                </div>

                <div className="bg-gradient-to-br from-primary-600 to-violet-600 rounded-2xl p-5 lg:p-6 shadow-lg text-white">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-white/80 text-sm font-medium">Your Email</span>
                        <Mail className="w-5 h-5 text-white/80" />
                    </div>
                    <div className="text-sm font-medium break-all mb-2">{userEmail}</div>
                    <button
                        onClick={handleCopyEmail}
                        className="text-xs flex items-center gap-1 text-white/80 hover:text-white transition-colors"
                    >
                        {emailCopied ? (
                            <>
                                <CheckCircle className="w-3 h-3" />
                                Copied!
                            </>
                        ) : (
                            <>
                                <Copy className="w-3 h-3" />
                                Copy address
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Quick Upload */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 mb-8 overflow-hidden">
                <div className="p-5 lg:p-6 border-b border-slate-100">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <FileUp className="w-5 h-5 text-primary-600" />
                        Quick Convert
                    </h2>
                </div>
                <div className="p-5 lg:p-6">
                    <FileUploader />
                </div>
            </div>

            {/* Recent Conversions */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
                <div className="p-5 lg:p-6 border-b border-slate-100 flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Recent Conversions</h2>
                    <a href="/dashboard/history" className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
                        View all
                        <ArrowUpRight className="w-4 h-4" />
                    </a>
                </div>

                {mockConversions.length > 0 ? (
                    <div className="divide-y divide-slate-100">
                        {mockConversions.map((conversion) => (
                            <div key={conversion.id} className="p-5 lg:p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                                        <FileText className="w-5 h-5 text-slate-500" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-slate-900">{conversion.filename}</p>
                                        <p className="text-sm text-slate-500">
                                            {conversion.type} - {conversion.typeName}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="text-right hidden sm:block">
                                        <p className="text-sm text-slate-500">
                                            {new Date(conversion.date).toLocaleDateString()}
                                        </p>
                                        <p className="text-xs text-slate-400">
                                            {new Date(conversion.date).toLocaleTimeString()}
                                        </p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors" title="Download PDF">
                                            <Download className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center text-slate-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <p>No conversions yet. Upload your first EDI file above!</p>
                    </div>
                )}
            </div>
        </div>
    );
}
