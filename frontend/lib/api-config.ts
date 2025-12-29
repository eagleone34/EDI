// API Configuration
// This file provides the API URL for both development and production environments

const getApiUrl = (): string => {
    // Check for environment variable first
    if (typeof window !== 'undefined') {
        // Client-side: check for env var or use production URL
        return process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app';
    }
    // Server-side
    return process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app';
};

export const API_URL = getApiUrl();

// Export for direct use
export const API_BASE_URL = 'https://edi-production.up.railway.app';
