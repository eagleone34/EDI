"use client";

import { useState, useEffect, useMemo } from "react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";
import { ChevronUp, ChevronDown, FileText, Eye, Download, Mail, MoreHorizontal, X, Trash2 } from "lucide-react";

type SortField = "created_at" | "transaction_type" | "filename" | "trading_partner";
type SortDirection = "asc" | "desc";

export default function TransactionsTable() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterType, setFilterType] = useState("all");
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
                doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                doc.transaction_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (doc.trading_partner?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false);
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

    // Action handlers
    const handleView = (doc: Document) => {
        // Helper to open base64 data in new tab via Blob
        const openDataUrl = (dataUrl: string, type: string) => {
            try {
                // Extract base64 content
                const base64Match = dataUrl.match(/base64,(.+)/);
                if (!base64Match) return false;

                const base64Data = base64Match[1];
                const byteCharacters = atob(base64Data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: type });
                const url = URL.createObjectURL(blob);
                window.open(url, "_blank");

                // Cleanup URL after a delay (browser needs it to open tab first)
                setTimeout(() => URL.revokeObjectURL(url), 60000);
                return true;
            } catch (e) {
                console.error("Error displaying file:", e);
                return false;
            }
        };

        if (doc.pdf_url) {
            // Prioritize PDF View
            openDataUrl(doc.pdf_url, "application/pdf");
        } else if (doc.html_url) {
            // Fallback to HTML
            openDataUrl(doc.html_url, "text/html");
        } else {
            alert("File preview not available for this archived item.");
        }
        setActiveActionMenu(null);
    };

    const handleDownload = (doc: Document) => {
        if (doc.pdf_url) {
            const link = document.createElement("a");
            link.href = doc.pdf_url;
            link.download = doc.filename.replace(/\.[^/.]+$/, "") + ".pdf";
            link.click();
        } else {
            alert("Download not available for this archived item.");
        }
        setActiveActionMenu(null);
    };

    const handleDelete = async (doc: Document) => {
        if (!confirm("Are you sure you want to delete this conversion history?")) {
            setActiveActionMenu(null);
            return;
        }

        try {
            const { error } = await supabase
                .from("documents")
                .delete()
                .eq("id", doc.id);

            if (error) {
                console.error("Error deleting document:", error);
                alert("Failed to delete document.");
            } else {
                // Optimistic update
                setDocuments(prev => prev.filter(d => d.id !== doc.id));
            }
        } catch (err) {
            console.error("Error deleting document:", err);
            alert("An error occurred while deleting.");
        } finally {
            setActiveActionMenu(null);
        }
    };

    const handleEmailClick = (doc: Document) => {
        setEmailModal({ doc });
        setActiveActionMenu(null);
    };

    const handleSendEmail = async () => {
        if (!emailModal || !emailTo) return;

        setEmailSending(true);

        try {
            const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://edi-production-d983.up.railway.app";

            const response = await fetch(`${API_BASE}/api/v1/email/send`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    to_emails: emailTo.split(",").map(e => e.trim()).filter(e => e),
                    filename: emailModal.doc.filename,
                    transaction_type: emailModal.doc.transaction_type,
                    transaction_name: emailModal.doc.transaction_name || emailModal.doc.transaction_type,
                    trading_partner: emailModal.doc.trading_partner,
                    document_id: emailModal.doc.id,
                }),
            });

            const result = await response.json();

            if (response.ok && result.status === "success") {
                alert(`Email sent successfully to: ${emailTo}`);
            } else {
                alert(`Failed to send email: ${result.detail || result.message || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Email send error:", error);
            alert("Failed to send email. Please try again.");
        } finally {
            setEmailSending(false);
            setEmailModal(null);
            setEmailTo("");
        }
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
        return <div className="p-8 text-center text-gray-500">Loading your conversions...</div>;
    }

    return (
        <>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200">
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

                        {/* Dynamic filter - only shows types that exist in data */}
                        <select
                            className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                        >
                            <option value="all">All Types</option>
                            {availableTypes.map((type) => (
                                <option key={type} value={type}>
                                    {type} ({typeNames[type] || type})
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 pb-32">
                    <table className="w-full table-fixed text-left text-sm">
                        <thead>
                            <tr className="bg-slate-50 text-slate-500 font-medium">
                                <th className="px-3 py-3 w-[8%]">Status</th>
                                <th
                                    className="px-3 py-3 cursor-pointer hover:text-slate-700 select-none w-[12%]"
                                    onClick={() => handleSort("transaction_type")}
                                >
                                    Type <SortIcon field="transaction_type" />
                                </th>
                                <th
                                    className="px-3 py-3 cursor-pointer hover:text-slate-700 select-none w-[15%]"
                                    onClick={() => handleSort("trading_partner")}
                                >
                                    Customer <SortIcon field="trading_partner" />
                                </th>
                                <th
                                    className="px-3 py-3 cursor-pointer hover:text-slate-700 select-none w-[38%]"
                                    onClick={() => handleSort("filename")}
                                >
                                    Filename <SortIcon field="filename" />
                                </th>
                                <th
                                    className="px-3 py-3 cursor-pointer hover:text-slate-700 select-none w-[17%]"
                                    onClick={() => handleSort("created_at")}
                                >
                                    Date <SortIcon field="created_at" />
                                </th>
                                <th className="px-3 py-3 text-center w-[10%]">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {filteredAndSortedDocuments.slice(0, 10).map((doc) => (
                                <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-3 py-3">
                                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                                            Done
                                        </span>
                                    </td>
                                    <td className="px-3 py-3">
                                        <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs font-bold">
                                            {doc.transaction_type}
                                        </span>
                                    </td>
                                    <td className="px-3 py-3 overflow-hidden">
                                        <p className="text-slate-600 truncate">
                                            {doc.trading_partner || <span className="text-slate-400">—</span>}
                                        </p>
                                    </td>
                                    <td className="px-3 py-3 overflow-hidden">
                                        <p className="text-slate-600 font-medium truncate" title={doc.filename}>
                                            {doc.filename}
                                        </p>
                                    </td>
                                    <td className="px-3 py-3 text-slate-500">
                                        {formatDate(doc.created_at)}
                                    </td>
                                    <td className="px-3 py-3">
                                        <div className="flex justify-center">
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
                                                        <button
                                                            onClick={() => handleDelete(doc)}
                                                            className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                            Delete
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}

                            {filteredAndSortedDocuments.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="px-6 py-16 text-center">
                                        <div className="flex flex-col items-center gap-3">
                                            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
                                                <FileText className="w-8 h-8 text-slate-400" />
                                            </div>
                                            <div>
                                                <p className="text-slate-600 font-medium">No conversions yet</p>
                                                <p className="text-slate-400 text-sm mt-1">
                                                    Upload an EDI file above to get started
                                                </p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div >

            {/* Email Modal */}
            {
                emailModal && (
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
                )
            }
        </>
    );
}
