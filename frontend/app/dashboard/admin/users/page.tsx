"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Users, Shield, User, ArrowLeft, Loader2, Trash2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/api-config";

interface UserInfo {
    id: string;
    email: string;
    name: string | null;
    role: string;
    created_at: string;
}

export default function UserManagementPage() {
    const [users, setUsers] = useState<UserInfo[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deletingUserId, setDeletingUserId] = useState<string | null>(null);
    const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/users`);
            if (!response.ok) throw new Error("Failed to fetch users");
            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setIsLoading(false);
        }
    };

    const updateRole = async (userId: string, newRole: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}/role`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role: newRole }),
            });
            if (!response.ok) throw new Error("Failed to update role");
            fetchUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Update failed");
        }
    };

    const deleteUser = async (userId: string) => {
        setDeletingUserId(userId);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
                method: "DELETE",
            });
            if (!response.ok) throw new Error("Failed to delete user");
            setConfirmDelete(null);
            fetchUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Delete failed");
        } finally {
            setDeletingUserId(null);
        }
    };

    const getRoleIcon = (role: string) => {
        switch (role) {
            case "superadmin": return <Shield className="w-4 h-4 text-purple-600" />;
            case "admin": return <Shield className="w-4 h-4 text-blue-600" />;
            default: return <User className="w-4 h-4 text-slate-400" />;
        }
    };

    const getRoleBadge = (role: string) => {
        switch (role) {
            case "superadmin": return "bg-purple-100 text-purple-700";
            case "admin": return "bg-blue-100 text-blue-700";
            default: return "bg-slate-100 text-slate-600";
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/dashboard/admin/layouts" className="p-2 hover:bg-slate-100 rounded-lg">
                    <ArrowLeft className="w-5 h-5 text-slate-600" />
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                        <Users className="w-6 h-6" />
                        User Management
                    </h1>
                    <p className="text-slate-500">Manage users and their roles</p>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                    {error}
                </div>
            )}

            {/* Users Table */}
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <table className="w-full">
                    <thead className="bg-slate-50 border-b border-slate-200">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">User</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Role</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Joined</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {users.map((user) => (
                            <tr key={user.id} className="hover:bg-slate-50">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-medium">
                                            {(user.name || user.email).charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="font-medium text-slate-800">{user.name || "—"}</p>
                                            <p className="text-sm text-slate-500">{user.email}</p>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getRoleBadge(user.role)}`}>
                                        {getRoleIcon(user.role)}
                                        {user.role || "user"}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-500">
                                    {new Date(user.created_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        <select
                                            value={user.role || "user"}
                                            onChange={(e) => updateRole(user.id, e.target.value)}
                                            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="user">User</option>
                                            <option value="admin">Admin</option>
                                            <option value="superadmin">Superadmin</option>
                                        </select>

                                        {confirmDelete === user.id ? (
                                            <div className="flex items-center gap-1">
                                                <button
                                                    onClick={() => deleteUser(user.id)}
                                                    disabled={deletingUserId === user.id}
                                                    className="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded font-medium disabled:opacity-50"
                                                >
                                                    {deletingUserId === user.id ? "..." : "Confirm"}
                                                </button>
                                                <button
                                                    onClick={() => setConfirmDelete(null)}
                                                    className="px-2 py-1 text-xs bg-slate-200 hover:bg-slate-300 text-slate-700 rounded font-medium"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => setConfirmDelete(user.id)}
                                                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                                title="Delete user"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {users.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                                    No users found
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Role Legend */}
            <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm font-medium text-slate-700 mb-3">Role Permissions</p>
                <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="flex items-start gap-2">
                        <Shield className="w-4 h-4 text-purple-600 mt-0.5" />
                        <div>
                            <p className="font-medium text-slate-800">Superadmin</p>
                            <p className="text-slate-500">Full access, manage defaults & users</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-2">
                        <Shield className="w-4 h-4 text-blue-600 mt-0.5" />
                        <div>
                            <p className="font-medium text-slate-800">Admin</p>
                            <p className="text-slate-500">Edit layouts, limited management</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-2">
                        <User className="w-4 h-4 text-slate-400 mt-0.5" />
                        <div>
                            <p className="font-medium text-slate-800">User</p>
                            <p className="text-slate-500">Customize own layouts only</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
