"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "@/lib/api-config";
import {
    Shield, Users, Activity, Server, ArrowLeft, Loader2,
    TrendingUp, FileText, Clock, UserPlus, BarChart3,
    AlertTriangle, CheckCircle, Database, Mail, RefreshCw
} from "lucide-react";

// ============================================================================
// Types
// ============================================================================

interface OverviewStats {
    total_users: number;
    active_users_7d: number;
    active_users_30d: number;
    total_conversions: number;
    conversions_today: number;
    conversions_week: number;
    conversions_month: number;
    new_users_7d: number;
}

interface ConversionsByType {
    transaction_type: string;
    count: number;
    percentage: number;
}

interface ActivityItem {
    id: number;
    user_id: string | null;
    user_email: string | null;
    action: string;
    details: Record<string, unknown>;
    created_at: string;
}

interface SystemHealth {
    database_connected: boolean;
    total_users: number;
    total_conversions: number;
    email_errors_24h: number;
    recent_errors: Array<{
        id: number;
        user_id: string | null;
        snippet: string;
        error: string;
        created_at: string | null;
    }>;
}

interface DailyConversion {
    date: string;
    count: number;
}

// ============================================================================
// Main Component
// ============================================================================

export default function AdminHubPage() {
    const { user, isLoading: authLoading } = useAuth();
    const router = useRouter();

    const [activeTab, setActiveTab] = useState<"overview" | "traffic" | "system">("overview");
    const [stats, setStats] = useState<OverviewStats | null>(null);
    const [conversionsByType, setConversionsByType] = useState<ConversionsByType[]>([]);
    const [activityFeed, setActivityFeed] = useState<ActivityItem[]>([]);
    const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
    const [dailyConversions, setDailyConversions] = useState<DailyConversion[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);

    // Redirect non-superadmins
    useEffect(() => {
        if (!authLoading && user && user.role !== "superadmin") {
            router.push("/dashboard");
        }
    }, [authLoading, user, router]);

    // Fetch data based on active tab
    useEffect(() => {
        if (user?.role === "superadmin") {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab, user?.role]);

    const fetchData = async () => {
        setIsLoading(true);
        setError(null);

        try {
            if (activeTab === "overview" || activeTab === "traffic") {
                // Fetch overview stats
                const statsRes = await fetch(`${API_BASE_URL}/api/v1/admin/stats/overview`);
                if (statsRes.ok) setStats(await statsRes.json());

                // Fetch conversions by type
                const typesRes = await fetch(`${API_BASE_URL}/api/v1/admin/stats/conversions-by-type?days=30`);
                if (typesRes.ok) setConversionsByType(await typesRes.json());

                // Fetch activity feed
                const activityRes = await fetch(`${API_BASE_URL}/api/v1/admin/stats/activity?limit=20`);
                if (activityRes.ok) setActivityFeed(await activityRes.json());

                // Fetch daily conversions for chart
                const dailyRes = await fetch(`${API_BASE_URL}/api/v1/admin/stats/daily-conversions?days=14`);
                if (dailyRes.ok) setDailyConversions(await dailyRes.json());
            }

            if (activeTab === "system") {
                const healthRes = await fetch(`${API_BASE_URL}/api/v1/admin/health`);
                if (healthRes.ok) setSystemHealth(await healthRes.json());
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to fetch data");
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    };

    const handleRefresh = () => {
        setIsRefreshing(true);
        fetchData();
    };

    // Loading or unauthorized
    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
            </div>
        );
    }

    if (user?.role !== "superadmin") {
        return null; // Will redirect
    }

    const tabs = [
        { id: "overview" as const, label: "Overview", icon: BarChart3 },
        { id: "traffic" as const, label: "Traffic", icon: Activity },
        { id: "system" as const, label: "System", icon: Server },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard" className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                            <Shield className="w-6 h-6 text-purple-600" />
                            Admin Hub
                        </h1>
                        <p className="text-slate-500">Platform analytics and management</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-medium text-slate-700 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                    <Link
                        href="/dashboard/admin/users"
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        <Users className="w-4 h-4" />
                        Manage Users
                    </Link>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-1 p-1 bg-slate-100 rounded-xl w-fit">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                            ? "bg-white text-purple-700 shadow-sm"
                            : "text-slate-600 hover:text-slate-800"
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Error State */}
            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    {error}
                </div>
            )}

            {/* Tab Content */}
            {isLoading && !isRefreshing ? (
                <div className="flex items-center justify-center min-h-[300px]">
                    <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                </div>
            ) : (
                <>
                    {activeTab === "overview" && <OverviewTab stats={stats} conversionsByType={conversionsByType} />}
                    {activeTab === "traffic" && <TrafficTab activityFeed={activityFeed} dailyConversions={dailyConversions} conversionsByType={conversionsByType} />}
                    {activeTab === "system" && <SystemTab health={systemHealth} />}
                </>
            )}
        </div>
    );
}

