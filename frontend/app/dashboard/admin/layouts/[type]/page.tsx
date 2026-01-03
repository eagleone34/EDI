"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Save, Loader2, CheckCircle2, AlertCircle, RotateCcw, Rocket, Lock, X } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";

interface LayoutDetail {
    code: string;
    name: string;
    version_number: number;
    status: string;
    is_active: boolean;
    config_json: Record<string, unknown>;
}

export default function EditLayoutPage({ params }: { params: Promise<{ type: string }> }) {
    const resolvedParams = use(params);
    const typeCode = resolvedParams.type;
    const router = useRouter();

    const [layout, setLayout] = useState<LayoutDetail | null>(null);
    const [jsonText, setJsonText] = useState("");
    const [originalJson, setOriginalJson] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isPromoting, setIsPromoting] = useState(false);
    const [isLocking, setIsLocking] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");
    const [jsonError, setJsonError] = useState<string | null>(null);
    const [showPromoteDialog, setShowPromoteDialog] = useState(false);
    const [showLockDialog, setShowLockDialog] = useState(false);
    const [actionMessage, setActionMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    useEffect(() => {
        fetchLayout();
    }, [typeCode]);

    const fetchLayout = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/${typeCode}`);
            if (!response.ok) throw new Error("Failed to fetch layout");
            const data: LayoutDetail = await response.json();
            setLayout(data);
            const prettyJson = JSON.stringify(data.config_json, null, 2);
            setJsonText(prettyJson);
            setOriginalJson(prettyJson);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setIsLoading(false);
        }
    };

    const validateJson = (text: string): boolean => {
        try {
            JSON.parse(text);
            setJsonError(null);
            return true;
        } catch (e) {
            setJsonError(e instanceof Error ? e.message : "Invalid JSON");
            return false;
        }
    };

    const handleJsonChange = (text: string) => {
        setJsonText(text);
        validateJson(text);
        setSaveStatus("idle");
    };

    const handleSave = async () => {
        if (!validateJson(jsonText)) return;

        setIsSaving(true);
        setSaveStatus("idle");

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/${typeCode}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ config_json: JSON.parse(jsonText) }),
            });

            if (!response.ok) throw new Error("Failed to save layout");

            const data: LayoutDetail = await response.json();
            setLayout(data);
            setOriginalJson(jsonText);
            setSaveStatus("success");
            setTimeout(() => setSaveStatus("idle"), 3000);
        } catch (err) {
            setSaveStatus("error");
            setError(err instanceof Error ? err.message : "Save failed");
        } finally {
            setIsSaving(false);
        }
    };

    const handlePromote = async () => {
        setIsPromoting(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/${typeCode}/promote`, {
                method: "POST",
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to promote");
            }
            const data = await response.json();
            setActionMessage({ type: "success", text: data.message });
            setShowPromoteDialog(false);
            // Refresh layout data
            fetchLayout();
            setTimeout(() => setActionMessage(null), 5000);
        } catch (err) {
            setActionMessage({ type: "error", text: err instanceof Error ? err.message : "Promote failed" });
        } finally {
            setIsPromoting(false);
        }
    };

    const handleLock = async () => {
        setIsLocking(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/layouts/${typeCode}/lock`, {
                method: "POST",
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to lock");
            }
            const data = await response.json();
            setActionMessage({ type: "success", text: data.message });
            setShowLockDialog(false);
            fetchLayout();
            setTimeout(() => setActionMessage(null), 5000);
        } catch (err) {
            setActionMessage({ type: "error", text: err instanceof Error ? err.message : "Lock failed" });
        } finally {
            setIsLocking(false);
        }
    };

    const handleReset = () => {
        setJsonText(originalJson);
        setJsonError(null);
        setSaveStatus("idle");
    };

    const hasChanges = jsonText !== originalJson;
    const isDraft = layout?.status === "DRAFT";
    const isProduction = layout?.status === "PRODUCTION";
    const isLocked = layout?.status === "LOCKED";

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (error && !layout) {
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

    const getStatusBadgeStyle = (status: string) => {
        switch (status) {
            case "PRODUCTION": return "bg-green-100 text-green-700";
            case "DRAFT": return "bg-amber-100 text-amber-700";
            case "LOCKED": return "bg-purple-100 text-purple-700";
            default: return "bg-slate-100 text-slate-600";
        }
    };

    return (
        <div className="space-y-6">
            {/* Action Message Banner */}
            {actionMessage && (
                <div className={`p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-top ${actionMessage.type === "success" ? "bg-green-50 border border-green-200 text-green-700" : "bg-red-50 border border-red-200 text-red-700"
                    }`}>
                    {actionMessage.type === "success" ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    <span className="font-medium">{actionMessage.text}</span>
                </div>
            )}

            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard/admin/layouts" className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">
                            Edit {layout?.code} Layout
                        </h1>
                        <p className="text-slate-500">
                            {layout?.name} • Version {layout?.version_number}
                            <span className={`ml-2 inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${getStatusBadgeStyle(layout?.status || "")}`}>
                                {layout?.status === "LOCKED" && <Lock className="w-3 h-3" />}
                                {layout?.status}
                            </span>
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Lock Button - Only for PRODUCTION */}
                    {isProduction && (
                        <button
                            onClick={() => setShowLockDialog(true)}
                            className="px-4 py-2 border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg font-medium flex items-center gap-2 transition-colors"
                        >
                            <Lock className="w-4 h-4" />
                            Lock Version
                        </button>
                    )}

                    {/* Promote Button - Only for DRAFT */}
                    {isDraft && (
                        <button
                            onClick={() => setShowPromoteDialog(true)}
                            className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 rounded-lg font-medium flex items-center gap-2 transition-all shadow-sm"
                        >
                            <Rocket className="w-4 h-4" />
                            Promote to Production
                        </button>
                    )}

                    {hasChanges && (
                        <button
                            onClick={handleReset}
                            className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium flex items-center gap-2 transition-colors"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reset
                        </button>
                    )}

                    {!isLocked && (
                        <button
                            onClick={handleSave}
                            disabled={isSaving || !!jsonError || !hasChanges}
                            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all ${saveStatus === "success"
                                    ? "bg-green-600 text-white"
                                    : isSaving || !!jsonError || !hasChanges
                                        ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                                        : "bg-blue-600 hover:bg-blue-700 text-white"
                                }`}
                        >
                            {isSaving ? (
                                <><Loader2 className="w-4 h-4 animate-spin" />Saving...</>
                            ) : saveStatus === "success" ? (
                                <><CheckCircle2 className="w-4 h-4" />Saved!</>
                            ) : (
                                <><Save className="w-4 h-4" />Save Draft</>
                            )}
                        </button>
                    )}
                </div>
            </div>

            {/* Locked Warning */}
            {isLocked && (
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl text-purple-700 flex items-center gap-3">
                    <Lock className="w-5 h-5" />
                    <div>
                        <p className="font-medium">This layout is locked</p>
                        <p className="text-sm text-purple-600">Locked versions are immutable and cannot be edited. Create a new draft to make changes.</p>
                    </div>
                </div>
            )}

            {/* JSON Error Banner */}
            {jsonError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="font-medium">Invalid JSON</p>
                        <p className="text-sm mt-1 font-mono">{jsonError}</p>
                    </div>
                </div>
            )}

            {/* Editor */}
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-600">config_json</span>
                    <span className="text-xs text-slate-400">{jsonText.split("\n").length} lines</span>
                </div>
                <textarea
                    value={jsonText}
                    onChange={(e) => handleJsonChange(e.target.value)}
                    disabled={isLocked}
                    className={`w-full h-[600px] p-4 font-mono text-sm resize-none focus:outline-none text-slate-800 ${isLocked ? "bg-slate-100 cursor-not-allowed" : "bg-slate-900/5"
                        }`}
                    spellCheck={false}
                />
            </div>

            {/* Help Text */}
            <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl text-blue-700 text-sm">
                <p className="font-medium mb-2">Layout Configuration Guide</p>
                <ul className="list-disc list-inside space-y-1 text-blue-600">
                    <li><code className="bg-blue-100 px-1 rounded">sections</code> - Array of section definitions</li>
                    <li><code className="bg-blue-100 px-1 rounded">fields</code> - Key-value mappings to display</li>
                    <li><code className="bg-blue-100 px-1 rounded">columns</code> - Table column definitions</li>
                    <li><code className="bg-blue-100 px-1 rounded">title_format</code> - Document title template</li>
                </ul>
            </div>

            {/* Promote Confirmation Dialog */}
            {showPromoteDialog && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-in zoom-in-95">
                        <div className="p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                                    <Rocket className="w-5 h-5 text-green-600" />
                                </div>
                                <h3 className="text-lg font-bold text-slate-800">Promote to Production</h3>
                            </div>
                            <p className="text-slate-600 mb-6">
                                This will make <strong>Version {layout?.version_number}</strong> the active PRODUCTION layout for <strong>{layout?.code}</strong>.
                                The current production version will be archived.
                            </p>
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowPromoteDialog(false)}
                                    className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handlePromote}
                                    disabled={isPromoting}
                                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2"
                                >
                                    {isPromoting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
                                    {isPromoting ? "Promoting..." : "Promote Now"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Lock Confirmation Dialog */}
            {showLockDialog && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-in zoom-in-95">
                        <div className="p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                                    <Lock className="w-5 h-5 text-purple-600" />
                                </div>
                                <h3 className="text-lg font-bold text-slate-800">Lock This Version</h3>
                            </div>
                            <p className="text-slate-600 mb-2">
                                Locking <strong>Version {layout?.version_number}</strong> will make it <strong>immutable</strong>.
                            </p>
                            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm mb-6">
                                ⚠️ This action cannot be undone. Locked versions cannot be edited.
                            </div>
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowLockDialog(false)}
                                    className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleLock}
                                    disabled={isLocking}
                                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium flex items-center gap-2"
                                >
                                    {isLocking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                                    {isLocking ? "Locking..." : "Lock Version"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
