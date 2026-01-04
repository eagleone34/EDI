"use client";

import { Trash2, Eye, EyeOff, Bold } from "lucide-react";
import { LayoutField, SegmentMapping } from "./VisualLayoutEditor";

interface FieldEditorProps {
    field: LayoutField;
    onUpdate: (updates: Partial<LayoutField>) => void;
    onDelete: () => void;
    segmentMappings: SegmentMapping[];
    mode: "field" | "column";
}

const FIELD_TYPES = [
    { value: "text", label: "Text" },
    { value: "currency", label: "Currency ($)" },
    { value: "date", label: "Date" },
    { value: "number", label: "Number" },
    { value: "status", label: "Status" },
];

export default function FieldEditor({
    field,
    onUpdate,
    onDelete,
    segmentMappings,
    mode
}: FieldEditorProps) {
    // Find the EDI segment for the current key
    const currentSegment = segmentMappings.find(m => m.key === field.key);

    return (
        <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100 hover:border-slate-200 transition-colors group">
            {/* EDI Segment Badge */}
            <div className="w-16 flex-shrink-0">
                <label className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1">Segment</label>
                <div className={`px-2 py-1.5 rounded text-xs font-mono text-center ${currentSegment ? "bg-indigo-100 text-indigo-700 font-medium" : "bg-slate-100 text-slate-400"
                    }`}>
                    {currentSegment?.segment || "—"}
                </div>
            </div>

            {/* Data Key Selector */}
            <div className="flex-1 min-w-0">
                <label className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1">Data Key</label>
                {segmentMappings.length > 0 ? (
                    <select
                        value={field.key}
                        onChange={(e) => onUpdate({ key: e.target.value })}
                        className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">Select field...</option>
                        {segmentMappings.map((m) => (
                            <option key={m.key} value={m.key}>
                                {m.segment} → {m.key}
                            </option>
                        ))}
                    </select>
                ) : (
                    <input
                        type="text"
                        value={field.key}
                        onChange={(e) => onUpdate({ key: e.target.value })}
                        placeholder="e.g. po_number"
                        className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-xs"
                    />
                )}
            </div>

            {/* Display Label */}
            <div className="flex-1 min-w-0">
                <label className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1">Label</label>
                <input
                    type="text"
                    value={field.label}
                    onChange={(e) => onUpdate({ label: e.target.value })}
                    placeholder="Display name"
                    className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            {/* Format Type */}
            <div className="w-28">
                <label className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1">Format</label>
                <select
                    value={field.type}
                    onChange={(e) => onUpdate({ type: e.target.value })}
                    className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    {FIELD_TYPES.map((t) => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                </select>
            </div>

            {/* Style Toggles */}
            {mode === "field" && (
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => onUpdate({ style: field.style === "bold" ? null : "bold" })}
                        className={`p-1.5 rounded ${field.style === "bold" ? "bg-blue-100 text-blue-600" : "text-slate-400 hover:bg-slate-100"}`}
                        title="Bold"
                    >
                        <Bold className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Visibility Toggle */}
            <button
                onClick={() => onUpdate({ visible: !field.visible })}
                className={`p-1.5 rounded ${field.visible ? "text-green-600 bg-green-50" : "text-slate-400 bg-slate-100"}`}
                title={field.visible ? "Visible" : "Hidden"}
            >
                {field.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>

            {/* Delete */}
            <button
                onClick={onDelete}
                className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                title="Delete"
            >
                <Trash2 className="w-4 h-4" />
            </button>
        </div>
    );
}
