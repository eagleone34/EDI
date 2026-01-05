"use client";

/**
 * Dynamic component for displaying supported EDI transaction types
 * Fetches from API - automatically updates when layouts change status
 */

import { useState, useEffect } from "react";
import { API_BASE_URL } from "@/lib/api-config";

interface TransactionType {
    code: string;
    name: string;
    available: boolean;
}

interface SupportedTypesProps {
    showLegend?: boolean;
    className?: string;
}

export function SupportedTypes({ showLegend = true, className = "" }: SupportedTypesProps) {
    const [types, setTypes] = useState<TransactionType[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchTypes = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/layouts/supported-types`);
                if (response.ok) {
                    const data = await response.json();
                    setTypes(data);
                }
            } catch (error) {
                console.error("Failed to fetch supported types:", error);
                // Fallback to empty - component will show nothing
            } finally {
                setIsLoading(false);
            }
        };
        fetchTypes();
    }, []);

    // Separate available and coming soon types
    const availableTypes = types.filter(t => t.available);
    const comingSoonTypes = types.filter(t => !t.available);

    if (isLoading) {
        return (
            <div className={className}>
                <p className="text-xs text-slate-500 mb-2 font-medium">Supported Transaction Types:</p>
                <div className="flex flex-wrap gap-2">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <span key={i} className="px-2.5 py-1 bg-slate-100 rounded-md text-xs animate-pulse">
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        </span>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className={className}>
            <p className="text-xs text-slate-500 mb-2 font-medium">Supported Transaction Types:</p>
            <div className="flex flex-wrap gap-2">
                {/* Available Now */}
                {availableTypes.map((type) => (
                    <span
                        key={type.code}
                        className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium"
                    >
                        {type.code} {type.name}
                    </span>
                ))}
                {/* Coming Soon */}
                {comingSoonTypes.map((type) => (
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

// Export function to get types for dropdowns (fetch on demand)
export async function fetchSupportedTypes(): Promise<TransactionType[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/layouts/supported-types`);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error("Failed to fetch supported types:", error);
    }
    return [];
}
