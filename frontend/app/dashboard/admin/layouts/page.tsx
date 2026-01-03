"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ChevronRight, Loader2, CheckCircle2, FileEdit, LayoutGrid, Users } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";
import { useAuth } from "@/lib/auth-context";

interface LayoutSummary {
    code: string;
    name: string;
    version_number: number;
    status: string;
    is_active: boolean;
}

export default function AdminLayoutsPage() {
    const { user, isLoading: authLoading } = useAuth();
    const [layouts, setLayouts] = useState<LayoutSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!authLoading && user) {
            fetchLayouts();
        }
    }, [authLoading, user]);

    const fetchLayouts = async () => {
        try {
            let url = `${API_BASE_URL}/api/v1/layouts`;
            if (user?.role === 'user') {
                url += `?user_id=${user.id}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch layouts");
            const data = await response.json();
            setLayouts(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setIsLoading(false);
        }
    };

    const getStatusBadge = (status: string, isActive: boolean) => {
        if (status === "PRODUCTION" && isActive) {
            return (
                <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                    <CheckCircle2 className="w-3 h-3" />
                    LIVE
                </span>
            );
        }
        if (status === "DRAFT") {
            return (
                <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-amber-100 text-amber-700">
                    <FileEdit className="w-3 h-3" />
                    DRAFT
                </span>
            );
        }
        return (
            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-600">
                {status}
            </span>
        );
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
                <h3 className="font-semibold">Error loading layouts</h3>
                <p className="text-sm mt-1">{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
                        <LayoutGrid className="w-7 h-7 text-blue-600" />
                        {user?.role === 'superadmin' ? 'Global Layout Manager' : 'My Layouts'}
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Configure the HTML/PDF output format for each EDI transaction type.
                    </p>
                </div>
                {user?.role === 'superadmin' && (
                    <Link
                        href="/dashboard/admin/users"
                        className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors font-medium"
                    >
                        <Users className="w-4 h-4" />
                        Manage Users
                    </Link>
                )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-4">
                    <p className="text-3xl font-bold text-slate-800">{layouts.length}</p>
                    <p className="text-sm text-slate-500">Transaction Types</p>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-4">
                    <p className="text-3xl font-bold text-green-600">
                        {layouts.filter(l => l.status === "PRODUCTION").length}
                    </p>
                    <p className="text-sm text-slate-500">Live Layouts</p>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-4">
                    <p className="text-3xl font-bold text-amber-600">
                        {layouts.filter(l => l.status === "DRAFT").length}
                    </p>
                    <p className="text-sm text-slate-500">Draft Versions</p>
                </div>
            </div>

            {/* Layout Cards */}
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div className="grid grid-cols-1 divide-y divide-slate-100">
                    {layouts.map((layout) => (
                        <Link
                            key={layout.code}
                            href={`/dashboard/admin/layouts/${layout.code}`}
                            className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors group"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                                    {layout.code}
                                </div>
                                <div>
                                    <h3 className="font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">
                                        {layout.name}
                                    </h3>
                                    <p className="text-sm text-slate-500">
                                        Version {layout.version_number}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                {getStatusBadge(layout.status, layout.is_active)}
                                <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-blue-600 transition-colors" />
                            </div>
                        </Link>
                    ))}
                </div>
            </div>

            {
                layouts.length === 0 && (
                    <div className="text-center py-12 text-slate-500">
                        No layouts configured yet. Seed the database to get started.
                    </div>
                )
            }
        </div >
    );
}
