"use client";

import { useAuth } from "@/lib/auth-context";
import TransactionsTable from "@/components/dashboard/TransactionsTable";

export default function DashboardPage() {
    const { user } = useAuth();
    const displayName = user?.email?.split("@")[0] || "User";

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
                <p className="text-slate-500 mt-1">Welcome back, {displayName}.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Total Conversions</p>
                        <p className="text-3xl font-bold text-slate-800 mt-2">0</p>
                        <p className="text-xs text-slate-400 mt-2 font-medium flex items-center">
                            Convert your first file to get started
                        </p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-purple-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Time Saved</p>
                        <p className="text-3xl font-bold text-slate-800 mt-2">0h</p>
                        <p className="text-xs text-purple-600 mt-2 font-medium flex items-center">
                            Based on manual entry time
                        </p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Plan</p>
                        <p className="text-3xl font-bold text-slate-800 mt-2">Free</p>
                        <p className="text-xs text-emerald-600 mt-2 font-medium flex items-center">
                            5 conversions/month
                        </p>
                    </div>
                </div>
            </div>

            {/* Transactions */}
            <TransactionsTable />
        </div>
    );
}
