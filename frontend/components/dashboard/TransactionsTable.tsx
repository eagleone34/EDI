"use client";

import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/api-config";

interface Transaction {
    id: string;
    filename: string;
    po_number: string;
    transaction_type: string;
    status: string;
    formatted_date: string;
}

export default function TransactionsTable() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterType, setFilterType] = useState("all");

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                // Fetch from our new mocked endpoint
                const res = await fetch(`${API_BASE_URL}/api/v1/transactions/`);
                if (res.ok) {
                    const data = await res.json();
                    setTransactions(data);
                }
            } catch (error) {
                console.error("Failed to fetch transactions", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTransactions();
    }, []);

    const filteredTransactions = transactions.filter((txn) => {
        const matchesSearch = txn.po_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
            txn.filename.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = filterType === "all" || txn.transaction_type === filterType;

        return matchesSearch && matchesType;
    });

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Loading transactions...</div>;
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h2 className="text-xl font-bold text-slate-800">Recent Conversions</h2>

                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Search PO Number..."
                        className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />

                    <select
                        className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                    >
                        <option value="all">All Types</option>
                        <option value="850">850 (PO)</option>
                        <option value="810">810 (Invoice)</option>
                        <option value="856">856 (ASN)</option>
                        <option value="997">997 (Ack)</option>
                    </select>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="bg-slate-50 text-slate-500 font-medium">
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">PO Number</th>
                            <th className="px-6 py-4">Type</th>
                            <th className="px-6 py-4">Filename</th>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredTransactions.map((txn) => (
                            <tr key={txn.id} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${txn.status === "Completed"
                                        ? "bg-emerald-100 text-emerald-800"
                                        : "bg-amber-100 text-amber-800"
                                        }`}>
                                        {txn.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-semibold text-slate-900">
                                    {txn.po_number}
                                </td>
                                <td className="px-6 py-4">
                                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs font-bold">
                                        EDI {txn.transaction_type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-slate-600">
                                    {txn.filename}
                                </td>
                                <td className="px-6 py-4 text-slate-500">
                                    {txn.formatted_date}
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <button className="text-blue-600 hover:text-blue-800 font-medium text-xs hover:underline">
                                        Download PDF
                                    </button>
                                </td>
                            </tr>
                        ))}

                        {filteredTransactions.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                                    No transactions found matching your filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
