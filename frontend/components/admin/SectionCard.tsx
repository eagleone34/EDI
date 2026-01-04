"use client";

import { useState } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, ChevronDown, ChevronRight, Trash2, Plus, Table, FormInput, X } from "lucide-react";
import FieldEditor from "./FieldEditor";
import { LayoutSection, LayoutField, LayoutColumn, SegmentMapping } from "./VisualLayoutEditor";

interface SectionCardProps {
    section: LayoutSection;
    onUpdate: (updates: Partial<LayoutSection>) => void;
    onDelete: () => void;
    segmentMappings: SegmentMapping[];
}

export default function SectionCard({ section, onUpdate, onDelete, segmentMappings }: SectionCardProps) {
    const [isExpanded, setIsExpanded] = useState(true);
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [showSegmentPicker, setShowSegmentPicker] = useState(false);
    const [pickerMode, setPickerMode] = useState<"field" | "column">("field");

    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: section.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    // Get already used keys in this section
    const usedKeys = section.type === "fields"
        ? section.fields.map(f => f.key)
        : section.columns.map(c => c.key);

    // Get available segments (all segments, even if some are already used - show as disabled)
    const getAvailableSegments = () => {
        return segmentMappings.map(m => ({
            ...m,
            isUsed: usedKeys.includes(m.key)
        }));
    };

    const openSegmentPicker = (mode: "field" | "column") => {
        setPickerMode(mode);
        setShowSegmentPicker(true);
    };

    const addFieldFromSegment = (segment: SegmentMapping) => {
        const newField: LayoutField = {
            key: segment.key,
            label: segment.description || segment.key,
            type: inferType(segment.key),
            visible: true,
            style: null,
            format_string: null,
        };
        onUpdate({ fields: [...section.fields, newField] });
        setShowSegmentPicker(false);
    };

    const addColumnFromSegment = (segment: SegmentMapping) => {
        const newColumn: LayoutColumn = {
            key: segment.key,
            label: segment.description || segment.key,
            type: inferType(segment.key),
            visible: true,
        };
        onUpdate({ columns: [...section.columns, newColumn] });
        setShowSegmentPicker(false);
    };

    // Infer field type from key name
    const inferType = (key: string): string => {
        const lowerKey = key.toLowerCase();
        if (lowerKey.includes("date")) return "date";
        if (lowerKey.includes("amount") || lowerKey.includes("price") || lowerKey.includes("total") || lowerKey.includes("cost")) return "currency";
        if (lowerKey.includes("quantity") || lowerKey.includes("count") || lowerKey.includes("number") && !lowerKey.includes("po_number")) return "number";
        if (lowerKey.includes("status")) return "status";
        return "text";
    };

    const updateField = (index: number, updates: Partial<LayoutField>) => {
        const newFields = [...section.fields];
        newFields[index] = { ...newFields[index], ...updates };
        onUpdate({ fields: newFields });
    };

    const deleteField = (index: number) => {
        onUpdate({ fields: section.fields.filter((_, i) => i !== index) });
    };

    const updateColumn = (index: number, updates: Partial<LayoutColumn>) => {
        const newColumns = [...section.columns];
        newColumns[index] = { ...newColumns[index], ...updates };
        onUpdate({ columns: newColumns });
    };

    const deleteColumn = (index: number) => {
        onUpdate({ columns: section.columns.filter((_, i) => i !== index) });
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className={`bg-white rounded-xl border ${isDragging ? "border-blue-400 shadow-lg" : "border-slate-200"} overflow-hidden`}
        >
            {/* Section Header */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
                <button
                    {...attributes}
                    {...listeners}
                    className="p-1 text-slate-400 hover:text-slate-600 cursor-grab active:cursor-grabbing"
                >
                    <GripVertical className="w-4 h-4" />
                </button>

                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="p-1 text-slate-400 hover:text-slate-600"
                >
                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>

                <div className={`p-1.5 rounded ${section.type === "table" ? "bg-purple-100" : "bg-blue-100"}`}>
                    {section.type === "table" ? (
                        <Table className="w-4 h-4 text-purple-600" />
                    ) : (
                        <FormInput className="w-4 h-4 text-blue-600" />
                    )}
                </div>

                {isEditingTitle ? (
                    <input
                        type="text"
                        value={section.title}
                        onChange={(e) => onUpdate({ title: e.target.value })}
                        onBlur={() => setIsEditingTitle(false)}
                        onKeyDown={(e) => e.key === "Enter" && setIsEditingTitle(false)}
                        className="flex-1 px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
                        autoFocus
                    />
                ) : (
                    <span
                        onClick={() => setIsEditingTitle(true)}
                        className="flex-1 text-sm font-semibold text-slate-800 cursor-pointer hover:text-blue-600"
                    >
                        {section.title}
                    </span>
                )}

                <span className={`text-xs px-2 py-0.5 rounded-full ${section.visible ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                    {section.visible ? "Visible" : "Hidden"}
                </span>

                <button
                    onClick={() => onUpdate({ visible: !section.visible })}
                    className="text-xs text-slate-500 hover:text-slate-700"
                >
                    {section.visible ? "Hide" : "Show"}
                </button>

                <button
                    onClick={onDelete}
                    className="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>

            {/* Section Content */}
            {isExpanded && (
                <div className="p-4 space-y-3">
                    {section.type === "fields" ? (
                        <>
                            {section.fields.map((field, index) => (
                                <FieldEditor
                                    key={index}
                                    field={field}
                                    onUpdate={(updates) => updateField(index, updates)}
                                    onDelete={() => deleteField(index)}
                                    segmentMappings={segmentMappings}
                                    mode="field"
                                />
                            ))}
                            <button
                                onClick={() => openSegmentPicker("field")}
                                className="w-full py-2 border-2 border-dashed border-slate-200 rounded-lg text-slate-400 hover:border-blue-300 hover:text-blue-500 text-sm flex items-center justify-center gap-2 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Add Field from Segment
                            </button>
                        </>
                    ) : (
                        <>
                            <div className="text-xs text-slate-500 mb-2">Table Columns:</div>
                            {section.columns.map((column, index) => (
                                <FieldEditor
                                    key={index}
                                    field={column as unknown as LayoutField}
                                    onUpdate={(updates) => updateColumn(index, updates as Partial<LayoutColumn>)}
                                    onDelete={() => deleteColumn(index)}
                                    segmentMappings={segmentMappings}
                                    mode="column"
                                />
                            ))}
                            <button
                                onClick={() => openSegmentPicker("column")}
                                className="w-full py-2 border-2 border-dashed border-slate-200 rounded-lg text-slate-400 hover:border-purple-300 hover:text-purple-500 text-sm flex items-center justify-center gap-2 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Add Column from Segment
                            </button>
                        </>
                    )}
                </div>
            )}

            {/* Segment Picker Modal */}
            {showSegmentPicker && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[80vh] flex flex-col">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
                            <h3 className="font-semibold text-slate-800">
                                Select EDI Segment to Add
                            </h3>
                            <button
                                onClick={() => setShowSegmentPicker(false)}
                                className="p-1 text-slate-400 hover:text-slate-600 rounded"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 overflow-y-auto flex-1">
                            {segmentMappings.length === 0 ? (
                                <p className="text-sm text-slate-500 text-center py-8">
                                    No segment mappings available for this transaction type.
                                </p>
                            ) : (
                                <div className="space-y-2">
                                    {getAvailableSegments().map((segment) => (
                                        <button
                                            key={segment.segment + segment.key}
                                            onClick={() => {
                                                if (!segment.isUsed) {
                                                    pickerMode === "field"
                                                        ? addFieldFromSegment(segment)
                                                        : addColumnFromSegment(segment);
                                                }
                                            }}
                                            disabled={segment.isUsed}
                                            className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${segment.isUsed
                                                    ? "bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed"
                                                    : "bg-white border-slate-200 hover:border-blue-300 hover:bg-blue-50 cursor-pointer"
                                                }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className={`font-mono text-xs px-2 py-1 rounded ${segment.isUsed
                                                        ? "bg-slate-200 text-slate-500"
                                                        : "bg-indigo-100 text-indigo-700"
                                                    }`}>
                                                    {segment.segment}
                                                </span>
                                                <div className="flex-1">
                                                    <div className={`font-medium text-sm ${segment.isUsed ? "text-slate-400" : "text-slate-800"}`}>
                                                        {segment.description}
                                                    </div>
                                                    <div className="text-xs text-slate-400 font-mono">{segment.key}</div>
                                                </div>
                                                {segment.isUsed && (
                                                    <span className="text-xs text-slate-400">Already added</span>
                                                )}
                                            </div>
                                        </button>
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
