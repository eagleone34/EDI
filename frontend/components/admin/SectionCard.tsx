"use client";

import { useState } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, ChevronDown, ChevronRight, Trash2, Plus, Table, FormInput } from "lucide-react";
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

    const addField = () => {
        const newField: LayoutField = {
            key: "",
            label: "New Field",
            type: "text",
            visible: true,
            style: null,
            format_string: null,
        };
        onUpdate({ fields: [...section.fields, newField] });
    };

    const updateField = (index: number, updates: Partial<LayoutField>) => {
        const newFields = [...section.fields];
        newFields[index] = { ...newFields[index], ...updates };
        onUpdate({ fields: newFields });
    };

    const deleteField = (index: number) => {
        onUpdate({ fields: section.fields.filter((_, i) => i !== index) });
    };

    const addColumn = () => {
        const newColumn: LayoutColumn = {
            key: "",
            label: "New Column",
            type: "text",
            visible: true,
        };
        onUpdate({ columns: [...section.columns, newColumn] });
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
                                onClick={addField}
                                className="w-full py-2 border-2 border-dashed border-slate-200 rounded-lg text-slate-400 hover:border-blue-300 hover:text-blue-500 text-sm flex items-center justify-center gap-2 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Add Field
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
                                onClick={addColumn}
                                className="w-full py-2 border-2 border-dashed border-slate-200 rounded-lg text-slate-400 hover:border-purple-300 hover:text-purple-500 text-sm flex items-center justify-center gap-2 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Add Column
                            </button>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
