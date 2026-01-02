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
    Loader2,
    Eye,
    Mail,
    MoreHorizontal,
    X
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";

type SortField = "created_at" | "transaction_type" | "filename" | "trading_partner";
type SortDirection = "asc" | "desc";

export default function HistoryPage() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedType, setSelectedType] = useState("all");
    const [sortField, setSortField] = useState<SortField>("created_at");
    const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
    const [activeActionMenu, setActiveActionMenu] = useState<string | null>(null);
    const [emailModal, setEmailModal] = useState<{ doc: Document } | null>(null);
    const [emailTo, setEmailTo] = useState("");
    const [emailSending, setEmailSending] = useState(false);

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

    // Get unique transaction types from actual data for dynamic filter
    const availableTypes = useMemo(() => {
        const types = new Set<string>();
        documents.forEach((doc) => {
            types.add(doc.transaction_type);
        });
        return Array.from(types).sort();
    }, [documents]);

    // Transaction type names mapping
    const typeNames: Record<string, string> = {
        "850": "Purchase Order",
        "810": "Invoice",
        "812": "Credit/Debit",
        "856": "ASN",
        "855": "PO Ack",
        "997": "Func Ack",
        "820": "Payment",
        "860": "PO Change",
        "861": "Receiving",
        "870": "Status",
    };

    // Filter and sort documents
    const filteredAndSortedDocuments = useMemo(() => {
        let result = documents.filter((doc) => {
            const matchesSearch =
                doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (doc.trading_partner?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
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

    // Action handlers
    const handleView = (doc: Document) => {
        if (doc.html_url) {
            window.open(doc.html_url, "_blank");
        } else if (doc.pdf_url) {
            window.open(doc.pdf_url, "_blank");
        }
        setActiveActionMenu(null);
    };

    const handleDownload = (doc: Document) => {
        if (doc.pdf_url) {
            const link = document.createElement("a");
            link.href = doc.pdf_url;
            link.download = doc.filename.replace(/\.[^/.]+$/, "") + ".pdf";
            link.click();
        }
        setActiveActionMenu(null);
    };

    const handleEmailClick = (doc: Document) => {
        setEmailModal({ doc });
        setActiveActionMenu(null);
    };

    const handleSendEmail = async () => {
        if (!emailModal || !emailTo) return;

        setEmailSending(true);
        // TODO: Implement email sending via backend API
        await new Promise(resolve => setTimeout(resolve, 1000));
        alert(`Email would be sent to: ${emailTo} with ${emailModal.doc.filename}`);
        setEmailSending(false);
        setEmailModal(null);
        setEmailTo("");
    };

    // Close action menu when clicking outside
    useEffect(() => {
        const handleClickOutside = () => setActiveActionMenu(null);
        if (activeActionMenu) {
            document.addEventListener("click", handleClickOutside);
            return () => document.removeEventListener("click", handleClickOutside);
        }
    }, [activeActionMenu]);

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto p-8 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
                <p className="text-slate-500 mt-4">Loading your conversion history...</p>
            </div>
        );
    }

    return (
        <>
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
                                placeholder="Search files or customers..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            />
                        </div>
                        <div className="relative">
                            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            {/* Dynamic filter - only shows types that exist in data */}
                            <select
                                value={selectedType}
                                onChange={(e) => setSelectedType(e.target.value)}
                                className="pl-10 pr-10 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 appearance-none bg-white"
                            >
                                <option value="all">All Types</option>
                                {availableTypes.map((type) => (
                                    <option key={type} value={type}>
                                        {type} - {typeNames[type] || type}
                                    </option>
                                ))}
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
                                        className="text-left px-6 py-4 text-sm font-semibold text-slate-600 cursor-pointer hover:text-slate-900"
                                        onClick={() => handleSort("trading_partner")}
                                    >
                                        Customer <SortIcon field="trading_partner" />
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
                                        <td className="px-6 py-4 text-slate-600">
                                            {doc.trading_partner || <span className="text-slate-400">—</span>}
                                        </td>
                                        <td className="px-6 py-4 text-slate-500 hidden sm:table-cell">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="w-4 h-4" />
                                                {formatDate(doc.created_at)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center justify-end">
                                                <div className="relative">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setActiveActionMenu(activeActionMenu === doc.id ? null : doc.id);
                                                        }}
                                                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                                                    >
                                                        <MoreHorizontal className="w-4 h-4 text-slate-500" />
                                                    </button>

                                                    {/* Action Dropdown */}
                                                    {activeActionMenu === doc.id && (
                                                        <div className="absolute right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10 min-w-[140px]">
                                                            <button
                                                                onClick={() => handleView(doc)}
                                                                className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                                                            >
                                                                <Eye className="w-4 h-4" />
                                                                View
                                                            </button>
                                                            <button
                                                                onClick={() => handleDownload(doc)}
                                                                className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                                                            >
                                                                <Download className="w-4 h-4" />
                                                                Download
                                                            </button>
                                                            <button
                                                                onClick={() => handleEmailClick(doc)}
                                                                className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                                                            >
                                                                <Mail className="w-4 h-4" />
                                                                Email
                                                            </button>
                                                        </div>
                                                    )}
                                                </div>
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
                                    <p className="text-sm mt-1">Upload an EDI file on the dashboard to get started</p>
                                </>
                            ) : (
                                <p>No conversions found matching your filters.</p>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Email Modal */}
            {emailModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-slate-800">Send via Email</h3>
                            <button onClick={() => setEmailModal(null)} className="p-1 hover:bg-slate-100 rounded">
                                <X className="w-5 h-5 text-slate-500" />
                            </button>
                        </div>

                        <p className="text-sm text-slate-600 mb-4">
                            Send <span className="font-medium">{emailModal.doc.filename}</span> to:
                        </p>

                        <input
                            type="email"
                            placeholder="recipient@example.com"
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
                            value={emailTo}
                            onChange={(e) => setEmailTo(e.target.value)}
                        />

                        <div className="flex gap-3">
                            <button
                                onClick={() => setEmailModal(null)}
                                className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSendEmail}
                                disabled={!emailTo || emailSending}
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                            >
                                {emailSending ? "Sending..." : "Send Email"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
