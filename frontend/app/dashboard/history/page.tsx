"use client";

import { useState } from "react";
import {
    FileText,
    Download,
    Search,
    Filter,
    Calendar,
    ChevronDown
} from "lucide-react";

// Mock data
const mockHistory = [
    { id: "1", filename: "walmart_po_12345.edi", type: "850", typeName: "Purchase Order", date: "2024-12-24T10:30:00", status: "completed", size: "2.4 KB" },
    { id: "2", filename: "target_invoice_67890.edi", type: "810", typeName: "Invoice", date: "2024-12-24T09:15:00", status: "completed", size: "1.8 KB" },
    { id: "3", filename: "amazon_asn_11111.edi", type: "856", typeName: "ASN", date: "2024-12-23T16:45:00", status: "completed", size: "3.2 KB" },
    { id: "4", filename: "costco_po_ack_22222.edi", type: "855", typeName: "PO Acknowledgment", date: "2024-12-23T14:20:00", status: "completed", size: "1.1 KB" },
    { id: "5", filename: "bestbuy_func_ack_33333.edi", type: "997", typeName: "Functional Ack", date: "2024-12-22T11:00:00", status: "completed", size: "0.8 KB" },
];

export default function HistoryPage() {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedType, setSelectedType] = useState("all");

    const filteredHistory = mockHistory.filter(item => {
        const matchesSearch = item.filename.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesType = selectedType === "all" || item.type === selectedType;
        return matchesSearch && matchesType;
    });

    return (
        <div className="max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl lg:text-3xl font-bold mb-2">Conversion History</h1>
                <p className="text-slate-600">View and download your past conversions</p>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-4 mb-6">
                <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search files..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                    </div>
                    <div className="relative">
                        <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                        <select
                            value={selectedType}
                            onChange={(e) => setSelectedType(e.target.value)}
                            className="pl-10 pr-10 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 appearance-none bg-white"
                        >
                            <option value="all">All Types</option>
                            <option value="850">850 - Purchase Order</option>
                            <option value="810">810 - Invoice</option>
                            <option value="856">856 - ASN</option>
                            <option value="855">855 - PO Ack</option>
                            <option value="997">997 - Func Ack</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* History Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">File</th>
                                <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Type</th>
                                <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600 hidden md:table-cell">Size</th>
                                <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600 hidden sm:table-cell">Date</th>
                                <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filteredHistory.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                                <FileText className="w-5 h-5 text-slate-500" />
                                            </div>
                                            <span className="font-medium text-slate-900 truncate max-w-[200px]">
                                                {item.filename}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-primary-50 text-primary-700">
                                            {item.type}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-500 hidden md:table-cell">{item.size}</td>
                                    <td className="px-6 py-4 text-slate-500 hidden sm:table-cell">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="w-4 h-4" />
                                            {new Date(item.date).toLocaleDateString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-end gap-2">
                                            <button className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors" title="PDF">
                                                <Download className="w-4 h-4" />
                                            </button>
                                            <button className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors" title="Excel">
                                                <Download className="w-4 h-4" />
                                            </button>
                                            <button className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors" title="HTML">
                                                <Download className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {filteredHistory.length === 0 && (
                    <div className="p-12 text-center text-slate-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <p>No conversions found matching your criteria.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
