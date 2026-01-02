import React, { useState, useRef, useEffect } from "react";
import { X } from "lucide-react";

interface EmailInputProps {
    value: string[];
    onChange: (emails: string[]) => void;
    placeholder?: string;
    className?: string;
}

export default function EmailInput({ value, onChange, placeholder, className = "" }: EmailInputProps) {
    const [inputValue, setInputValue] = useState("");
    const [error, setError] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const isValidEmail = (email: string) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (["Enter", "Tab", ","].includes(e.key)) {
            e.preventDefault();
            addEmail();
        } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
            // Remove last email if input is empty
            const newEmails = [...value];
            newEmails.pop();
            onChange(newEmails);
        }
    };

    const handleBlur = () => {
        if (inputValue) {
            addEmail();
        }
    };

    const addEmail = () => {
        const email = inputValue.trim().replace(/,$/, "");

        if (!email) return;

        if (!isValidEmail(email)) {
            setError(`Invalid email: ${email}`);
            return;
        }

        if (value.includes(email)) {
            setError(`Email already added: ${email}`);
            setInputValue("");
            return;
        }

        onChange([...value, email]);
        setInputValue("");
        setError(null);
    };

    const removeEmail = (emailToRemove: string) => {
        onChange(value.filter(email => email !== emailToRemove));
    };

    return (
        <div className={`space-y-1 ${className}`}>
            <div
                className="flex flex-wrap items-center gap-2 p-2 border border-slate-300 rounded-lg bg-white focus-within:ring-2 focus-within:ring-blue-500 min-h-[42px]"
                onClick={() => inputRef.current?.focus()}
            >
                {value.map((email) => (
                    <div
                        key={email}
                        className="flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-sm rounded-md border border-blue-100"
                    >
                        <span>{email}</span>
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation();
                                removeEmail(email);
                            }}
                            className="p-0.5 hover:bg-blue-100 rounded-full text-blue-500 hover:text-blue-700 transition-colors"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </div>
                ))}

                <input
                    ref={inputRef}
                    type="text"
                    className="flex-1 outline-none min-w-[120px] text-sm py-1"
                    placeholder={value.length === 0 ? (placeholder || "Enter email addresses...") : ""}
                    value={inputValue}
                    onChange={(e) => {
                        setInputValue(e.target.value);
                        setError(null);
                    }}
                    onKeyDown={handleKeyDown}
                    onBlur={handleBlur}
                />
            </div>
            {error && <p className="text-xs text-red-500 ml-1">{error}</p>}
        </div>
    );
}
