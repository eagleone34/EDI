"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Lock, Rocket, Code, Palette, RotateCcw } from "lucide-react";
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

    const handleLock = async () => {
        try {
            let url = `${API_BASE_URL}/api/v1/layouts/${typeCode}/lock`;
            // Pass user_id for non-superadmin users
            if (user?.role !== 'superadmin' && user?.id) {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url, { method: "POST" });
            if (!response.ok) throw new Error("Failed to lock");
            const data = await response.json();
            setSaveMessage({ type: "success", text: data.message });
            fetchLayout();
        } catch (err) {
            setSaveMessage({ type: "error", text: err instanceof Error ? err.message : "Lock failed" });
        }
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

                    {isProduction && (
                        <button
                            onClick={handleLock}
                            className="px-3 py-2 border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg text-sm font-medium flex items-center gap-2"
                        >
                            <Lock className="w-4 h-4" />
                            Lock
                        </button>
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

            {/* Locked Warning */}
            {isLocked && (
                <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg text-purple-700 text-sm flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    This layout is locked and cannot be edited.
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
        </div>
    );
}
