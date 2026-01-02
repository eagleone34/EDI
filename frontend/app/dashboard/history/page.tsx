"use client";

import { useState, useEffect, useMemo } from "react";
import {
    FileText,
    Download,
    Search,
    Filter,
    Calendar,
    ChevronDown,
    ChevronUp,
    Loader2
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";

type SortField = "created_at" | "transaction_type" | "filename";
type SortDirection = "asc" | "desc";

export default function HistoryPage() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedType, setSelectedType] = useState("all");
    const [sortField, setSortField] = useState<SortField>("created_at");
    const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

    useEffect(() => {
        const fetchDocuments = async () => {
            if (!user?.userId) {
                setLoading(false);
                return;
            }

            try {
                const { data, error } = await supabase
                    .from("documents")
                    .select("*")
                    .eq("user_id", user.userId)
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
    }, [user?.userId]);

    // Filter and sort documents
    const filteredAndSortedDocuments = useMemo(() => {
        let result = documents.filter((doc) => {
            const matchesSearch = doc.filename.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesType = selectedType === "all" || doc.transaction_type === selectedType;
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
    }, [documents, searchQuery, selectedType, sortField, sortDirection]);

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
        return (
            <div className="max-w-7xl mx-auto p-8 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
                <p className="text-slate-500 mt-4">Loading your conversion history...</p>
            </div>
        );
    }

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
                            <option value="812">812 - Credit/Debit</option>
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
                                <th
                                    className="text-left px-6 py-4 text-sm font-semibold text-slate-600 cursor-pointer hover:text-slate-900"
                                    onClick={() => handleSort("filename")}
                                >
                                    File <SortIcon field="filename" />
                                </th>
                                <th
                                    className="text-left px-6 py-4 text-sm font-semibold text-slate-600 cursor-pointer hover:text-slate-900"
                                    onClick={() => handleSort("transaction_type")}
                                >
                                    Type <SortIcon field="transaction_type" />
                                </th>
                                <th
                                    className="text-left px-6 py-4 text-sm font-semibold text-slate-600 hidden sm:table-cell cursor-pointer hover:text-slate-900"
                                    onClick={() => handleSort("created_at")}
                                >
                                    Date <SortIcon field="created_at" />
                                </th>
                                <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filteredAndSortedDocuments.map((doc) => (
                                <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                                <FileText className="w-5 h-5 text-slate-500" />
                                            </div>
                                            <div>
                                                <span className="font-medium text-slate-900 truncate max-w-[200px] block">
                                                    {doc.filename}
                                                </span>
                                                <span className="text-xs text-slate-400">{doc.transaction_name}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-primary-50 text-primary-700">
                                            EDI {doc.transaction_type}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-500 hidden sm:table-cell">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="w-4 h-4" />
                                            {formatDate(doc.created_at)}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-end gap-2">
                                            {doc.pdf_url && (
                                                <a
                                                    href={doc.pdf_url}
                                                    target="_blank"
                                                    className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                                                    title="PDF"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </a>
                                            )}
                                            {doc.excel_url && (
                                                <a
                                                    href={doc.excel_url}
                                                    target="_blank"
                                                    className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
                                                    title="Excel"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </a>
                                            )}
                                            {doc.html_url && (
                                                <a
                                                    href={doc.html_url}
                                                    target="_blank"
                                                    className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                                                    title="HTML"
                                                >
                                                    <Download className="w-4 h-4" />
                                                </a>
                                            )}
                                            {!doc.pdf_url && !doc.excel_url && !doc.html_url && (
                                                <span className="text-xs text-slate-400">No files</span>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {filteredAndSortedDocuments.length === 0 && (
                    <div className="p-12 text-center text-slate-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        {documents.length === 0 ? (
                            <>
                                <p className="font-medium">No conversions yet</p>
                                <p className="text-sm mt-1">Upload an EDI file on the homepage to get started</p>
                            </>
                        ) : (
                            <p>No conversions found matching your filters.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
