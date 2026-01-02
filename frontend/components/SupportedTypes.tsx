"use client";

/**
 * Shared component for displaying supported EDI transaction types
 * Use this component on both landing page and dashboard
 * UPDATE THIS FILE when adding new transaction types
 */

// Current supported types (available now)
const CURRENT_TYPES = [
    { code: "850", name: "Purchase Order" },
    { code: "810", name: "Invoice" },
    { code: "812", name: "Credit/Debit" },
    { code: "856", name: "ASN" },
    { code: "855", name: "PO Ack" },
    { code: "997", name: "Func Ack" },
];

// Phase 2 types (coming soon)
const COMING_SOON_TYPES = [
    { code: "820", name: "Payment" },
    { code: "860", name: "PO Change" },
    { code: "861", name: "Receiving" },
    { code: "870", name: "Status" },
    { code: "830", name: "Planning" },
    { code: "852", name: "POS Data" },
    { code: "875/880", name: "Grocery" },
];

interface SupportedTypesProps {
    showLegend?: boolean;
    className?: string;
}

export function SupportedTypes({ showLegend = true, className = "" }: SupportedTypesProps) {
    return (
        <div className={className}>
            <p className="text-xs text-slate-500 mb-2 font-medium">Supported Transaction Types:</p>
            <div className="flex flex-wrap gap-2">
                {/* Current - Available Now */}
                {CURRENT_TYPES.map((type) => (
                    <span
                        key={type.code}
                        className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium"
                    >
                        {type.code} {type.name}
                    </span>
                ))}
                {/* Phase 2 - Coming Soon */}
                {COMING_SOON_TYPES.map((type) => (
                    <span
                        key={type.code}
                        className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium"
                    >
                        {type.code} {type.name}
                    </span>
                ))}
            </div>
            {showLegend && (
                <p className="text-xs text-slate-400 mt-2">
                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-1"></span> Available now
                    <span className="inline-block w-2 h-2 bg-slate-300 rounded-full ml-3 mr-1"></span> Coming soon
                </p>
            )}
        </div>
    );
}

// Export the types arrays for use in dropdowns, etc.
export { CURRENT_TYPES, COMING_SOON_TYPES };
