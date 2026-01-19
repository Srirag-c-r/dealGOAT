import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * Protected Route Component
 * Ensures only authenticated admin users can access admin routes
 */
const ProtectedAdminRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // Check if user is authenticated
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // Check if user has admin privileges
    if (!user.is_staff && !user.is_superuser) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
                    <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
                    <p className="text-gray-700 mb-4">
                        You do not have permission to access the admin dashboard.
                    </p>
                    <a
                        href="/user-home"
                        className="inline-block px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                        Go to Home
                    </a>
                </div>
            </div>
        );
    }

    return children;
};

export default ProtectedAdminRoute;
