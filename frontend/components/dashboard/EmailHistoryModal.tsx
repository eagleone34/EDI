import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { X, Loader2, RefreshCw, CheckCircle, XCircle, Clock } from "lucide-react";

interface EmailLog {
    id: string;
    sent_at: string;
    recipient_email: string;
    status: string;
    error_message: string | null;
    document_id: string;
    documents?: {
        filename: string;
        transaction_type: string;
        transaction_name: string;
    };
}

interface EmailHistoryModalProps {
    routeId: string | null;
    isOpen: boolean;
    onClose: () => void;
}

export default function EmailHistoryModal({ routeId, isOpen, onClose }: EmailHistoryModalProps) {
    const [logs, setLogs] = useState<EmailLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [resendingId, setResendingId] = useState<string | null>(null);
    const [clearing, setClearing] = useState(false);

    useEffect(() => {
        if (isOpen && routeId) {
            fetchLogs();
        }
    }, [isOpen, routeId]);

    const handleClearHistory = async () => {
        if (!routeId || !confirm("Are you sure you want to clear the email history for this rule? This cannot be undone.")) return;

        setClearing(true);
        try {
            const { error } = await supabase
                .from("email_logs")
                .delete()
                .eq("route_id", routeId);

            if (error) throw error;
            setLogs([]);
        } catch (error) {
            console.error("Error clearing history:", error);
            alert("Failed to clear history.");
        } finally {
            setClearing(false);
        }
    };

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const { data, error } = await supabase
                .from("email_logs")
                .select(`
                    *,
                    documents (
                        filename,
                        transaction_type,
                        transaction_name
                    )
                `)
                .eq("route_id", routeId)
                .order("sent_at", { ascending: false })
                .limit(20);

            if (error) {
                console.error("Error fetching logs:", error);
            } else {
                setLogs(data || []);
            }
        } catch (err) {
            console.error("Failed to fetch logs:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async (log: EmailLog) => {
        if (!log.documents) return;

        setResendingId(log.id);
        try {
            const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://edi-production-d983.up.railway.app";

            const response = await fetch(`${API_BASE}/api/v1/email/send`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    to_emails: [log.recipient_email],
                    filename: log.documents.filename,
                    transaction_type: log.documents.transaction_type,
                    transaction_name: log.documents.transaction_name || log.documents.transaction_type,
                    document_id: log.document_id
                }),
            });

            if (response.ok) {
                alert("Email resent successfully!");
                fetchLogs(); // Refresh status if we were tracking new sends
            } else {
                alert("Failed to resend email.");
            }
        } catch (error) {
            console.error("Resend error:", error);
            alert("Error resending email.");
        } finally {
            setResendingId(null);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 flex flex-col max-h-[80vh]">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-slate-800">Sent Email History</h3>
                        {logs.length > 0 && (
                            <button
                                onClick={handleClearHistory}
                                disabled={clearing}
                                className="text-xs text-red-600 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition-colors"
                            >
                                {clearing ? "Clearing..." : "Clear History"}
                            </button>
                        )}
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded">
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                        </div>
                    ) : logs.length === 0 ? (
                        <div className="text-center py-8 text-slate-500">
                            <Clock className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                            <p>No email history for this rule yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {logs.map((log) => (
                                <div key={log.id} className="flex items-start justify-between p-4 bg-slate-50 rounded-lg border border-slate-100">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded ${log.status === 'sent' || log.status === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                                }`}>
                                                {log.status === 'sent' || log.status === 'success' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                                                {log.status.toUpperCase()}
                                            </span>
                                            <span className="text-xs text-slate-400">
                                                {new Date(log.sent_at).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-sm font-medium text-slate-800">{log.documents?.filename || "Unknown File"}</p>
                                        <p className="text-sm text-slate-600">to: {log.recipient_email}</p>
                                        {log.error_message && (
                                            <p className="text-xs text-red-500 mt-1">Error: {log.error_message}</p>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => handleResend(log)}
                                        disabled={resendingId === log.id}
                                        className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                        title="Resend Email"
                                    >
                                        {resendingId === log.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <RefreshCw className="w-4 h-4" />
                                        )}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
