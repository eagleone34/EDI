"use client";

import { useState } from "react";
import { Plus, Server, Check, X, Mail, Copy } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";
import { useAuth } from "@/lib/auth-context";
import EmailRoutesSettings from "@/components/dashboard/EmailRoutesSettings";

export default function IntegrationsPage() {
    const { user } = useAuth();
    const [isAdding, setIsAdding] = useState(false);
    const [protocol, setProtocol] = useState<"sftp" | "gdrive" | "onedrive">("sftp");
    const [copied, setCopied] = useState(false);

    // Form State
    const [name, setName] = useState("");
    const [host, setHost] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [port, setPort] = useState("22");

    const [isTesting, setIsTesting] = useState(false);
    const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

    const handleCopyEmail = () => {
        if (user?.inboundEmail) {
            navigator.clipboard.writeText(user.inboundEmail);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/integrations/test`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    type: "sftp",
                    config: { host, username, password, port }
                }),
            });
            const data = await response.json();

            if (data.success) {
                setTestResult("success");
            } else {
                setTestResult("error");
                // TODO: Store error message to display
            }
        } catch (error) {
            console.error("Test failed:", error);
            setTestResult("error");
        } finally {
            setIsTesting(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Inbound Email Section */}
            {user?.inboundEmail && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="p-6 border-b border-slate-100">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Mail className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-slate-800">Inbound Email Address</h2>
                                <p className="text-sm text-slate-500">Your unique address for receiving EDI files via email</p>
                            </div>
                        </div>
                    </div>
                    <div className="p-6 bg-slate-50">
                        <div className="flex items-center gap-3">
                            <input
                                type="text"
                                value={user.inboundEmail}
                                readOnly
                                className="flex-1 px-4 py-2.5 bg-gray-100 border border-slate-200 rounded-lg font-mono text-sm text-slate-600 cursor-not-allowed"
                            />
                            <button
                                onClick={handleCopyEmail}
                                className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
                            >
                                {copied ? (
                                    <>
                                        <Check className="w-4 h-4" />
                                        Copied
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-4 h-4" />
                                        Copy
                                    </>
                                )}
                            </button>
                        </div>
                        <p className="text-xs text-slate-500 mt-3">
                            Forward EDI files to this address. They'll be automatically converted and added to your account.
                            Your routing rules will apply automatically.
                        </p>
                    </div>
                </div>
            )}

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

                            {(protocol === "gdrive" || protocol === "onedrive") && (
                                <div className="space-y-4 animate-in fade-in">
                                    <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-700 flex items-start gap-3">
                                        <div className="mt-0.5 font-bold">ℹ️</div>
                                        <div>
                                            Authorization required. You will be redirected to {protocol === "gdrive" ? "Google" : "Microsoft"} to approve access.
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Connection Name</label>
                                        <input
                                            type="text"
                                            placeholder={`My ${protocol === 'gdrive' ? 'Google Drive' : 'OneDrive'}`}
                                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                        />
                                    </div>
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
                                <h4 className="font-semibold text-slate-800">Connection Status</h4>
                                <p className="text-xs text-slate-500 mt-1 max-w-[200px] mx-auto">
                                    {testResult === "success" ? "Connection verified successfully!" :
                                        testResult === "error" ? "Could not connect. Check credentials." :
                                            protocol === "sftp" ? "Enter details and test connection." :
                                                "Click below to authenticate."}
                                </p>
                            </div>

                            {protocol === "sftp" ? (
                                <button
                                    onClick={handleTestConnection}
                                    disabled={isTesting || !host || !username}
                                    className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-all ${isTesting
                                        ? "bg-slate-200 text-slate-500 cursor-wait"
                                        : "bg-white border border-slate-300 text-slate-700 hover:bg-white hover:shadow-sm"
                                        }`}
                                >
                                    {isTesting ? "Testing..." : "Test SFTP Connection"}
                                </button>
                            ) : (
                                <button
                                    onClick={() => {
                                        setIsTesting(true);
                                        // Mock OAuth delay
                                        setTimeout(() => { setIsTesting(false); setTestResult("success"); }, 2000);
                                    }}
                                    className="w-full py-2 px-4 rounded-lg text-sm font-medium bg-white border border-slate-300 text-slate-700 hover:bg-white hover:shadow-sm"
                                >
                                    {isTesting ? "Redirecting..." : `Connect ${protocol === 'gdrive' ? 'Google' : 'Microsoft'} Account`}
                                </button>
                            )}

                            {testResult === "success" && (
                                <button className="w-full py-2 px-4 rounded-lg text-sm font-bold bg-green-600 text-white hover:bg-green-700 shadow-sm animate-in zoom-in duration-300">
                                    Save Connection
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Email Routing Section */}
            <EmailRoutesSettings />
        </div>
    );
}