// ============================================================================
// Overview Tab
// ============================================================================

function OverviewTab({ stats, conversionsByType }: { stats: OverviewStats | null; conversionsByType: ConversionsByType[] }) {
    if (!stats) return <div className="text-slate-500 text-center py-8">No data available</div>;

    const statCards = [
        { label: "Total Users", value: stats.total_users, icon: Users, color: "blue", subtext: `+${stats.new_users_7d} this week` },
        { label: "Active Users (7d)", value: stats.active_users_7d, icon: Activity, color: "green", subtext: `${stats.active_users_30d} in 30 days` },
        { label: "Conversions Today", value: stats.conversions_today, icon: FileText, color: "purple", subtext: `${stats.conversions_week} this week` },
        { label: "Total Conversions", value: stats.total_conversions, icon: TrendingUp, color: "indigo", subtext: `${stats.conversions_month} this month` },
    ];

    const colorClasses: Record<string, { bg: string; icon: string; text: string }> = {
        blue: { bg: "bg-blue-50", icon: "text-blue-600", text: "text-blue-600" },
        green: { bg: "bg-green-50", icon: "text-green-600", text: "text-green-600" },
        purple: { bg: "bg-purple-50", icon: "text-purple-600", text: "text-purple-600" },
        indigo: { bg: "bg-indigo-50", icon: "text-indigo-600", text: "text-indigo-600" },
    };

    return (
        <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {statCards.map((card, i) => {
                    const colors = colorClasses[card.color];
                    return (
                        <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-center gap-3 mb-3">
                                <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}>
                                    <card.icon className={`w-5 h-5 ${colors.icon}`} />
                                </div>
                                <span className="text-sm font-medium text-slate-500">{card.label}</span>
                            </div>
                            <p className="text-3xl font-bold text-slate-800">{card.value.toLocaleString()}</p>
                            <p className={`text-xs ${colors.text} mt-1 font-medium`}>{card.subtext}</p>
                        </div>
                    );
                })}
            </div>

            {/* Conversions by Type */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-600" />
                    Conversions by Type (Last 30 Days)
                </h3>
                {conversionsByType.length > 0 ? (
                    <div className="space-y-3">
                        {conversionsByType.map((item, i) => (
                            <div key={i} className="flex items-center gap-4">
                                <div className="w-16 text-sm font-mono font-semibold text-slate-700">{item.transaction_type}</div>
                                <div className="flex-1 bg-slate-100 rounded-full h-6 overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full flex items-center justify-end pr-2"
                                        style={{ width: `${Math.max(item.percentage, 5)}%` }}
                                    >
                                        <span className="text-xs font-medium text-white">{item.count}</span>
                                    </div>
                                </div>
                                <div className="w-16 text-right text-sm text-slate-500">{item.percentage}%</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-slate-500 text-center py-4">No conversion data yet</p>
                )}
            </div>
        </div>
    );
}

// ============================================================================
// Traffic Tab
// ============================================================================

function TrafficTab({
    activityFeed,
    dailyConversions,
    conversionsByType
}: {
    activityFeed: ActivityItem[];
    dailyConversions: DailyConversion[];
    conversionsByType: ConversionsByType[];
}) {
    const getActionIcon = (action: string) => {
        switch (action) {
            case "conversion": return <FileText className="w-4 h-4 text-purple-600" />;
            case "login": return <Users className="w-4 h-4 text-green-600" />;
            case "layout_edit": return <Activity className="w-4 h-4 text-blue-600" />;
            default: return <Activity className="w-4 h-4 text-slate-400" />;
        }
    };

    const getActionColor = (action: string) => {
        switch (action) {
            case "conversion": return "bg-purple-100 text-purple-700";
            case "login": return "bg-green-100 text-green-700";
            case "layout_edit": return "bg-blue-100 text-blue-700";
            default: return "bg-slate-100 text-slate-600";
        }
    };

    const formatTime = (dateStr: string) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return "Just now";
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    };

    // Find max for chart scaling
    const maxDaily = Math.max(...dailyConversions.map(d => d.count), 1);

    return (
        <div className="space-y-6">
            {/* Daily Conversions Chart */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                    Daily Conversions (Last 14 Days)
                </h3>
                {dailyConversions.length > 0 ? (
                    <div className="flex items-end gap-2 h-40">
                        {dailyConversions.map((day, i) => {
                            const height = (day.count / maxDaily) * 100;
                            const date = new Date(day.date);
                            return (
                                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                                    <span className="text-xs font-medium text-slate-600">{day.count}</span>
                                    <div
                                        className="w-full bg-gradient-to-t from-purple-500 to-indigo-400 rounded-t-md transition-all hover:from-purple-600 hover:to-indigo-500"
                                        style={{ height: `${Math.max(height, 4)}%` }}
                                        title={`${day.date}: ${day.count} conversions`}
                                    />
                                    <span className="text-[10px] text-slate-400">{date.getDate()}/{date.getMonth() + 1}</span>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <p className="text-slate-500 text-center py-8">No conversion data yet</p>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Activity Feed */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-600" />
                        Recent Activity
                    </h3>
                    {activityFeed.length > 0 ? (
                        <div className="space-y-3 max-h-[400px] overflow-y-auto">
                            {activityFeed.map((item) => (
                                <div key={item.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                                    <div className="mt-0.5">{getActionIcon(item.action)}</div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getActionColor(item.action)}`}>
                                                {item.action}
                                            </span>
                                            {typeof item.details?.transaction_type === 'string' && (
                                                <span className="text-xs text-slate-500 font-mono">
                                                    {item.details.transaction_type}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-slate-600 truncate mt-1">
                                            {item.user_email || item.user_id?.slice(0, 8) || "Anonymous"}
                                            {typeof item.details?.filename === 'string' && ` → ${item.details.filename}`}
                                        </p>
                                    </div>
                                    <span className="text-xs text-slate-400 whitespace-nowrap">{formatTime(item.created_at)}</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 text-center py-8">No activity yet</p>
                    )}
                </div>

                {/* Feature Usage */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-purple-600" />
                        Feature Usage
                    </h3>
                    {conversionsByType.length > 0 ? (
                        <div className="space-y-4">
                            {conversionsByType.slice(0, 8).map((item, i) => (
                                <div key={i} className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                                            {item.transaction_type}
                                        </div>
                                        <div>
                                            <p className="font-medium text-slate-800">EDI {item.transaction_type}</p>
                                            <p className="text-xs text-slate-500">{item.count} conversions</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-lg font-bold text-slate-800">{item.percentage}%</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 text-center py-8">No usage data yet</p>
                    )}
                </div>
            </div>
        </div>
    );
}

// ============================================================================
// System Tab
// ============================================================================

function SystemTab({ health }: { health: SystemHealth | null }) {
    if (!health) return <div className="text-slate-500 text-center py-8">No health data available</div>;

    return (
        <div className="space-y-6">
            {/* Health Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Database */}
                <div className={`p-6 rounded-xl border ${health.database_connected ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                    <div className="flex items-center gap-3 mb-3">
                        <Database className={`w-6 h-6 ${health.database_connected ? 'text-green-600' : 'text-red-600'}`} />
                        <span className="font-semibold text-slate-800">Database</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {health.database_connected ? (
                            <>
                                <CheckCircle className="w-5 h-5 text-green-600" />
                                <span className="text-green-700 font-medium">Connected</span>
                            </>
                        ) : (
                            <>
                                <AlertTriangle className="w-5 h-5 text-red-600" />
                                <span className="text-red-700 font-medium">Disconnected</span>
                            </>
                        )}
                    </div>
                </div>

                {/* Email Processing */}
                <div className={`p-6 rounded-xl border ${health.email_errors_24h === 0 ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                    <div className="flex items-center gap-3 mb-3">
                        <Mail className={`w-6 h-6 ${health.email_errors_24h === 0 ? 'text-green-600' : 'text-yellow-600'}`} />
                        <span className="font-semibold text-slate-800">Email Processing</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {health.email_errors_24h === 0 ? (
                            <>
                                <CheckCircle className="w-5 h-5 text-green-600" />
                                <span className="text-green-700 font-medium">No errors</span>
                            </>
                        ) : (
                            <>
                                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                                <span className="text-yellow-700 font-medium">{health.email_errors_24h} errors (24h)</span>
                            </>
                        )}
                    </div>
                </div>

                {/* Stats Summary */}
                <div className="p-6 rounded-xl border bg-purple-50 border-purple-200">
                    <div className="flex items-center gap-3 mb-3">
                        <BarChart3 className="w-6 h-6 text-purple-600" />
                        <span className="font-semibold text-slate-800">Platform Stats</span>
                    </div>
                    <div className="space-y-1 text-sm">
                        <p className="text-purple-700"><strong>{health.total_users}</strong> total users</p>
                        <p className="text-purple-700"><strong>{health.total_conversions}</strong> total conversions</p>
                    </div>
                </div>
            </div>

            {/* Recent Errors */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600" />
                    Recent Email Errors
                </h3>
                {health.recent_errors.length > 0 ? (
                    <div className="space-y-3">
                        {health.recent_errors.map((error, i) => (
                            <div key={i} className="p-4 bg-red-50 border border-red-100 rounded-lg">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-red-800">{error.error}</p>
                                        {error.snippet && (
                                            <p className="text-xs text-red-600 mt-1 truncate font-mono">{error.snippet}</p>
                                        )}
                                    </div>
                                    <span className="text-xs text-red-500 whitespace-nowrap">
                                        {error.created_at ? new Date(error.created_at).toLocaleString() : "Unknown"}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="flex items-center justify-center gap-2 py-8 text-green-600">
                        <CheckCircle className="w-5 h-5" />
                        <span className="font-medium">No recent errors</span>
                    </div>
                )}
            </div>
        </div>
    );
}
