import React, { useState, useEffect } from 'react';
import {
    Shield, UserPlus, Users, Crown, Trash2, ArrowUp, ArrowDown,
    Search, RefreshCw, AlertTriangle, CheckCircle, XCircle
} from 'lucide-react';

const AdminManagement = () => {
    const [admins, setAdmins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [stats, setStats] = useState({ total: 0, super_admins: 0, regular_admins: 0 });

    useEffect(() => {
        fetchAdmins();
    }, []);

    const fetchAdmins = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/auth/admin/admins/list/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to fetch admins');

            const data = await response.json();
            setAdmins(data.admins || []);
            setStats({
                total: data.total || 0,
                super_admins: data.super_admins || 0,
                regular_admins: data.regular_admins || 0
            });
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch admins:', err);
            setError('Failed to load admin users');
            setLoading(false);
        }
    };

    const handlePromote = async (userId, toSuperuser = false) => {
        if (!confirm(`Are you sure you want to promote this user to ${toSuperuser ? 'Super Admin' : 'Admin'}?`)) return;

        try {
            const response = await fetch(`http://localhost:8000/api/auth/admin/admins/${userId}/promote/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ to_superuser: toSuperuser })
            });

            if (!response.ok) throw new Error('Failed to promote user');

            alert('User promoted successfully!');
            fetchAdmins();
        } catch (err) {
            alert('Failed to promote user');
        }
    };

    const handleDemote = async (userId) => {
        if (!confirm('Are you sure you want to demote this admin to a regular user?')) return;

        try {
            const response = await fetch(`http://localhost:8000/api/auth/admin/admins/${userId}/demote/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to demote admin');

            alert('Admin demoted successfully!');
            fetchAdmins();
        } catch (err) {
            alert('Failed to demote admin');
        }
    };

    const handleDelete = async (userId, email) => {
        if (!confirm(`⚠️ WARNING: This will permanently delete the admin user "${email}". Type DELETE to confirm.`)) return;

        const confirmText = prompt('Type DELETE to confirm:');
        if (confirmText !== 'DELETE') {
            alert('Deletion cancelled');
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/api/auth/admin/admins/${userId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to delete admin');

            alert('Admin deleted successfully!');
            fetchAdmins();
        } catch (err) {
            alert('Failed to delete admin');
        }
    };

    const filteredAdmins = admins.filter(admin =>
        admin.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        `${admin.first_name} ${admin.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
                <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Admins</h2>
                <p className="text-red-800 mb-4">{error}</p>
                <button
                    onClick={fetchAdmins}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Admin Management</h1>
                    <p className="text-gray-600 mt-1">Manage admin users and permissions</p>
                </div>
                <div className="flex items-center space-x-3">
                    <button
                        onClick={fetchAdmins}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Refresh</span>
                    </button>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2"
                    >
                        <UserPlus className="w-4 h-4" />
                        <span>Create Admin</span>
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-600 text-sm">Total Admins</p>
                            <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
                        </div>
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <Users className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-600 text-sm">Super Admins</p>
                            <p className="text-3xl font-bold text-gray-900 mt-1">{stats.super_admins}</p>
                        </div>
                        <div className="p-3 bg-red-100 rounded-lg">
                            <Crown className="w-6 h-6 text-red-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-600 text-sm">Regular Admins</p>
                            <p className="text-3xl font-bold text-gray-900 mt-1">{stats.regular_admins}</p>
                        </div>
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <Shield className="w-6 h-6 text-yellow-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="bg-white rounded-lg shadow-md p-4">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search by email or name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                </div>
            </div>

            {/* Admins Table */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Admin
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Role
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Joined
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredAdmins.map((admin) => (
                            <tr key={admin.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0 h-10 w-10 bg-red-600 rounded-full flex items-center justify-center">
                                            <span className="text-white font-medium">
                                                {admin.first_name?.[0] || admin.email[0].toUpperCase()}
                                            </span>
                                        </div>
                                        <div className="ml-4">
                                            <div className="text-sm font-medium text-gray-900">
                                                {admin.first_name} {admin.last_name}
                                            </div>
                                            <div className="text-sm text-gray-500">{admin.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {admin.is_superuser ? (
                                        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                            <Crown className="w-3 h-3 mr-1" />
                                            Super Admin
                                        </span>
                                    ) : (
                                        <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                            <Shield className="w-3 h-3 mr-1" />
                                            Admin
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {admin.is_suspended ? (
                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                            <XCircle className="w-3 h-3 mr-1" />
                                            Suspended
                                        </span>
                                    ) : (
                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                            <CheckCircle className="w-3 h-3 mr-1" />
                                            Active
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(admin.date_joined).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <div className="flex items-center justify-end space-x-2">
                                        {!admin.is_superuser && (
                                            <button
                                                onClick={() => handlePromote(admin.id, true)}
                                                className="text-blue-600 hover:text-blue-900"
                                                title="Promote to Super Admin"
                                            >
                                                <ArrowUp className="w-4 h-4" />
                                            </button>
                                        )}
                                        {admin.is_staff && (
                                            <button
                                                onClick={() => handleDemote(admin.id)}
                                                className="text-yellow-600 hover:text-yellow-900"
                                                title="Demote to Regular User"
                                            >
                                                <ArrowDown className="w-4 h-4" />
                                            </button>
                                        )}
                                        <button
                                            onClick={() => handleDelete(admin.id, admin.email)}
                                            className="text-red-600 hover:text-red-900"
                                            title="Delete Admin"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {filteredAdmins.length === 0 && (
                    <div className="text-center py-12">
                        <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Admins Found</h3>
                        <p className="text-gray-600">
                            {searchTerm ? 'No admins match your search.' : 'No admin users have been created yet.'}
                        </p>
                    </div>
                )}
            </div>

            {/* Create Admin Modal */}
            {showCreateModal && (
                <CreateAdminModal
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={() => {
                        setShowCreateModal(false);
                        fetchAdmins();
                    }}
                />
            )}

            {/* Info Box */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                        <h4 className="font-medium text-yellow-900">Security Notice</h4>
                        <p className="text-sm text-yellow-800 mt-1">
                            Only Super Admins can manage admin users. Be careful when promoting or demoting admins.
                            You cannot demote or delete yourself.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Create Admin Modal Component
const CreateAdminModal = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        is_superuser: false
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/auth/admin/admins/create/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to create admin');
            }

            alert('Admin created successfully!');
            onSuccess();
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New Admin</h2>

                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                        <p className="text-sm text-red-800">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                        <input
                            type="email"
                            required
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                        <input
                            type="password"
                            required
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                            <input
                                type="text"
                                value={formData.first_name}
                                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input
                                type="text"
                                value={formData.last_name}
                                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_superuser"
                            checked={formData.is_superuser}
                            onChange={(e) => setFormData({ ...formData, is_superuser: e.target.checked })}
                            className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                        />
                        <label htmlFor="is_superuser" className="ml-2 text-sm text-gray-700">
                            Create as Super Admin
                        </label>
                    </div>

                    <div className="flex items-center justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating...' : 'Create Admin'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminManagement;
