import React, { useState, useEffect } from 'react';
import {
    Settings as SettingsIcon,
    Save,
    RefreshCw,
    Eye,
    EyeOff,
    Lock,
    Globe,
    Mail,
    Zap,
    Shield,
    Bell,
    Database
} from 'lucide-react';

const Settings = () => {
    const [settings, setSettings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [activeCategory, setActiveCategory] = useState('all');
    const [showSensitive, setShowSensitive] = useState({});
    const [editedValues, setEditedValues] = useState({});

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/api/recommendations/admin/settings/get/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to fetch settings');

            const data = await response.json();
            setSettings(data.settings || []);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch settings:', err);
            setError('Failed to load settings');
            setLoading(false);
        }
    };

    const handleSaveSetting = async (key, value) => {
        setSaving(true);
        try {
            const response = await fetch('http://localhost:8000/api/recommendations/admin/settings/update/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ key, value })
            });

            if (!response.ok) throw new Error('Failed to update setting');

            // Refresh settings
            await fetchSettings();

            // Clear edited value
            const newEditedValues = { ...editedValues };
            delete newEditedValues[key];
            setEditedValues(newEditedValues);

            setSaving(false);
            alert('Setting updated successfully!');
        } catch (err) {
            console.error('Failed to update setting:', err);
            alert('Failed to update setting');
            setSaving(false);
        }
    };

    const handleValueChange = (key, value) => {
        setEditedValues({
            ...editedValues,
            [key]: value
        });
    };

    const toggleSensitiveVisibility = (key) => {
        setShowSensitive({
            ...showSensitive,
            [key]: !showSensitive[key]
        });
    };

    const categories = [
        { id: 'all', label: 'All Settings', icon: SettingsIcon },
        { id: 'system', label: 'System', icon: Database },
        { id: 'ml', label: 'ML/AI', icon: Zap },
        { id: 'business', label: 'Business Rules', icon: Globe },
        { id: 'email', label: 'Email', icon: Mail },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'notifications', label: 'Notifications', icon: Bell },
    ];

    const getCategoryIcon = (category) => {
        const cat = categories.find(c => c.id === category);
        return cat ? cat.icon : SettingsIcon;
    };

    const filteredSettings = activeCategory === 'all'
        ? settings
        : settings.filter(s => s.category === activeCategory);

    const renderInput = (setting) => {
        const currentValue = editedValues[setting.key] !== undefined
            ? editedValues[setting.key]
            : setting.value;

        const isEdited = editedValues[setting.key] !== undefined;

        if (setting.is_sensitive) {
            return (
                <div className="flex items-center space-x-2">
                    <div className="relative flex-1">
                        <input
                            type={showSensitive[setting.key] ? 'text' : 'password'}
                            value={currentValue}
                            onChange={(e) => handleValueChange(setting.key, e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            placeholder="Enter value..."
                        />
                        <button
                            onClick={() => toggleSensitiveVisibility(setting.key)}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                            {showSensitive[setting.key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                    </div>
                    <Lock className="w-4 h-4 text-gray-400" />
                </div>
            );
        }

        switch (setting.value_type) {
            case 'boolean':
                return (
                    <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={currentValue === 'true' || currentValue === true}
                            onChange={(e) => handleValueChange(setting.key, e.target.checked.toString())}
                            className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                        />
                        <span className="text-sm text-gray-700">
                            {currentValue === 'true' || currentValue === true ? 'Enabled' : 'Disabled'}
                        </span>
                    </label>
                );

            case 'integer':
                return (
                    <input
                        type="number"
                        value={currentValue}
                        onChange={(e) => handleValueChange(setting.key, e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                );

            case 'json':
                return (
                    <textarea
                        value={currentValue}
                        onChange={(e) => handleValueChange(setting.key, e.target.value)}
                        rows={4}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent font-mono text-sm"
                        placeholder='{"key": "value"}'
                    />
                );

            default: // string
                return (
                    <input
                        type="text"
                        value={currentValue}
                        onChange={(e) => handleValueChange(setting.key, e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                );
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
                <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Settings</h2>
                <p className="text-red-800 mb-4">{error}</p>
                <button
                    onClick={fetchSettings}
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
                    <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
                    <p className="text-gray-600 mt-1">Manage system-wide configurations and preferences</p>
                </div>
                <button
                    onClick={fetchSettings}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh</span>
                </button>
            </div>

            {/* Category Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex space-x-4 overflow-x-auto">
                    {categories.map((category) => {
                        const Icon = category.icon;
                        const count = category.id === 'all'
                            ? settings.length
                            : settings.filter(s => s.category === category.id).length;

                        return (
                            <button
                                key={category.id}
                                onClick={() => setActiveCategory(category.id)}
                                className={`flex items-center space-x-2 py-4 px-4 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${activeCategory === category.id
                                        ? 'border-red-600 text-red-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span>{category.label}</span>
                                {count > 0 && (
                                    <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                                        {count}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* Settings List */}
            {filteredSettings.length === 0 ? (
                <div className="bg-gray-50 rounded-lg p-12 text-center">
                    <SettingsIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Settings Found</h3>
                    <p className="text-gray-600">
                        {activeCategory === 'all'
                            ? 'No system settings have been configured yet.'
                            : `No settings found in the ${categories.find(c => c.id === activeCategory)?.label} category.`
                        }
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredSettings.map((setting) => {
                        const Icon = getCategoryIcon(setting.category);
                        const isEdited = editedValues[setting.key] !== undefined;

                        return (
                            <div key={setting.id} className="bg-white rounded-lg shadow-md p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-start space-x-3 flex-1">
                                        <div className="p-2 bg-gray-100 rounded-lg">
                                            <Icon className="w-5 h-5 text-gray-600" />
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2">
                                                <h3 className="text-lg font-semibold text-gray-900">
                                                    {setting.key}
                                                </h3>
                                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                                    {setting.value_type}
                                                </span>
                                                {setting.is_sensitive && (
                                                    <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full flex items-center space-x-1">
                                                        <Lock className="w-3 h-3" />
                                                        <span>Sensitive</span>
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 mt-1">{setting.description}</p>
                                            {setting.updated_at && (
                                                <p className="text-xs text-gray-500 mt-2">
                                                    Last updated: {new Date(setting.updated_at).toLocaleString()}
                                                    {setting.updated_by && ` by ${setting.updated_by}`}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-end space-x-3">
                                    <div className="flex-1">
                                        {renderInput(setting)}
                                    </div>
                                    {isEdited && (
                                        <button
                                            onClick={() => handleSaveSetting(setting.key, editedValues[setting.key])}
                                            disabled={saving}
                                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                                        >
                                            <Save className="w-4 h-4" />
                                            <span>{saving ? 'Saving...' : 'Save'}</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                        <h4 className="font-medium text-blue-900">Security Notice</h4>
                        <p className="text-sm text-blue-800 mt-1">
                            Only Super Admins can modify system settings. Sensitive values are encrypted and hidden by default.
                            Changes take effect immediately and may impact system behavior.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Settings;
