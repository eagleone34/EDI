import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "ReadableEDI - Transform Complex EDI Files to PDF, Excel, HTML",
    description: "Convert complex EDI files into human-readable formats (PDF, Excel, HTML) through email automation. Upload EDI files, get readable PDFs back in seconds.",
    keywords: ["EDI", "EDI converter", "EDI to PDF", "EDI to Excel", "850", "810", "856", "purchase order", "invoice", "ASN", "ReadableEDI"],
    authors: [{ name: "ReadableEDI" }],
    openGraph: {
        title: "ReadableEDI - Transform Complex EDI Files to PDF, Excel, HTML",
        description: "Upload EDI files. Get readable PDFs. That's it.",
        url: "https://readableedi.com",
        siteName: "ReadableEDI",
        type: "website",
    },
    twitter: {
        card: "summary_large_image",
        title: "ReadableEDI - Transform Complex EDI Files to PDF, Excel, HTML",
        description: "Upload EDI files. Get readable PDFs. That's it.",
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={inter.className} suppressHydrationWarning>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}

