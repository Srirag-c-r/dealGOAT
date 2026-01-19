import React, { useState, useEffect } from 'react';
import StatCard from '../../components/admin/StatCard';
import {
    Users,
    FileText,
    TrendingUp,
    MessageSquare,
    AlertTriangle,
    CheckCircle,
    Clock,
    ShoppingCart
} from 'lucide-react';
import { adminAPI } from '../../services/adminApi';

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardStats();
    }, []);

    const fetchDashboardStats = async () => {
        try {
            console.log('Fetching dashboard stats...');

            const response = await adminAPI.getDashboardStats();

            console.log('Dashboard stats received:', response.data);
            setStats(response.data);
            setLoading(false);
        } catch (err) {
            console.error('Dashboard stats error:', err);
            console.error('Error response:', err.response);

            let errorMessage = 'Failed to fetch dashboard stats';

            if (err.response) {
                // Server responded with error
                if (err.response.status === 401) {
                    errorMessage = 'Unauthorized. Please logout and login again.';
                } else if (err.response.status === 403) {
                    errorMessage = 'Access forbidden. You need admin privileges.';
                } else if (err.response.data?.error) {
                    errorMessage = err.response.data.error;
                }
            } else if (err.request) {
                // Request made but no response
                errorMessage = 'Cannot connect to server. Make sure backend is running on http://localhost:8000';
            } else {
                // Something else happened
                errorMessage = err.message;
            }

            setError(errorMessage);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Dashboard</h2>
                <p className="text-red-800 mb-4">{error}</p>
                <div className="space-y-2 text-sm text-red-700">
                    <p><strong>Troubleshooting:</strong></p>
                    <ul className="list-disc list-inside space-y-1">
                        <li>Make sure backend server is running: <code className="bg-red-100 px-2 py-1 rounded">python manage.py runserver</code></li>
                        <li>Check if you're logged in with admin account</li>
                        <li>Try logging out and logging in again</li>
                        <li>Open browser console (F12) for more details</li>
                    </ul>
                </div>
                <button
                    onClick={() => {
                        setLoading(true);
                        setError(null);
                        fetchDashboardStats();
                    }}
                    className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
                <p className="text-gray-600 mt-1">Welcome back! Here's what's happening with DealGoat.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Users"
                    value={stats?.users?.total?.toLocaleString() || '0'}
                    change={stats?.users?.new_7d}
                    icon={Users}
                    color="blue"
                    trend="up"
                />
                <StatCard
                    title="Active Listings"
                    value={stats?.listings?.active?.toLocaleString() || '0'}
                    change={stats?.listings?.recent_7d}
                    icon={FileText}
                    color="green"
                    trend="up"
                />
                <StatCard
                    title="Pending Moderation"
                    value={stats?.listings?.pending_moderation?.toLocaleString() || '0'}
                    icon={Clock}
                    color="yellow"
                />
                <StatCard
                    title="Flagged Items"
                    value={stats?.listings?.flagged?.toLocaleString() || '0'}
                    icon={AlertTriangle}
                    color="red"
                />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Predictions"
                    value={stats?.predictions?.total?.toLocaleString() || '0'}
                    icon={TrendingUp}
                    color="purple"
                />
                <StatCard
                    title="Active Conversations"
                    value={stats?.messaging?.active_conversations_7d?.toLocaleString() || '0'}
                    icon={MessageSquare}
                    color="indigo"
                />
                <StatCard
                    title="Verified Users"
                    value={stats?.users?.verified?.toLocaleString() || '0'}
                    icon={CheckCircle}
                    color="green"
                />
                <StatCard
                    title="Sold Listings"
                    value={stats?.listings?.sold?.toLocaleString() || '0'}
                    icon={ShoppingCart}
                    color="blue"
                />
            </div>

            {/* Quick Actions & Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
                    <div className="space-y-3">
                        <button className="w-full flex items-center justify-between px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
                            <span className="font-medium text-red-900">Review Pending Listings</span>
                            <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm">
                                {stats?.listings?.pending_moderation || 0}
                            </span>
                        </button>
                        <button className="w-full flex items-center justify-between px-4 py-3 bg-yellow-50 hover:bg-yellow-100 rounded-lg transition-colors">
                            <span className="font-medium text-yellow-900">Check Flagged Items</span>
                            <span className="bg-yellow-600 text-white px-3 py-1 rounded-full text-sm">
                                {stats?.listings?.flagged || 0}
                            </span>
                        </button>
                        <button className="w-full flex items-center justify-between px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
                            <span className="font-medium text-blue-900">Run Fraud Detection</span>
                            <span className="text-blue-600 text-sm">→</span>
                        </button>
                        <button className="w-full flex items-center justify-between px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
                            <span className="font-medium text-green-900">Generate Report</span>
                            <span className="text-green-600 text-sm">→</span>
                        </button>
                    </div>
                </div>

                {/* System Status */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-gray-700">API Status</span>
                            </div>
                            <span className="text-green-600 font-medium">Operational</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-gray-700">Database</span>
                            </div>
                            <span className="text-green-600 font-medium">Connected</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-gray-700">ML Models</span>
                            </div>
                            <span className="text-green-600 font-medium">Active</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                <span className="text-gray-700">Fraud Detection</span>
                            </div>
                            <span className="text-yellow-600 font-medium">Monitoring</span>
                        </div>
                    </div>

                    <div className="mt-6 pt-4 border-t border-gray-200">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Admin Actions (7d)</span>
                            <span className="font-bold text-gray-900">
                                {stats?.admin_activity?.actions_7d || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between text-sm mt-2">
                            <span className="text-gray-600">Verification Rate</span>
                            <span className="font-bold text-gray-900">
                                {stats?.users?.verification_rate || 0}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* User & Listing Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* User Stats */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">User Statistics</h2>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Active (7 days)</span>
                            <span className="font-bold text-blue-600">
                                {stats?.users?.active_7d?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Active (30 days)</span>
                            <span className="font-bold text-blue-600">
                                {stats?.users?.active_30d?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Suspended</span>
                            <span className="font-bold text-red-600">
                                {stats?.users?.suspended?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">New (7 days)</span>
                            <span className="font-bold text-green-600">
                                {stats?.users?.new_7d?.toLocaleString() || 0}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Prediction Stats */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Prediction Breakdown</h2>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Laptop Predictions</span>
                            <span className="font-bold text-purple-600">
                                {stats?.predictions?.laptop?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Smartphone Predictions</span>
                            <span className="font-bold text-purple-600">
                                {stats?.predictions?.smartphone?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Recent (7 days)</span>
                            <span className="font-bold text-green-600">
                                {stats?.predictions?.recent_7d?.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-700">Total Queries</span>
                            <span className="font-bold text-indigo-600">
                                {stats?.recommendations?.total_queries?.toLocaleString() || 0}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
