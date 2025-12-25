import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "EDI.email - Transform EDI Files to PDF, Excel, HTML",
    description: "Convert complex EDI files into human-readable formats (PDF, Excel, HTML) through email automation. Forward EDI files, get readable PDFs back in seconds.",
    keywords: ["EDI", "EDI converter", "EDI to PDF", "EDI to Excel", "850", "810", "856", "purchase order", "invoice", "ASN"],
    authors: [{ name: "EDI.email" }],
    openGraph: {
        title: "EDI.email - Transform EDI Files to PDF, Excel, HTML",
        description: "Forward EDI files. Get readable PDFs. That's it.",
        url: "https://edi.email",
        siteName: "EDI.email",
        type: "website",
    },
    twitter: {
        card: "summary_large_image",
        title: "EDI.email - Transform EDI Files to PDF, Excel, HTML",
        description: "Forward EDI files. Get readable PDFs. That's it.",
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                {children}
            </body>
        </html>
    );
}
