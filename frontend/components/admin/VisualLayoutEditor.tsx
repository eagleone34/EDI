"use client";

import { useState, useCallback, useEffect } from "react";
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragEndEvent,
} from "@dnd-kit/core";
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Plus, Eye, EyeOff } from "lucide-react";
import SectionCard from "./SectionCard";
import LivePreview from "./LivePreview";
import AddSectionModal from "./AddSectionModal";

export interface LayoutField {
    key: string;
    label: string;
    type: string;
    style?: string | null;
    visible: boolean;
    format_string?: string | null;
}

export interface LayoutColumn {
    key: string;
    label: string;
    width?: string;
    type: string;
    visible: boolean;
}

export interface LayoutSection {
    id: string;
    title: string;
    type: "fields" | "table";
    visible: boolean;
    fields: LayoutField[];
    columns: LayoutColumn[];
    data_source_key?: string;
}

export interface LayoutConfig {
    title_format: string;
    theme_color: string;
    sections: LayoutSection[];
}

interface VisualLayoutEditorProps {
    initialConfig: LayoutConfig;
    typeCode: string;
    typeName: string;
    onSave: (config: LayoutConfig) => Promise<void>;
    availableFields?: string[];
}

export default function VisualLayoutEditor({
    initialConfig,
    typeCode,
    typeName,
    onSave,
    availableFields = [],
}: VisualLayoutEditorProps) {
    const [config, setConfig] = useState<LayoutConfig>(initialConfig);
    const [showPreview, setShowPreview] = useState(true);
    const [showAddSection, setShowAddSection] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        if (over && active.id !== over.id) {
            setConfig((prev) => {
                const oldIndex = prev.sections.findIndex((s) => s.id === active.id);
                const newIndex = prev.sections.findIndex((s) => s.id === over.id);
                return {
                    ...prev,
                    sections: arrayMove(prev.sections, oldIndex, newIndex),
                };
            });
        }
    };

    const updateSection = useCallback((sectionId: string, updates: Partial<LayoutSection>) => {
        setConfig((prev) => ({
            ...prev,
            sections: prev.sections.map((s) =>
                s.id === sectionId ? { ...s, ...updates } : s
            ),
        }));
    }, []);

    const deleteSection = useCallback((sectionId: string) => {
        setConfig((prev) => ({
            ...prev,
            sections: prev.sections.filter((s) => s.id !== sectionId),
        }));
    }, []);

    const addSection = useCallback((section: LayoutSection) => {
        setConfig((prev) => ({
            ...prev,
            sections: [...prev.sections, section],
        }));
        setShowAddSection(false);
    }, []);

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await onSave(config);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Toolbar */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-white">
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowAddSection(true)}
                        className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Add Section
                    </button>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowPreview(!showPreview)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${showPreview
                                ? "bg-indigo-100 text-indigo-700"
                                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                            }`}
                    >
                        {showPreview ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                        {showPreview ? "Preview On" : "Preview Off"}
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium disabled:opacity-50"
                    >
                        {isSaving ? "Saving..." : "Save Changes"}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className={`flex-1 flex ${showPreview ? "gap-6" : ""} p-6 bg-slate-50 overflow-hidden`}>
                {/* Left: Section Editor */}
                <div className={`${showPreview ? "w-1/2" : "w-full"} overflow-y-auto pr-2`}>
                    <div className="space-y-4">
                        <DndContext
                            sensors={sensors}
                            collisionDetection={closestCenter}
                            onDragEnd={handleDragEnd}
                        >
                            <SortableContext
                                items={config.sections.map((s) => s.id)}
                                strategy={verticalListSortingStrategy}
                            >
                                {config.sections.map((section) => (
                                    <SectionCard
                                        key={section.id}
                                        section={section}
                                        onUpdate={(updates) => updateSection(section.id, updates)}
                                        onDelete={() => deleteSection(section.id)}
                                        availableFields={availableFields}
                                    />
                                ))}
                            </SortableContext>
                        </DndContext>

                        {config.sections.length === 0 && (
                            <div className="text-center py-12 text-slate-400">
                                No sections yet. Click "Add Section" to start building your layout.
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Live Preview */}
                {showPreview && (
                    <div className="w-1/2 bg-white rounded-xl border border-slate-200 overflow-hidden">
                        <LivePreview config={config} typeCode={typeCode} typeName={typeName} />
                    </div>
                )}
            </div>

            {/* Add Section Modal */}
            {showAddSection && (
                <AddSectionModal
                    onAdd={addSection}
                    onClose={() => setShowAddSection(false)}
                    existingIds={config.sections.map((s) => s.id)}
                />
            )}
        </div>
    );
}
