"use client";

import { useState } from "react";
import { X, FormInput, Table } from "lucide-react";
import { LayoutSection } from "./VisualLayoutEditor";

interface AddSectionModalProps {
    onAdd: (section: LayoutSection) => void;
    onClose: () => void;
    existingIds: string[];
}

export default function AddSectionModal({ onAdd, onClose, existingIds }: AddSectionModalProps) {
    const [title, setTitle] = useState("");
    const [type, setType] = useState<"fields" | "table">("fields");
    const [dataSourceKey, setDataSourceKey] = useState("line_items");

    const generateId = (title: string) => {
        const base = title.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
        let id = base || "section";
        let counter = 1;
        while (existingIds.includes(id)) {
            id = `${base}_${counter}`;
            counter++;
        }
        return id;
    };

    const handleAdd = () => {
        if (!title.trim()) return;

        const section: LayoutSection = {
            id: generateId(title),
            title: title.trim(),
            type,
            visible: true,
            fields: type === "fields" ? [] : [],
            columns: type === "table" ? [] : [],
            data_source_key: type === "table" ? dataSourceKey : undefined,
        };

        onAdd(section);
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-in zoom-in-95">
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800">Add New Section</h3>
                    <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    {/* Section Title */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Section Title
                        </label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="e.g. Order Information, Line Items"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            autoFocus
                        />
                    </div>

                    {/* Section Type */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Section Type
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => setType("fields")}
                                className={`p-4 rounded-lg border-2 text-left transition-all ${type === "fields"
                                        ? "border-blue-500 bg-blue-50"
                                        : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <FormInput className={`w-6 h-6 mb-2 ${type === "fields" ? "text-blue-600" : "text-slate-400"}`} />
                                <p className="font-medium text-slate-800">Fields</p>
                                <p className="text-xs text-slate-500 mt-1">Key-value pairs</p>
                            </button>
                            <button
                                onClick={() => setType("table")}
                                className={`p-4 rounded-lg border-2 text-left transition-all ${type === "table"
                                        ? "border-purple-500 bg-purple-50"
                                        : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <Table className={`w-6 h-6 mb-2 ${type === "table" ? "text-purple-600" : "text-slate-400"}`} />
                                <p className="font-medium text-slate-800">Table</p>
                                <p className="text-xs text-slate-500 mt-1">For line items</p>
                            </button>
                        </div>
                    </div>

                    {/* Data Source Key (for tables) */}
                    {type === "table" && (
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">
                                Data Source Key
                            </label>
                            <input
                                type="text"
                                value={dataSourceKey}
                                onChange={(e) => setDataSourceKey(e.target.value)}
                                placeholder="e.g. line_items"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                            />
                            <p className="text-xs text-slate-500 mt-1">
                                The array key in your EDI data containing the rows
                            </p>
                        </div>
                    )}
                </div>

                <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-100 bg-slate-50 rounded-b-xl">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleAdd}
                        disabled={!title.trim()}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Add Section
                    </button>
                </div>
            </div>
        </div>
    );
}
