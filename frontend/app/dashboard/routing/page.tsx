"use client";

import EmailRoutesSettings from "@/components/dashboard/EmailRoutesSettings";

export default function RoutingPage() {
    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl lg:text-3xl font-bold mb-2">Routing Rules</h1>
                <p className="text-slate-600">Automatically route documents to the right people</p>
            </div>

            <EmailRoutesSettings />
        </div>
    );
}
