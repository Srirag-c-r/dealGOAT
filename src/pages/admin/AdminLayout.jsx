import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import AdminSidebar from '../../components/admin/AdminSidebar';
import { Menu, Bell, User } from 'lucide-react';

const AdminLayout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <AdminSidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Header */}
                <header className="bg-white shadow-sm z-10">
                    <div className="flex items-center justify-between px-6 py-4">
                        {/* Mobile menu button */}
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="lg:hidden text-gray-600 hover:text-gray-900"
                        >
                            <Menu className="w-6 h-6" />
                        </button>

                        {/* Search bar (placeholder) */}
                        <div className="flex-1 max-w-2xl mx-4">
                            <input
                                type="text"
                                placeholder="Search users, listings, or actions..."
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg
                         focus:outline-none focus:ring-2 focus:ring-red-500"
                            />
                        </div>

                        {/* Right side icons */}
                        <div className="flex items-center space-x-4">
                            {/* Notifications */}
                            <button className="relative text-gray-600 hover:text-gray-900">
                                <Bell className="w-6 h-6" />
                                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-600 
                               rounded-full text-xs text-white flex items-center justify-center">
                                    3
                                </span>
                            </button>

                            {/* User profile */}
                            <div className="flex items-center space-x-3">
                                <div className="text-right hidden sm:block">
                                    <p className="text-sm font-medium text-gray-900">
                                        {user.first_name || 'Admin'} {user.last_name || 'User'}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {user.is_superuser ? 'Super Admin' : 'Moderator'}
                                    </p>
                                </div>
                                <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center">
                                    <User className="w-6 h-6 text-white" />
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-y-auto p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;
