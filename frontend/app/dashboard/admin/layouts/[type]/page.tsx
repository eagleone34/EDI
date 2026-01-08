"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Rocket, Code, Palette, RotateCcw, ChevronDown, History, Clock, ArrowUpCircle } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";
import VisualLayoutEditor, { LayoutConfig } from "@/components/admin/VisualLayoutEditor";

interface LayoutDetail {
    code: string;
    name: string;
    version_number: number;
    status: string;
    is_active: boolean;
    config_json: LayoutConfig;
    is_personal?: boolean;
}

interface SegmentMapping {
    segment: string;
    key: string;
    description: string;
}

interface VersionSummary {
    version_number: number;
    status: string;
    is_active: boolean;
    updated_at: string | null;
    created_by: string | null;
}

import { useAuth } from "@/lib/auth-context";

export default function EditLayoutPage({ params }: { params: Promise<{ type: string }> }) {
    const { user, isLoading: authLoading } = useAuth();
    const resolvedParams = use(params);
    const typeCode = resolvedParams.type;
    const router = useRouter();

    const [layout, setLayout] = useState<LayoutDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [segmentMappings, setSegmentMappings] = useState<SegmentMapping[]>([]);
    const [editorMode, setEditorMode] = useState<"visual" | "json">("visual");
    const [jsonText, setJsonText] = useState("");
    const [saveMessage, setSaveMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
    const [showHistory, setShowHistory] = useState(false);
    const [versionHistory, setVersionHistory] = useState<VersionSummary[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(false);

    useEffect(() => {
        if (!authLoading && user) {
            fetchLayout();
            fetchSegments();
        }
    }, [typeCode, authLoading, user]);

    const fetchSegments = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/segments/${typeCode}`);
            if (response.ok) {
                const data = await response.json();
                setSegmentMappings(data);
            }
        } catch (err) {
            console.error('Error fetching segments:', err);
        }
    };

    const fetchLayout = async () => {
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch layout");
            const data: LayoutDetail = await response.json();
            setLayout(data);
            setJsonText(JSON.stringify(data.config_json, null, 2));
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async (config: LayoutConfig) => {
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ config_json: config }),
            });
            if (!response.ok) throw new Error("Failed to save layout");
            const data: LayoutDetail = await response.json();
            setLayout(data);
            setJsonText(JSON.stringify(data.config_json, null, 2));
            setSaveMessage({ type: "success", text: "Layout saved successfully!" });
            setTimeout(() => setSaveMessage(null), 3000);
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Save failed" });
        }
    };

    const handleJsonSave = async () => {
        try {
            const config = JSON.parse(jsonText);
            await handleSave(config);
        } catch (err) {
            setSaveMessage({ type: "error", text: "Invalid JSON" });
        }
    };

    const handlePromote = async () => {
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}/promote`;
            // Pass user_id for non-superadmin users (they can only promote their own layouts)
            if (user?.role !== 'superadmin' && user?.id) {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url, { method: "POST" });
            if (!response.ok) throw new Error("Failed to promote");
            const data = await response.json();
            setSaveMessage({ type: "success", text: data.message });
            fetchLayout();
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Promote failed" });
        }
    };

    const handleStatusChange = async (newStatus: string) => {
        if (user?.role !== 'superadmin') return;
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/${typeCode}/status`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: newStatus }),
            });
            if (!response.ok) throw new Error("Failed to change status");
            const data = await response.json();
            setSaveMessage({ type: "success", text: data.message });
            fetchLayout();
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Status change failed" });
        }
    };

    const fetchHistory = async () => {
        setIsLoadingHistory(true);
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}/history`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch history");
            const data = await response.json();
            setVersionHistory(data);
        } catch (err) {
            console.error("Error fetching history:", err);
        } finally {
            setIsLoadingHistory(false);
        }
    };

    const handleRollback = async (versionNumber: number) => {
        if (!confirm(`Rollback to version ${versionNumber}? This will create a new DRAFT.`)) return;
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}/rollback`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ version_number: versionNumber }),
            });
            if (!response.ok) throw new Error("Failed to rollback");
            const data = await response.json();
            setSaveMessage({ type: "success", text: data.message });
            setShowHistory(false);
            fetchLayout();
            fetchHistory();
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Rollback failed" });
        }
    };

    const openHistory = () => {
        setShowHistory(true);
        fetchHistory();
    };

    const handleRestore = async () => {
        if (!confirm("Are you sure? This will delete your custom layout and revert to the system default.")) return;
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url, { method: "DELETE" });
            if (!response.ok) throw new Error("Failed to restore");

            setSaveMessage({ type: "success", text: "Restored to default!" });
            fetchLayout(); // Reload to see default
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Restore failed" });
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[600px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (error || !layout) {
        return (
            <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
                <h3 className="font-semibold">Error loading layout</h3>
                <p className="text-sm mt-1">{error}</p>
                <Link href="/dashboard/admin/layouts" className="text-blue-600 hover:underline mt-4 inline-block">
                    ← Back to layouts
                </Link>
            </div>
        );
    }

    const isDraft = layout.status === "DRAFT";
    const isProduction = layout.status === "PRODUCTION";
    const isLocked = layout.status === "LOCKED";

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard/admin/layouts" className="p-2 hover:bg-slate-100 rounded-lg">
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Edit {layout.code} Layout</h1>
                        <p className="text-slate-500">
                            {layout.name} • Version {layout.version_number}
                            <span className={`ml-2 px-2 py-0.5 text-xs font-medium rounded-full ${isLocked ? "bg-purple-100 text-purple-700" :
                                isProduction ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"
                                }`}>
                                {layout.status}
                            </span>
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Mode Toggle */}
                    <div className="flex bg-slate-100 rounded-lg p-1">
                        <button
                            onClick={() => setEditorMode("visual")}
                            className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-2 ${editorMode === "visual" ? "bg-white shadow text-blue-600" : "text-slate-600"
                                }`}
                        >
                            <Palette className="w-4 h-4" />
                            Visual
                        </button>
                        <button
                            onClick={() => setEditorMode("json")}
                            className={`px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-2 ${editorMode === "json" ? "bg-white shadow text-blue-600" : "text-slate-600"
                                }`}
                        >
                            <Code className="w-4 h-4" />
                            JSON
                        </button>
                    </div>

                    {/* History Button */}
                    <button
                        onClick={openHistory}
                        className="px-3 py-2 border border-slate-300 text-slate-600 hover:bg-slate-100 rounded-lg text-sm font-medium flex items-center gap-2"
                    >
                        <History className="w-4 h-4" />
                        History
                    </button>

                    {/* Status Dropdown - Superadmin Only */}
                    {user?.role === 'superadmin' && (
                        <div className="relative">
                            <select
                                value={layout.status}
                                onChange={(e) => handleStatusChange(e.target.value)}
                                className="px-3 py-2 pr-8 border border-slate-300 rounded-lg text-sm font-medium bg-white cursor-pointer appearance-none"
                            >
                                <option value="PRODUCTION">LIVE</option>
                                <option value="DRAFT">DRAFT</option>
                            </select>
                            <ChevronDown className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
                        </div>
                    )}
                    {layout.is_personal && (
                        <button
                            onClick={handleRestore}
                            className="px-3 py-2 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg text-sm font-medium flex items-center gap-2"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Restore Default
                        </button>
                    )}
                    {isDraft && (
                        <button
                            onClick={handlePromote}
                            className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                        >
                            <Rocket className="w-4 h-4" />
                            Promote
                        </button>
                    )}
                </div>
            </div>

            {/* Save Message */}
            {saveMessage && (
                <div className={`mb-4 p-3 rounded-lg text-sm font-medium ${saveMessage.type === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                    }`}>
                    {saveMessage.text}
                </div>
            )}



            {/* Editor */}
            <div className="flex-1 bg-white rounded-xl border border-slate-200 overflow-hidden">
                {editorMode === "visual" ? (
                    <VisualLayoutEditor
                        initialConfig={layout.config_json}
                        typeCode={layout.code}
                        typeName={layout.name}
                        onSave={handleSave}
                        segmentMappings={segmentMappings}
                    />
                ) : (
                    <div className="flex flex-col h-full">
                        <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200">
                            <span className="text-sm font-medium text-slate-600">config_json</span>
                            <button
                                onClick={handleJsonSave}
                                disabled={isLocked}
                                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg disabled:opacity-50"
                            >
                                Save JSON
                            </button>
                        </div>
                        <textarea
                            value={jsonText}
                            onChange={(e) => setJsonText(e.target.value)}
                            disabled={isLocked}
                            className="flex-1 p-4 font-mono text-sm resize-none focus:outline-none text-slate-800 bg-slate-900/5"
                            spellCheck={false}
                        />
                    </div>
                )}
            </div>

            {/* Version History Modal */}
            {showHistory && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[80vh] overflow-hidden">
                        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
                            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                                <History className="w-5 h-5 text-blue-600" />
                                Version History - {typeCode}
                            </h3>
                            <button
                                onClick={() => setShowHistory(false)}
                                className="text-slate-400 hover:text-slate-600 text-xl font-bold"
                            >
                                ×
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto max-h-[60vh]">
                            {isLoadingHistory ? (
                                <div className="flex justify-center py-8">
                                    <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                                </div>
                            ) : versionHistory.length === 0 ? (
                                <p className="text-center text-slate-500 py-8">No version history found.</p>
                            ) : (
                                <div className="space-y-3">
                                    {versionHistory.map((version) => (
                                        <div
                                            key={version.version_number}
                                            className={`flex items-center justify-between p-4 rounded-lg border ${version.is_active
                                                    ? "border-green-200 bg-green-50"
                                                    : "border-slate-200 bg-slate-50"
                                                }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${version.is_active
                                                        ? "bg-green-600 text-white"
                                                        : "bg-slate-200 text-slate-600"
                                                    }`}>
                                                    v{version.version_number}
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${version.status === "PRODUCTION" ? "bg-green-100 text-green-700" :
                                                                version.status === "DRAFT" ? "bg-amber-100 text-amber-700" :
                                                                    version.status === "ARCHIVED" ? "bg-slate-100 text-slate-500" :
                                                                        "bg-purple-100 text-purple-700"
                                                            }`}>
                                                            {version.status}
                                                        </span>
                                                        {version.is_active && (
                                                            <span className="text-xs text-green-600 font-medium">CURRENT</span>
                                                        )}
                                                    </div>
                                                    <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                                                        <Clock className="w-3 h-3" />
                                                        {version.updated_at ? new Date(version.updated_at).toLocaleString() : "Unknown"}
                                                    </p>
                                                </div>
                                            </div>

                                            {!version.is_active && version.status !== "DRAFT" && (
                                                <button
                                                    onClick={() => handleRollback(version.version_number)}
                                                    className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg flex items-center gap-1"
                                                >
                                                    <ArrowUpCircle className="w-4 h-4" />
                                                    Rollback
                                                </button>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
