"use client";

import { useState, useEffect, useMemo } from "react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";
import { ChevronUp, ChevronDown, FileText } from "lucide-react";

type SortField = "created_at" | "transaction_type" | "filename";
type SortDirection = "asc" | "desc";

export default function TransactionsTable() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterType, setFilterType] = useState("all");
    const [sortField, setSortField] = useState<SortField>("created_at");
    const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

    useEffect(() => {
        const fetchDocuments = async () => {
            if (!user?.id) {
                setLoading(false);
                return;
            }

            try {
                const { data, error } = await supabase
                    .from("documents")
                    .select("*")
                    .eq("user_id", user.id)
                    .order("created_at", { ascending: false });

                if (error) {
                    console.error("Error fetching documents:", error);
                } else {
                    setDocuments(data || []);
                }
            } catch (error) {
                console.error("Failed to fetch documents", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDocuments();
    }, [user?.id]);

    // Filter and sort documents
    const filteredAndSortedDocuments = useMemo(() => {
        let result = documents.filter((doc) => {
            const matchesSearch =
                doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                doc.transaction_name.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = filterType === "all" || doc.transaction_type === filterType;
            return matchesSearch && matchesType;
        });

        // Sort
        result.sort((a, b) => {
            let aVal: string | number = a[sortField] || "";
            let bVal: string | number = b[sortField] || "";

            if (sortField === "created_at") {
                aVal = new Date(a.created_at).getTime();
                bVal = new Date(b.created_at).getTime();
            }

            if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
            if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
            return 0;
        });

        return result;
    }, [documents, searchTerm, filterType, sortField, sortDirection]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc");
        } else {
            setSortField(field);
            setSortDirection("desc");
        }
    };

    const SortIcon = ({ field }: { field: SortField }) => {
        if (sortField !== field) return null;
        return sortDirection === "asc"
            ? <ChevronUp className="w-4 h-4 inline ml-1" />
            : <ChevronDown className="w-4 h-4 inline ml-1" />;
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    };

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Loading your conversions...</div>;
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h2 className="text-xl font-bold text-slate-800">Recent Conversions</h2>

                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Search files..."
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
                        <option value="850">850 (Purchase Order)</option>
                        <option value="810">810 (Invoice)</option>
                        <option value="812">812 (Credit/Debit)</option>
                        <option value="856">856 (ASN)</option>
                        <option value="855">855 (PO Ack)</option>
                        <option value="997">997 (Func Ack)</option>
                    </select>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="bg-slate-50 text-slate-500 font-medium">
                            <th className="px-6 py-4">Status</th>
                            <th
                                className="px-6 py-4 cursor-pointer hover:text-slate-700 select-none"
                                onClick={() => handleSort("transaction_type")}
                            >
                                Type <SortIcon field="transaction_type" />
                            </th>
                            <th
                                className="px-6 py-4 cursor-pointer hover:text-slate-700 select-none"
                                onClick={() => handleSort("filename")}
                            >
                                Filename <SortIcon field="filename" />
                            </th>
                            <th
                                className="px-6 py-4 cursor-pointer hover:text-slate-700 select-none"
                                onClick={() => handleSort("created_at")}
                            >
                                Date <SortIcon field="created_at" />
                            </th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredAndSortedDocuments.map((doc) => (
                            <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-6 py-4">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                                        Completed
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs font-bold">
                                        EDI {doc.transaction_type}
                                    </span>
                                    <span className="text-slate-400 text-xs ml-2">{doc.transaction_name}</span>
                                </td>
                                <td className="px-6 py-4 text-slate-600 font-medium">
                                    {doc.filename}
                                </td>
                                <td className="px-6 py-4 text-slate-500">
                                    {formatDate(doc.created_at)}
                                </td>
                                <td className="px-6 py-4 text-right space-x-3">
                                    {doc.pdf_url && (
                                        <a
                                            href={doc.pdf_url}
                                            target="_blank"
                                            className="text-blue-600 hover:text-blue-800 font-medium text-xs hover:underline"
                                        >
                                            PDF
                                        </a>
                                    )}
                                    {doc.excel_url && (
                                        <a
                                            href={doc.excel_url}
                                            target="_blank"
                                            className="text-green-600 hover:text-green-800 font-medium text-xs hover:underline"
                                        >
                                            Excel
                                        </a>
                                    )}
                                    {doc.html_url && (
                                        <a
                                            href={doc.html_url}
                                            target="_blank"
                                            className="text-purple-600 hover:text-purple-800 font-medium text-xs hover:underline"
                                        >
                                            HTML
                                        </a>
                                    )}
                                </td>
                            </tr>
                        ))}

                        {filteredAndSortedDocuments.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-6 py-16 text-center">
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
                                            <FileText className="w-8 h-8 text-slate-400" />
                                        </div>
                                        <div>
                                            <p className="text-slate-600 font-medium">No conversions yet</p>
                                            <p className="text-slate-400 text-sm mt-1">
                                                Upload an EDI file on the homepage to get started
                                            </p>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
