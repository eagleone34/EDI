import { FileUp, Mail, FileText, TrendingUp } from "lucide-react";

export default function DashboardPage() {
    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
                <p className="text-slate-600">Welcome back! Here's your conversion summary.</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-slate-500 text-sm">This Month</span>
                        <TrendingUp className="w-5 h-5 text-green-500" />
                    </div>
                    <div className="text-3xl font-bold">0</div>
                    <div className="text-slate-500 text-sm">conversions</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-slate-500 text-sm">Remaining</span>
                    </div>
                    <div className="text-3xl font-bold">10</div>
                    <div className="text-slate-500 text-sm">free conversions</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-slate-500 text-sm">Routing Rules</span>
                    </div>
                    <div className="text-3xl font-bold">0</div>
                    <div className="text-slate-500 text-sm">active rules</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-slate-500 text-sm">Your Email</span>
                        <Mail className="w-5 h-5 text-primary-500" />
                    </div>
                    <div className="text-sm font-medium text-primary-600 break-all">user@edi.email</div>
                </div>
            </div>

            {/* Quick Upload */}
            <div className="bg-white rounded-xl p-8 shadow-sm mb-8">
                <h2 className="text-lg font-semibold mb-4">Quick Convert</h2>
                <div className="drop-zone rounded-xl p-8 text-center">
                    <FileUp className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-600 mb-4">Drag & drop your EDI file here</p>
                    <button className="btn-primary">Select File</button>
                </div>
            </div>

            {/* Recent Conversions */}
            <div className="bg-white rounded-xl shadow-sm">
                <div className="p-6 border-b border-slate-100">
                    <h2 className="text-lg font-semibold">Recent Conversions</h2>
                </div>
                <div className="p-6">
                    <div className="text-center py-12 text-slate-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                        <p>No conversions yet. Upload your first EDI file above!</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
