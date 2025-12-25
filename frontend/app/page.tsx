"use client";

import { Navbar } from "@/components/Navbar";
import { FileUploader } from "@/components/FileUploader";
import { Mail, FileText, Zap, Shield, Check, ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
    return (
        <main className="min-h-screen bg-white">
            <Navbar />

            {/* Hero Section */}
            <section className="pt-28 pb-16 px-6 bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-12">
                        {/* Badge */}
                        <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 bg-gradient-to-r from-primary-50 to-violet-50 border border-primary-100 rounded-full">
                            <Sparkles className="w-4 h-4 text-primary-600" />
                            <span className="text-sm font-medium text-primary-700">
                                Transform EDI files in seconds
                            </span>
                        </div>

                        {/* Headline */}
                        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight tracking-tight">
                            Forward EDI files.
                            <br />
                            <span className="bg-gradient-to-r from-primary-600 via-violet-600 to-primary-600 bg-clip-text text-transparent">
                                Get readable PDFs.
                            </span>
                        </h1>

                        <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed">
                            Convert complex EDI files (850, 810, 856) into beautiful PDFs, Excel files,
                            or HTML — through simple email automation. No setup required.
                        </p>

                        {/* Trust badges */}
                        <div className="flex flex-wrap justify-center gap-6 mb-12 text-sm text-slate-500">
                            <div className="flex items-center gap-2">
                                <Check className="w-4 h-4 text-green-500" />
                                <span>5-minute setup</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Check className="w-4 h-4 text-green-500" />
                                <span>No credit card required</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Check className="w-4 h-4 text-green-500" />
                                <span>10 free conversions</span>
                            </div>
                        </div>
                    </div>

                    {/* File Uploader */}
                    <div className="max-w-2xl mx-auto">
                        <FileUploader />
                        <p className="text-center text-sm text-slate-500 mt-4">
                            Supports: 850 (Purchase Order), 810 (Invoice), 856 (ASN), 855, 997
                        </p>
                    </div>
                </div>
            </section>

            {/* How it Works */}
            <section id="how-it-works" className="py-24 px-6 bg-white">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">
                            How it works
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Convert EDI files in three simple steps
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: Mail,
                                step: "01",
                                title: "Forward your EDI",
                                desc: "Send EDI files to your unique @edi.email address, or upload directly on the web.",
                                color: "from-blue-500 to-blue-600"
                            },
                            {
                                icon: Zap,
                                step: "02",
                                title: "Instant conversion",
                                desc: "We parse and convert your EDI in under 30 seconds using intelligent document recognition.",
                                color: "from-violet-500 to-violet-600"
                            },
                            {
                                icon: FileText,
                                step: "03",
                                title: "Get readable output",
                                desc: "Receive beautifully formatted PDF, Excel, or HTML right in your inbox.",
                                color: "from-emerald-500 to-emerald-600"
                            }
                        ].map((item, i) => (
                            <div key={i} className="relative group">
                                <div className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-slate-300 hover:shadow-xl transition-all duration-300">
                                    <div className={`w-14 h-14 bg-gradient-to-br ${item.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                                        <item.icon className="w-7 h-7 text-white" />
                                    </div>
                                    <div className="text-xs font-bold text-slate-400 mb-2">STEP {item.step}</div>
                                    <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                                    <p className="text-slate-600 leading-relaxed">{item.desc}</p>
                                </div>
                                {i < 2 && (
                                    <div className="hidden md:block absolute top-1/2 -right-4 transform translate-x-1/2 -translate-y-1/2">
                                        <ArrowRight className="w-8 h-8 text-slate-300" />
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features */}
            <section id="features" className="py-24 px-6 bg-gradient-to-b from-slate-50 to-white">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">
                            Why businesses choose EDI.email
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            We solve the real problems SMBs face with EDI compliance
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            {
                                emoji: "⚡",
                                title: "5-Minute Setup",
                                desc: "No 60-90 day implementations. Start converting immediately.",
                                highlight: true
                            },
                            {
                                emoji: "📧",
                                title: "Email Automation",
                                desc: "Forward EDI files to your unique address. No portals or software to install.",
                                highlight: false
                            },
                            {
                                emoji: "📄",
                                title: "Multi-Format Output",
                                desc: "Get PDF, Excel, or HTML — whatever your team needs.",
                                highlight: false
                            },
                            {
                                emoji: "🔄",
                                title: "Smart Routing",
                                desc: "Auto-route different document types to the right people.",
                                highlight: false
                            },
                            {
                                emoji: "💰",
                                title: "Transparent Pricing",
                                desc: "$99/month unlimited. No hidden fees or \"request quote\" games.",
                                highlight: true
                            },
                            {
                                emoji: "🔒",
                                title: "Enterprise Security",
                                desc: "Encrypted storage, SOC 2 compliant, GDPR ready.",
                                highlight: false
                            },
                        ].map((feature, i) => (
                            <div
                                key={i}
                                className={`
                  p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1
                  ${feature.highlight
                                        ? "bg-gradient-to-br from-primary-600 to-violet-600 text-white shadow-lg shadow-primary-500/25"
                                        : "bg-white border border-slate-200 hover:shadow-lg hover:border-slate-300"
                                    }
                `}
                            >
                                <div className="text-3xl mb-4">{feature.emoji}</div>
                                <h3 className={`text-lg font-semibold mb-2 ${feature.highlight ? "text-white" : ""}`}>
                                    {feature.title}
                                </h3>
                                <p className={feature.highlight ? "text-white/80" : "text-slate-600"}>
                                    {feature.desc}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section id="pricing" className="py-24 px-6 bg-white">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">
                            Simple, transparent pricing
                        </h2>
                        <p className="text-lg text-slate-600">
                            Start free, upgrade when you need more
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Free Tier */}
                        <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
                            <h3 className="text-xl font-semibold mb-2">Free</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">$0</span>
                                <span className="text-slate-500">/month</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                {["10 conversions/month", "PDF output only", "Web upload", "Email support"].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-green-500" />
                                        <span className="text-slate-600">{item}</span>
                                    </li>
                                ))}
                            </ul>
                            <button className="w-full py-3 border border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
                                Get Started
                            </button>
                        </div>

                        {/* Pro Tier */}
                        <div className="relative bg-gradient-to-b from-primary-600 to-primary-700 rounded-2xl p-8 text-white shadow-xl shadow-primary-500/30 scale-105">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-amber-400 to-orange-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                                Most Popular
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Pro</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">$99</span>
                                <span className="text-white/70">/month</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                {[
                                    "Unlimited conversions",
                                    "Email automation",
                                    "PDF, Excel, HTML output",
                                    "Smart routing",
                                    "Custom branding",
                                    "Priority support"
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-emerald-300" />
                                        <span className="text-white/90">{item}</span>
                                    </li>
                                ))}
                            </ul>
                            <button className="w-full py-3 bg-white text-primary-600 rounded-xl font-semibold hover:bg-slate-100 transition-colors">
                                Start Free Trial
                            </button>
                        </div>

                        {/* Enterprise Tier */}
                        <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
                            <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">Custom</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                {[
                                    "Everything in Pro",
                                    "SFTP/AS2 integration",
                                    "API access",
                                    "SLA guarantees",
                                    "Dedicated support",
                                    "White-label options"
                                ].map((item, i) => (
                                    <li key={i} className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-green-500" />
                                        <span className="text-slate-600">{item}</span>
                                    </li>
                                ))}
                            </ul>
                            <button className="w-full py-3 border border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
                                Contact Sales
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 px-6 bg-gradient-to-br from-primary-600 via-violet-600 to-primary-700">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                        Ready to simplify your EDI workflow?
                    </h2>
                    <p className="text-xl text-white/80 mb-8">
                        Join thousands of businesses converting EDI files effortlessly.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button className="px-8 py-4 bg-white text-primary-600 rounded-xl font-semibold text-lg hover:bg-slate-100 transition-colors shadow-lg">
                            Start Free Trial
                        </button>
                        <button className="px-8 py-4 bg-white/10 text-white border border-white/30 rounded-xl font-semibold text-lg hover:bg-white/20 transition-colors">
                            Schedule Demo
                        </button>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-16 px-6 bg-slate-900">
                <div className="max-w-6xl mx-auto">
                    <div className="grid md:grid-cols-4 gap-8 mb-12">
                        <div className="md:col-span-2">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
                                    <Mail className="w-5 h-5 text-white" />
                                </div>
                                <span className="text-xl font-bold text-white">EDI.email</span>
                            </div>
                            <p className="text-slate-400 max-w-sm">
                                The Mailchimp of EDI — dead simple automation that just works.
                                Transform complex EDI files into human-readable formats in seconds.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white mb-4">Product</h4>
                            <ul className="space-y-2 text-slate-400">
                                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">API Docs</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold text-white mb-4">Company</h4>
                            <ul className="space-y-2 text-slate-400">
                                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-slate-800 text-center text-slate-500">
                        <p>© 2024 EDI.email. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </main>
    );
}
