"use client";

import TransactionsTable from "@/components/dashboard/TransactionsTable";

export default function HistoryPage() {
    return (
        <div className="max-w-7xl mx-auto">
            <div className="mb-8">
                <p className="text-slate-600">View and download your past conversions</p>
            </div>

            <TransactionsTable title="Conversion History" limit={0} />
        </div>
    );
}
