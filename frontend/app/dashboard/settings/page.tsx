"use client";

import { useState } from "react";
import { Plus, Server, Check, X } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";

export default function IntegrationsPage() {
    const [isAdding, setIsAdding] = useState(false);
    const [protocol, setProtocol] = useState<"sftp" | "gdrive" | "onedrive">("sftp");

    // Form State
    const [name, setName] = useState("");
    const [host, setHost] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [port, setPort] = useState("22");

    const [isTesting, setIsTesting] = useState(false);
    const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);

        // Mock test for now (until backend endpoint exists)
        setTimeout(() => {
            setIsTesting(false);
            if (host && username) {
                setTestResult("success");
            } else {
                setTestResult("error");
            }
        }, 1500);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Integrations</h1>
                    <p className="text-slate-500 mt-1">Connect external services to route your files.</p>
                </div>
                <button
                    onClick={() => setIsAdding(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    New Connection
                </button>
            </div>

            {/* List of Integrations (Empty State) */}
            {!isAdding && (
                <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Server className="w-8 h-8 text-slate-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-700">No connections yet</h3>
                    <p className="text-slate-500 mt-1 max-w-sm mx-auto">
                        Add an SFTP server, Google Drive, or OneDrive to automatically save your converted files.
                    </p>
                    <button
                        onClick={() => setIsAdding(true)}
                        className="mt-6 text-blue-600 font-medium hover:underline"
                    >
                        Add your first connection
                    </button>
                </div>
            )}

            {/* Add Connection Form */}
            {isAdding && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <h2 className="text-lg font-bold text-slate-800">Add New Connection</h2>
                        <button onClick={() => setIsAdding(false)} className="text-slate-400 hover:text-slate-600">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Connection Type</label>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setProtocol("sftp")}
                                        className={`flex-1 py-3 px-4 rounded-lg border text-sm font-medium transition-all ${protocol === "sftp"
                                                ? "bg-blue-50 border-blue-200 text-blue-700 ring-1 ring-blue-200"
                                                : "border-slate-200 text-slate-600 hover:bg-slate-50"
                                            }`}
                                    >
                                        SFTP Server
                                    </button>
                                    <button
                                        onClick={() => setProtocol("gdrive")}
                                        className={`flex-1 py-3 px-4 rounded-lg border text-sm font-medium transition-all ${protocol === "gdrive"
                                                ? "bg-blue-50 border-blue-200 text-blue-700 ring-1 ring-blue-200"
                                                : "border-slate-200 text-slate-600 hover:bg-slate-50"
                                            }`}
                                    >
                                        Google Drive
                                    </button>
                                </div>
                            </div>

                            {protocol === "sftp" && (
                                <div className="space-y-4 animate-in fade-in">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Connection Name</label>
                                        <input
                                            type="text"
                                            placeholder="e.g. Client A SFTP"
                                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                        />
                                    </div>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="col-span-2">
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Host Address</label>
                                            <input
                                                type="text"
                                                placeholder="sftp.example.com"
                                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
                                                value={host}
                                                onChange={(e) => setHost(e.target.value)}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Port</label>
                                            <input
                                                type="text"
                                                placeholder="22"
                                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
                                                value={port}
                                                onChange={(e) => setPort(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
                                        <input
                                            type="text"
                                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Password / Private Key</label>
                                        <input
                                            type="password"
                                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                        />
                                    </div>
                                </div>
                            )}

                            {protocol !== "sftp" && (
                                <div className="p-4 bg-slate-50 rounded-lg text-sm text-slate-600">
                                    Please use SFTP for the initial setup. Cloud drive integrations (Google/OneDrive) will be enabled in the next update.
                                </div>
                            )}
                        </div>

                        {/* Testing Panel */}
                        <div className="bg-slate-50 rounded-xl p-6 flex flex-col justify-center items-center text-center space-y-4">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${testResult === "success" ? "bg-green-100 text-green-600" :
                                    testResult === "error" ? "bg-red-100 text-red-600" :
                                        "bg-white border border-slate-200 text-slate-400"
                                }`}>
                                {testResult === "success" ? <Check className="w-6 h-6" /> :
                                    testResult === "error" ? <X className="w-6 h-6" /> :
                                        <Server className="w-6 h-6" />}
                            </div>

                            <div>
                                <h4 className="font-semibold text-slate-800">Connection Test</h4>
                                <p className="text-xs text-slate-500 mt-1">
                                    {testResult === "success" ? "Connection verified successfully!" :
                                        testResult === "error" ? "Could not connect. Check credentials." :
                                            "Enter details and test before saving."}
                                </p>
                            </div>

                            <button
                                onClick={handleTestConnection}
                                disabled={isTesting || !host || !username}
                                className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-all ${isTesting
                                        ? "bg-slate-200 text-slate-500 cursor-wait"
                                        : "bg-white border border-slate-300 text-slate-700 hover:bg-white hover:shadow-sm"
                                    }`}
                            >
                                {isTesting ? "Testing..." : "Test Connection"}
                            </button>

                            {testResult === "success" && (
                                <button className="w-full py-2 px-4 rounded-lg text-sm font-bold bg-green-600 text-white hover:bg-green-700 shadow-sm animate-in zoom-in duration-300">
                                    Save Connection
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
