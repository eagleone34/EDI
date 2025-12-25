"use client";

import { useState } from "react";
import {
    User,
    Bell,
    CreditCard,
    Shield,
    Save,
    Check
} from "lucide-react";

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);
    const [settings, setSettings] = useState({
        name: "Demo User",
        email: "demo@company.com",
        company: "ACME Corporation",
        defaultFormat: "pdf",
        emailNotifications: true,
        weeklyDigest: false,
    });

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl lg:text-3xl font-bold mb-2">Settings</h1>
                <p className="text-slate-600">Manage your account and preferences</p>
            </div>

            <div className="space-y-6">
                {/* Profile Section */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
                        <User className="w-5 h-5 text-slate-400" />
                        <h2 className="font-semibold">Profile</h2>
                    </div>
                    <div className="p-6 space-y-4">
                        <div className="grid sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Name</label>
                                <input
                                    type="text"
                                    value={settings.name}
                                    onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                                <input
                                    type="email"
                                    value={settings.email}
                                    onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Company</label>
                            <input
                                type="text"
                                value={settings.company}
                                onChange={(e) => setSettings({ ...settings, company: e.target.value })}
                                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                        </div>
                    </div>
                </div>

                {/* Preferences Section */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
                        <Bell className="w-5 h-5 text-slate-400" />
                        <h2 className="font-semibold">Preferences</h2>
                    </div>
                    <div className="p-6 space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Default Output Format</label>
                            <select
                                value={settings.defaultFormat}
                                onChange={(e) => setSettings({ ...settings, defaultFormat: e.target.value })}
                                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                            >
                                <option value="pdf">PDF</option>
                                <option value="excel">Excel</option>
                                <option value="html">HTML</option>
                                <option value="all">All Formats</option>
                            </select>
                        </div>
                        <div className="flex items-center justify-between py-3 border-b border-slate-100">
                            <div>
                                <p className="font-medium text-slate-900">Email Notifications</p>
                                <p className="text-sm text-slate-500">Receive emails when conversions complete</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, emailNotifications: !settings.emailNotifications })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.emailNotifications ? "bg-primary-600" : "bg-slate-200"
                                    }`}
                            >
                                <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.emailNotifications ? "left-7" : "left-1"
                                    }`} />
                            </button>
                        </div>
                        <div className="flex items-center justify-between py-3">
                            <div>
                                <p className="font-medium text-slate-900">Weekly Digest</p>
                                <p className="text-sm text-slate-500">Receive a weekly summary of your activity</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, weeklyDigest: !settings.weeklyDigest })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.weeklyDigest ? "bg-primary-600" : "bg-slate-200"
                                    }`}
                            >
                                <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${settings.weeklyDigest ? "left-7" : "left-1"
                                    }`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Billing Section */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
                        <CreditCard className="w-5 h-5 text-slate-400" />
                        <h2 className="font-semibold">Billing</h2>
                    </div>
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <p className="font-medium text-slate-900">Current Plan</p>
                                <p className="text-sm text-slate-500">Free - 10 conversions/month</p>
                            </div>
                            <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm font-medium">Free</span>
                        </div>
                        <button className="w-full py-3 bg-gradient-to-r from-primary-600 to-violet-600 text-white rounded-xl font-semibold hover:opacity-90 transition-opacity">
                            Upgrade to Pro - $99/month
                        </button>
                    </div>
                </div>

                {/* Security Section */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
                        <Shield className="w-5 h-5 text-slate-400" />
                        <h2 className="font-semibold">Security</h2>
                    </div>
                    <div className="p-6">
                        <button className="px-4 py-2.5 border border-slate-200 rounded-xl font-medium hover:bg-slate-50 transition-colors">
                            Change Password
                        </button>
                    </div>
                </div>

                {/* Save Button */}
                <button
                    onClick={handleSave}
                    className={`w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${saved
                            ? "bg-green-600 text-white"
                            : "bg-primary-600 text-white hover:bg-primary-700"
                        }`}
                >
                    {saved ? (
                        <>
                            <Check className="w-5 h-5" />
                            Saved!
                        </>
                    ) : (
                        <>
                            <Save className="w-5 h-5" />
                            Save Changes
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
