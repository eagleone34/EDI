"use client";

import { useState, useEffect, useMemo } from "react";
import { RefreshCw, Upload } from "lucide-react";
import { LayoutConfig } from "./VisualLayoutEditor";

interface LivePreviewProps {
    config: LayoutConfig;
    typeCode: string;
    typeName: string;
}

// Sample data for preview
const SAMPLE_DATA: Record<string, Record<string, unknown>> = {
    "812": {
        credit_debit_number: "CD-SAMPLE-001",
        date: "2026-01-02",
        purchase_order_number: "PO-123456",
        vendor_name: "Acme Corp",
        buyer_name: "Walmart Inc.",
        adjustment_reason: "Price Discrepancy",
        total_amount: "1,250.00",
        line_items: [
            { assigned_id: "ITEM-001", description: "Widget A - Price Adjustment", adjustment_amount: "500.00", quantity: "10" },
            { assigned_id: "ITEM-002", description: "Widget B - Shortage", adjustment_amount: "750.00", quantity: "15" },
        ],
    },
    default: {
        po_number: "PO-SAMPLE-001",
        date: "2026-01-02",
        vendor_name: "Sample Vendor",
        total: "5,000.00",
        line_items: [
            { product_id: "SKU-001", description: "Sample Product", quantity: "100", unit_price: "50.00" },
        ],
    },
};

export default function LivePreview({ config, typeCode, typeName }: LivePreviewProps) {
    const [isRefreshing, setIsRefreshing] = useState(false);

    const sampleData = SAMPLE_DATA[typeCode] || SAMPLE_DATA.default;

    const previewHtml = useMemo(() => {
        return generatePreviewHtml(config, sampleData, typeName);
    }, [config, sampleData, typeName]);

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => setIsRefreshing(false), 300);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Preview Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200">
                <span className="text-sm font-medium text-slate-600">Live Preview</span>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleRefresh}
                        className={`p-1.5 text-slate-400 hover:text-slate-600 rounded ${isRefreshing ? "animate-spin" : ""}`}
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Preview Content */}
            <div className="flex-1 overflow-auto p-4 bg-white">
                <div
                    className="preview-container"
                    dangerouslySetInnerHTML={{ __html: previewHtml }}
                />
            </div>

            {/* Sample Data Info */}
            <div className="px-4 py-2 bg-amber-50 border-t border-amber-100 text-xs text-amber-700">
                📋 Showing preview with sample data. Upload a real EDI file to see actual content.
            </div>
        </div>
    );
}

function generatePreviewHtml(config: LayoutConfig, data: Record<string, unknown>, typeName: string): string {
    const styles = `
        <style>
            .preview-doc { font-family: system-ui, -apple-system, sans-serif; max-width: 600px; }
            .preview-header { padding: 16px; background: linear-gradient(135deg, #3b82f6, #6366f1); color: white; border-radius: 12px 12px 0 0; }
            .preview-title { font-size: 18px; font-weight: 700; margin: 0; }
            .preview-subtitle { font-size: 12px; opacity: 0.8; margin-top: 4px; }
            .preview-section { padding: 16px; border: 1px solid #e2e8f0; border-top: none; }
            .preview-section:last-child { border-radius: 0 0 12px 12px; }
            .preview-section-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }
            .preview-field { display: flex; padding: 4px 0; }
            .preview-field-label { color: #64748b; font-size: 13px; width: 140px; flex-shrink: 0; }
            .preview-field-value { color: #1e293b; font-size: 13px; font-weight: 500; }
            .preview-field-value.bold { font-weight: 700; }
            .preview-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
            .preview-table th { background: #f1f5f9; padding: 8px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }
            .preview-table td { padding: 8px; border-bottom: 1px solid #e2e8f0; color: #334155; }
            .preview-table tr:hover td { background: #f8fafc; }
        </style>
    `;

    let html = `${styles}<div class="preview-doc">`;

    // Header
    const refNumber = (data.credit_debit_number || data.po_number || "001") as string;
    html += `
        <div class="preview-header">
            <h1 class="preview-title">${typeName}</h1>
            <p class="preview-subtitle">#${refNumber}</p>
        </div>
    `;

    // Sections
    for (const section of config.sections) {
        if (!section.visible) continue;

        html += `<div class="preview-section">`;
        html += `<div class="preview-section-title">${section.title}</div>`;

        if (section.type === "fields") {
            for (const field of section.fields) {
                if (!field.visible) continue;
                const value = data[field.key] ?? "—";
                const boldClass = field.style === "bold" ? "bold" : "";
                html += `
                    <div class="preview-field">
                        <span class="preview-field-label">${field.label}</span>
                        <span class="preview-field-value ${boldClass}">${formatValue(value, field.type)}</span>
                    </div>
                `;
            }
        } else if (section.type === "table") {
            const items = (data[section.data_source_key || "line_items"] as Record<string, unknown>[]) || [];
            html += `<table class="preview-table"><thead><tr>`;
            for (const col of section.columns) {
                if (!col.visible) continue;
                html += `<th>${col.label}</th>`;
            }
            html += `</tr></thead><tbody>`;
            for (const item of items) {
                html += `<tr>`;
                for (const col of section.columns) {
                    if (!col.visible) continue;
                    html += `<td>${formatValue(item[col.key], col.type)}</td>`;
                }
                html += `</tr>`;
            }
            html += `</tbody></table>`;
        }

        html += `</div>`;
    }

    html += `</div>`;
    return html;
}

function formatValue(value: unknown, type: string): string {
    if (value === undefined || value === null) return "—";
    const strValue = String(value);

    switch (type) {
        case "currency":
            return `$${strValue}`;
        case "date":
            try {
                return new Date(strValue).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
            } catch {
                return strValue;
            }
        default:
            return strValue;
    }
}
