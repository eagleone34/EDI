import { FileUp, Mail, FileText, Zap, Shield, DollarSign } from "lucide-react";

export default function Home() {
    return (
        <main className="min-h-screen">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 glass border-b border-slate-200">
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Mail className="w-8 h-8 text-primary-600" />
                        <span className="text-xl font-bold">EDI.email</span>
                    </div>
                    <div className="flex items-center gap-6">
                        <a href="#features" className="text-slate-600 hover:text-primary-600 transition-colors">Features</a>
                        <a href="#pricing" className="text-slate-600 hover:text-primary-600 transition-colors">Pricing</a>
                        <a href="/auth/login" className="text-slate-600 hover:text-primary-600 transition-colors">Login</a>
                        <a href="/auth/signup" className="btn-primary">Get Started</a>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6 bg-gradient-to-b from-slate-50 to-white">
                <div className="max-w-5xl mx-auto text-center">
                    <div className="inline-block mb-6 px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                        🚀 Transform EDI files in seconds
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                        Forward EDI files.{" "}
                        <span className="gradient-text">Get readable PDFs.</span>
                    </h1>
                    <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
                        Convert complex EDI files (850, 810, 856) into beautiful PDFs, Excel files,
                        or HTML — through simple email automation. No setup required.
                    </p>

                    {/* Upload Area */}
                    <div className="max-w-2xl mx-auto">
                        <div className="drop-zone rounded-2xl p-12 cursor-pointer hover:shadow-lg transition-shadow bg-white">
                            <FileUp className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold mb-2">Try it now — no signup needed</h3>
                            <p className="text-slate-500 mb-4">Drag & drop your EDI file or click to browse</p>
                            <input
                                type="file"
                                className="hidden"
                                accept=".edi,.txt,.x12,.dat"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="inline-block btn-primary cursor-pointer"
                            >
                                Select EDI File
                            </label>
                        </div>
                        <p className="text-sm text-slate-500 mt-4">
                            Supports: 850 (Purchase Order), 810 (Invoice), 856 (ASN), 855, 997
                        </p>
                    </div>
                </div>
            </section>

            {/* How it Works */}
            <section className="py-20 px-6 bg-white">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-8 h-8 text-primary-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-2">1. Forward your EDI</h3>
                            <p className="text-slate-600">
                                Send EDI files to your unique @edi.email address
                            </p>
                        </div>
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <Zap className="w-8 h-8 text-primary-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-2">2. Instant conversion</h3>
                            <p className="text-slate-600">
                                We parse and convert your EDI in under 30 seconds
                            </p>
                        </div>
                        <div className="text-center p-6">
                            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <FileText className="w-8 h-8 text-primary-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-2">3. Get readable output</h3>
                            <p className="text-slate-600">
                                Receive PDF, Excel, or HTML right in your inbox
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section id="features" className="py-20 px-6 bg-slate-50">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-4">Why EDI.email?</h2>
                    <p className="text-slate-600 text-center mb-12 max-w-2xl mx-auto">
                        We solve the real problems that SMBs face with EDI compliance
                    </p>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            {
                                icon: "⚡",
                                title: "5-Minute Setup",
                                desc: "No 60-90 day implementations. Start converting immediately."
                            },
                            {
                                icon: "📧",
                                title: "Email Automation",
                                desc: "Forward EDI files to your unique address. No portals or software."
                            },
                            {
                                icon: "📄",
                                title: "Multi-Format Output",
                                desc: "Get PDF, Excel, or HTML — whatever your team needs."
                            },
                            {
                                icon: "🔄",
                                title: "Smart Routing",
                                desc: "Auto-route different document types to the right people."
                            },
                            {
                                icon: "💰",
                                title: "Transparent Pricing",
                                desc: "$99/month unlimited. No hidden fees or \"request quote\" games."
                            },
                            {
                                icon: "🔒",
                                title: "Enterprise Security",
                                desc: "Encrypted storage, SOC 2 compliant, GDPR ready."
                            },
                        ].map((feature, i) => (
                            <div key={i} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                                <div className="text-3xl mb-3">{feature.icon}</div>
                                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                                <p className="text-slate-600">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section id="pricing" className="py-20 px-6 bg-white">
                <div className="max-w-5xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-4">Simple, transparent pricing</h2>
                    <p className="text-slate-600 text-center mb-12">
                        Start free, upgrade when you need more
                    </p>
                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Free Tier */}
                        <div className="border border-slate-200 rounded-2xl p-8">
                            <h3 className="text-xl font-semibold mb-2">Free</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">$0</span>
                                <span className="text-slate-500">/month</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> 10 conversions/month
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> PDF output only
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Web upload
                                </li>
                            </ul>
                            <button className="w-full btn-secondary">Get Started</button>
                        </div>

                        {/* Pro Tier */}
                        <div className="border-2 border-primary-600 rounded-2xl p-8 relative">
                            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary-600 text-white px-3 py-1 rounded-full text-sm">
                                Most Popular
                            </div>
                            <h3 className="text-xl font-semibold mb-2">Pro</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">$99</span>
                                <span className="text-slate-500">/month</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Unlimited conversions
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Email automation
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> PDF, Excel, HTML output
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Smart routing
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Custom branding
                                </li>
                            </ul>
                            <button className="w-full btn-primary">Start Free Trial</button>
                        </div>

                        {/* Enterprise Tier */}
                        <div className="border border-slate-200 rounded-2xl p-8">
                            <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold">Custom</span>
                            </div>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Everything in Pro
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> SFTP/AS2 integration
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> API access
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> SLA guarantees
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-green-500">✓</span> Dedicated support
                                </li>
                            </ul>
                            <button className="w-full btn-secondary">Contact Sales</button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 bg-slate-900 text-slate-400">
                <div className="max-w-6xl mx-auto">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-2">
                            <Mail className="w-6 h-6 text-primary-400" />
                            <span className="text-lg font-semibold text-white">EDI.email</span>
                        </div>
                        <div className="flex gap-6">
                            <a href="#" className="hover:text-white transition-colors">Privacy</a>
                            <a href="#" className="hover:text-white transition-colors">Terms</a>
                            <a href="#" className="hover:text-white transition-colors">Support</a>
                        </div>
                    </div>
                    <div className="mt-8 pt-8 border-t border-slate-800 text-center">
                        <p>© 2024 EDI.email. The Mailchimp of EDI.</p>
                    </div>
                </div>
            </footer>
        </main>
    );
}
