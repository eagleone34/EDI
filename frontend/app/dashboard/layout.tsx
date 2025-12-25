"use client";

import { useState } from "react";
import Link from "next/link";
import {
    LayoutDashboard,
    History,
    Route,
    Settings,
    Mail,
    LogOut,
    ChevronRight,
    Menu,
    X
} from "lucide-react";
import { usePathname } from "next/navigation";

const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "History", href: "/dashboard/history", icon: History },
    { name: "Routing Rules", href: "/dashboard/routing", icon: Route },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Mobile Header */}
            <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200 px-4 py-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                            <Mail className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-bold text-lg">EDI.email</span>
                    </div>
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="p-2 hover:bg-slate-100 rounded-lg"
                    >
                        {isMobileMenuOpen ? (
                            <X className="w-6 h-6" />
                        ) : (
                            <Menu className="w-6 h-6" />
                        )}
                    </button>
                </div>
            </div>

            {/* Mobile Sidebar Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="lg:hidden fixed inset-0 z-40 bg-black/50"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
        fixed left-0 top-0 h-full w-64 bg-white border-r border-slate-200 z-50
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0
        ${isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="p-6 border-b border-slate-100">
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform">
                                <Mail className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold">EDI.email</span>
                        </Link>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 p-4 space-y-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                    ${isActive
                                            ? "bg-primary-50 text-primary-600"
                                            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                                        }
                  `}
                                >
                                    <item.icon className={`w-5 h-5 ${isActive ? "text-primary-600" : "text-slate-400"}`} />
                                    {item.name}
                                    {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Email Address */}
                    <div className="p-4 border-t border-slate-100">
                        <div className="bg-gradient-to-r from-primary-50 to-violet-50 rounded-xl p-4">
                            <p className="text-xs font-medium text-slate-500 mb-1">Your EDI Email</p>
                            <p className="text-sm font-semibold text-primary-600 break-all">
                                user@edi.email
                            </p>
                        </div>
                    </div>

                    {/* Logout */}
                    <div className="p-4 border-t border-slate-100">
                        <button className="flex items-center gap-3 px-4 py-3 w-full text-slate-600 hover:bg-slate-50 rounded-xl font-medium transition-colors">
                            <LogOut className="w-5 h-5 text-slate-400" />
                            Sign Out
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="lg:ml-64 pt-16 lg:pt-0 min-h-screen">
                <div className="p-6 lg:p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
