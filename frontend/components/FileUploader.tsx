"use client";

import { useState, useCallback, useRef } from "react";
import { FileUp, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface ConversionResult {
    id: string;
    status: "success" | "error";
    transactionType: string;
    transactionName: string;
    processingTime: number;
    downloads: {
        pdf?: string;
        excel?: string;
        html?: string;
    };
}

interface FileUploaderProps {
    onConversionComplete?: (result: ConversionResult) => void;
}

export function FileUploader({ onConversionComplete }: FileUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ConversionResult | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

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

            // Call the backend API
            const response = await fetch("/api/v1/convert", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Conversion failed");
            }

            const data = await response.json();

            // For now, simulate a successful response since backend isn't fully wired
            const mockResult: ConversionResult = {
                id: data.id || `conv_${Date.now()}`,
                status: "success",
                transactionType: data.transactionType || "850",
                transactionName: data.transactionName || "Purchase Order",
                processingTime: data.processingTime || 1234,
                downloads: {
                    pdf: data.downloads?.pdf || "#",
                    excel: data.downloads?.excel || "#",
                    html: data.downloads?.html || "#",
                },
            };

            setResult(mockResult);
            onConversionComplete?.(mockResult);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setIsUploading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    // Show result view
    if (result) {
        return (
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-green-200">
                <div className="text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Conversion Complete!</h3>
                    <p className="text-slate-600 mb-6">
                        {result.transactionName} (EDI {result.transactionType}) processed in{" "}
                        {(result.processingTime / 1000).toFixed(2)}s
                    </p>

                    {/* Download buttons */}
                    <div className="flex flex-wrap justify-center gap-3 mb-6">
                        {result.downloads.pdf && (
                            <a
                                href={result.downloads.pdf}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
                            >
                                <FileUp className="w-4 h-4" />
                                Download PDF
                            </a>
                        )}
                        {result.downloads.excel && (
                            <a
                                href={result.downloads.excel}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
                            >
                                <FileUp className="w-4 h-4" />
                                Download Excel
                            </a>
                        )}
                        {result.downloads.html && (
                            <a
                                href={result.downloads.html}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
                            >
                                <FileUp className="w-4 h-4" />
                                View HTML
                            </a>
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
        </div>
    );
}
