export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-slate-50">
            {/* Sidebar */}
            <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-8">
                    <span className="text-xl font-bold">EDI.email</span>
                </div>
                <nav className="space-y-2">
                    <a href="/dashboard" className="block px-4 py-2 rounded-lg bg-primary-50 text-primary-600 font-medium">
                        Dashboard
                    </a>
                    <a href="/dashboard/history" className="block px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-50">
                        History
                    </a>
                    <a href="/dashboard/routing" className="block px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-50">
                        Routing Rules
                    </a>
                    <a href="/dashboard/settings" className="block px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-50">
                        Settings
                    </a>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="ml-64 p-8">
                {children}
            </main>
        </div>
    );
}
