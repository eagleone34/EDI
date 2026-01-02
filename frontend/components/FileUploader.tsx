"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { FileUp, X, CheckCircle, AlertCircle, Loader2, ChevronDown, Lock } from "lucide-react";
import { EmailGateModal } from "./EmailGateModal";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";

interface ConversionResult {
    id: string;
    status: "success" | "error";
    transactionType: string;
    transactionName: string;
    transactionCount?: number;
    processingTime: number;
    downloads: {
        pdf?: string;
        excel?: string;
        html?: string;
    };
    // Smart detection fields
    detectedType?: string;
    selectedType?: string;
    typeMismatch?: boolean;
    warning?: string;
}

interface FileUploaderProps {
    onConversionComplete?: (result: ConversionResult) => void;
}

const TRANSACTION_TYPES = [
    { code: "850", name: "Purchase Order" },
    { code: "810", name: "Invoice" },
    { code: "812", name: "Credit/Debit Adjustment" },
    { code: "856", name: "Advance Ship Notice (ASN)" },
    { code: "855", name: "Purchase Order Acknowledgment" },
    { code: "997", name: "Functional Acknowledgment" },
];

export function FileUploader({ onConversionComplete }: FileUploaderProps) {
    const router = useRouter();
    const { user, isAuthenticated } = useAuth();
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [transactionType, setTransactionType] = useState("850");
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ConversionResult | null>(null);
    const [isVerified, setIsVerified] = useState(false);
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [pendingDownload, setPendingDownload] = useState<{ url: string; filename: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Check if already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            setIsVerified(true);
        }
    }, [isAuthenticated]);

    const allowedExtensions = [".edi", ".txt", ".x12", ".dat"];

    const validateFile = (file: File): boolean => {
        const extension = "." + file.name.split(".").pop()?.toLowerCase();
        if (!allowedExtensions.includes(extension)) {
            setError(`Invalid file type. Allowed: ${allowedExtensions.join(", ")}`);
            return false;
        }
        if (file.size > 10 * 1024 * 1024) {
            setError("File too large. Maximum size: 10MB");
            return false;
        }
        return true;
    };

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);
        setResult(null);

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && validateFile(droppedFile)) {
            setFile(droppedFile);
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        setError(null);
        setResult(null);
        const selectedFile = e.target.files?.[0];
        if (selectedFile && validateFile(selectedFile)) {
            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("formats", "pdf,excel,html");
            formData.append("transaction_type", transactionType);

            // Try calling the real backend API
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app';
            const response = await fetch(`${apiUrl}/api/v1/convert/`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = "Conversion failed";
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    if (errorText.includes("Internal Server Error")) {
                        throw new Error("Backend not running");
                    }
                    errorMessage = errorText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();

            const apiResult: ConversionResult = {
                id: data.id || `conv_${Date.now()}`,
                status: "success",
                transactionType: data.transactionType || "850",
                transactionName: data.transactionName || "Purchase Order",
                transactionCount: data.transactionCount || 1,
                processingTime: data.processingTime || 1000,
                downloads: {
                    pdf: data.outputs?.pdf ? `data:application/pdf;base64,${data.outputs.pdf}` : undefined,
                    excel: data.outputs?.excel ? `data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,${data.outputs.excel}` : undefined,
                    html: data.outputs?.html ? `data:text/html;base64,${data.outputs.html}` : undefined,
                },
                // Smart detection info
                detectedType: data.detectedType,
                selectedType: data.selectedType,
                typeMismatch: data.typeMismatch,
                warning: data.warning,
            };

            setResult(apiResult);
            onConversionComplete?.(apiResult);

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "An error occurred";

            // If backend not running, fall back to demo mode
            if (errorMessage.includes("Backend not running") || errorMessage.includes("fetch")) {
                await runDemoMode();
            } else {
                setError(errorMessage);
            }
        } finally {
            setIsUploading(false);
        }
    };

    const runDemoMode = async () => {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Detect transaction type from filename
        const filename = file!.name.toLowerCase();
        let transactionType = "850";
        let transactionName = "Purchase Order";

        if (filename.includes("810") || filename.includes("invoice")) {
            transactionType = "810";
            transactionName = "Invoice";
        } else if (filename.includes("812") || filename.includes("credit") || filename.includes("debit") || filename.includes("adjustment")) {
            transactionType = "812";
            transactionName = "Credit/Debit Adjustment";
        } else if (filename.includes("856") || filename.includes("asn") || filename.includes("ship")) {
            transactionType = "856";
            transactionName = "Advance Ship Notice";
        } else if (filename.includes("855") || filename.includes("ack")) {
            transactionType = "855";
            transactionName = "Purchase Order Acknowledgment";
        } else if (filename.includes("997") || filename.includes("func")) {
            transactionType = "997";
            transactionName = "Functional Acknowledgment";
        }

        const demoResult: ConversionResult = {
            id: `demo_${Date.now()}`,
            status: "success",
            transactionType,
            transactionName,
            processingTime: 1234 + Math.random() * 500,
            downloads: {
                pdf: "#demo-pdf",
                excel: "#demo-excel",
                html: "#demo-html",
            },
        };

        setResult(demoResult);
        onConversionComplete?.(demoResult);
    };

    const handleReset = () => {
        setFile(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    // Helper function to download base64 data as a file
    const handleDownload = (dataUrl: string, filename: string) => {
        console.log("handleDownload called", { dataUrl: dataUrl.substring(0, 50), filename, isVerified });

        if (dataUrl.startsWith("#")) {
            alert("Demo mode: Downloads not available");
            return;
        }

        // Check if user is verified
        if (!isVerified) {
            console.log("Not verified, showing email modal");
            setPendingDownload({ url: dataUrl, filename });
            setShowEmailModal(true);
            console.log("showEmailModal set to true");
            return;
        }

        performDownload(dataUrl, filename);
    };

    const performDownload = (dataUrl: string, filename: string) => {

        // Extract base64 data from data URL
        const base64Match = dataUrl.match(/base64,(.+)/);
        if (!base64Match) {
            console.error("Invalid data URL format");
            return;
        }

        const base64Data = base64Match[1];

        // Determine MIME type based on filename extension
        let mimeType = "application/octet-stream";
        if (filename.endsWith(".pdf") || filename.endsWith(".html")) {
            mimeType = "text/html"; // PDF is actually HTML for now
        } else if (filename.endsWith(".xlsx")) {
            mimeType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        }

        try {
            // Convert base64 to blob
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: mimeType });

            // Use saveAs-like approach
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.style.display = "none";
            link.href = url;
            link.setAttribute("download", filename);

            // Append to body and click
            document.body.appendChild(link);
            link.click();

            // Cleanup after a delay
            setTimeout(() => {
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }, 100);
        } catch (error) {
            console.error("Download failed:", error);
            alert("Download failed. Please try again.");
        }
    };

    // Show result view
    if (result) {
        const isDemoMode = result.id.startsWith("demo_");
        const baseFilename = file?.name.replace(/\.[^.]+$/, "") || "converted";

        return (
            <>
                <div className="bg-white rounded-2xl p-8 shadow-lg border border-green-200">
                    <div className="text-center">
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle className="w-8 h-8 text-green-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Conversion Complete!</h3>
                        {isDemoMode && (
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium mb-4">
                                🎭 Demo Mode - Backend not connected
                            </div>
                        )}
                        {/* Type mismatch warning */}
                        {result.typeMismatch && result.warning && (
                            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3 max-w-lg mx-auto">
                                <span className="text-lg">⚠️</span>
                                <div className="text-left">
                                    <p className="font-medium text-amber-800">Document Type Auto-Corrected</p>
                                    <p className="text-sm text-amber-700 mt-1">{result.warning}</p>
                                </div>
                            </div>
                        )}
                        {(result.transactionCount ?? 1) > 1 && (
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
                                📦 Found {result.transactionCount} {result.transactionName}s in this file
                            </div>
                        )}
                        <p className="text-slate-600 mb-6">
                            {(result.transactionCount ?? 1) > 1
                                ? `${result.transactionCount} ${result.transactionName}s processed in `
                                : `${result.transactionName} (EDI ${result.transactionType}) processed in `}
                            {(result.processingTime / 1000).toFixed(2)}s
                        </p>

                        {/* Download buttons */}
                        <div className="flex flex-wrap justify-center gap-3 mb-6">
                            {result.downloads.pdf && (
                                <button
                                    onClick={() => handleDownload(result.downloads.pdf!, `${baseFilename}.pdf`)}
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
                                >
                                    <FileUp className="w-4 h-4" />
                                    Download PDF
                                </button>
                            )}
                            {result.downloads.excel && (
                                <button
                                    onClick={() => handleDownload(result.downloads.excel!, `${baseFilename}.xlsx`)}
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
                                >
                                    <FileUp className="w-4 h-4" />
                                    Download Excel
                                </button>
                            )}
                            {result.downloads.html && (
                                <button
                                    onClick={() => handleDownload(result.downloads.html!, `${baseFilename}.html`)}
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
                                >
                                    <FileUp className="w-4 h-4" />
                                    Download HTML
                                </button>
                            )}
                        </div>

                        <button
                            onClick={handleReset}
                            className="text-slate-500 hover:text-slate-700 transition-colors"
                        >
                            Convert another file
                        </button>
                    </div>
                </div>

                {/* Email Gate Modal - must be here for result view */}
                <EmailGateModal
                    isOpen={showEmailModal}
                    onClose={() => {
                        setShowEmailModal(false);
                        setPendingDownload(null);
                    }}
                    onVerified={async (userData) => {
                        setIsVerified(true);
                        setShowEmailModal(false);

                        // Capture result for TypeScript (result is guaranteed non-null here)
                        const currentResult = result;
                        const currentFile = file;

                        // Save document to Supabase
                        if (currentResult && userData.userId) {
                            try {
                                await supabase.from("documents").insert({
                                    user_id: userData.userId,
                                    filename: currentFile?.name || "unknown.edi",
                                    transaction_type: currentResult.transactionType,
                                    transaction_name: currentResult.transactionName,
                                    transaction_count: currentResult.transactionCount || 1,
                                });
                            } catch (err) {
                                console.error("Failed to save document:", err);
                            }
                        }

                        // Process pending download
                        if (pendingDownload) {
                            performDownload(pendingDownload.url, pendingDownload.filename);
                            setPendingDownload(null);
                        }
                    }}
                    pendingDownload={pendingDownload ? () => {
                        if (pendingDownload) {
                            performDownload(pendingDownload.url, pendingDownload.filename);
                        }
                    } : undefined}
                />
            </>
        );
    }

    return (
        <div className="bg-white rounded-2xl p-8 shadow-lg">
            {/* Drop zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
          relative rounded-xl p-12 text-center cursor-pointer transition-all duration-200
          border-2 border-dashed
          ${isDragging
                        ? "border-primary-500 bg-primary-50"
                        : file
                            ? "border-green-400 bg-green-50"
                            : "border-slate-300 hover:border-primary-400 hover:bg-slate-50"
                    }
        `}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".edi,.txt,.x12,.dat"
                    onChange={handleFileSelect}
                />

                {file ? (
                    <div className="flex items-center justify-center gap-4">
                        <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <FileUp className="w-6 h-6 text-green-600" />
                        </div>
                        <div className="text-left">
                            <p className="font-medium text-slate-900">{file.name}</p>
                            <p className="text-sm text-slate-500">
                                {(file.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleReset();
                            }}
                            className="ml-4 p-2 hover:bg-slate-100 rounded-full transition-colors"
                        >
                            <X className="w-5 h-5 text-slate-400" />
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <FileUp className={`w-8 h-8 ${isDragging ? "text-primary-600" : "text-slate-400"}`} />
                        </div>
                        <h3 className="text-xl font-semibold mb-2">
                            {isDragging ? "Drop your file here" : "Drag & drop your EDI file"}
                        </h3>
                        <p className="text-slate-500 mb-4">or click to browse</p>
                        <p className="text-xs text-slate-400">
                            Supports: .edi, .txt, .x12, .dat (max 10MB)
                        </p>
                    </>
                )}
            </div>

            {/* Error message */}
            {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            {/* Convert button */}
            {file && !error && (
                <div className="mt-6 text-center">
                    {/* Transaction Type Selector */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Select Transaction Type
                        </label>
                        <div className="relative inline-block">
                            <select
                                value={transactionType}
                                onChange={(e) => setTransactionType(e.target.value)}
                                className="appearance-none px-4 py-2.5 pr-10 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white text-slate-700 font-medium min-w-[280px]"
                            >
                                {TRANSACTION_TYPES.map((type) => (
                                    <option key={type.code} value={type.code}>
                                        {type.code} - {type.name}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                        </div>
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={isUploading}
                        className={`
              inline-flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-lg
              transition-all duration-200
              ${isUploading
                                ? "bg-slate-300 cursor-not-allowed"
                                : "bg-primary-600 hover:bg-primary-700 text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5"
                            }
            `}
                    >
                        {isUploading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Converting...
                            </>
                        ) : (
                            <>
                                Convert to PDF, Excel & HTML
                            </>
                        )}
                    </button>
                    <p className="text-sm text-slate-500 mt-3">
                        Free users: 10 conversions remaining
                    </p>
                </div>
            )}

            {/* Email Gate Modal */}
            <EmailGateModal
                isOpen={showEmailModal}
                onClose={() => {
                    setShowEmailModal(false);
                    setPendingDownload(null);
                }}
                onVerified={async (userData) => {
                    setIsVerified(true);
                    setShowEmailModal(false);

                    // Process pending download
                    // Note: No document saving here since result is null in this render path
                    if (pendingDownload) {
                        performDownload(pendingDownload.url, pendingDownload.filename);
                        setPendingDownload(null);
                    }
                }}
            />
        </div>
    );
}

