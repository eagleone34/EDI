"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import { usePathname } from "next/navigation";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { user, isLoading } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // If we know user is loaded
        if (!isLoading && user) {
            // Block generic users from /admin/users
            if (pathname?.includes('/admin/users') && user.role !== 'superadmin') {
                router.push('/dashboard/admin/layouts'); // or 404
            }
        }
    }, [user, isLoading, router, pathname]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    // Explicit block for specific restricted routes
    if (pathname?.includes('/admin/users') && user?.role !== 'superadmin') {
        return null;
    }

    return <>{children}</>;
}
