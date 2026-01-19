import React, { useState, useEffect } from 'react';
import {
    Users, TrendingUp, ShoppingCart, BarChart3,
    Calendar, Download, RefreshCw, Activity
} from 'lucide-react';
import { adminAPI } from '../../services/adminApi';
import LineChart from '../../components/admin/charts/LineChart';
import BarChart from '../../components/admin/charts/BarChart';
import PieChart from '../../components/admin/charts/PieChart';
import MetricCard from '../../components/admin/charts/MetricCard';

const Analytics = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [dateRange, setDateRange] = useState('30');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Data states
    const [dashboardStats, setDashboardStats] = useState(null);
    const [userTrends, setUserTrends] = useState(null);
    const [userSegments, setUserSegments] = useState(null);
    const [userGeography, setUserGeography] = useState(null);
    const [predictionTrends, setPredictionTrends] = useState(null);
    const [devicePopularity, setDevicePopularity] = useState(null);
    const [priceDistribution, setPriceDistribution] = useState(null);
    const [listingTrends, setListingTrends] = useState(null);

    useEffect(() => {
        fetchAllData();
    }, [dateRange]);

    const fetchAllData = async () => {
        setLoading(true);
        setError(null);
        try {
            // Fetch dashboard stats
            const statsRes = await adminAPI.getDashboardStats();
            setDashboardStats(statsRes.data);

            // Fetch user analytics
            const trendsRes = await fetch(`http://localhost:8000/api/auth/admin/analytics/users/trends/?period=${dateRange}`, {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const trendsData = await trendsRes.json();
            setUserTrends(trendsData);

            const segmentsRes = await fetch('http://localhost:8000/api/auth/admin/analytics/users/segments/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const segmentsData = await segmentsRes.json();
            setUserSegments(segmentsData);

            const geoRes = await fetch('http://localhost:8000/api/auth/admin/analytics/users/geography/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const geoData = await geoRes.json();
            setUserGeography(geoData);

            // Fetch prediction analytics
            const predTrendsRes = await fetch(`http://localhost:8000/api/predictions/admin/analytics/trends/?period=${dateRange}`, {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const predTrendsData = await predTrendsRes.json();
            setPredictionTrends(predTrendsData);

            const devicesRes = await fetch('http://localhost:8000/api/predictions/admin/analytics/devices/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const devicesData = await devicesRes.json();
            setDevicePopularity(devicesData);

            const priceDistRes = await fetch('http://localhost:8000/api/predictions/admin/analytics/price-distribution/', {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const priceDistData = await priceDistRes.json();
            setPriceDistribution(priceDistData);

            const listingTrendsRes = await fetch(`http://localhost:8000/api/predictions/admin/analytics/listings/trends/?period=${dateRange}`, {
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`
                }
            });
            const listingTrendsData = await listingTrendsRes.json();
            setListingTrends(listingTrendsData);

            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setError('Failed to load analytics data');
            setLoading(false);
        }
    };

    const tabs = [
        { id: 'overview', label: 'Overview', icon: Activity },
        { id: 'users', label: 'Users', icon: Users },
        { id: 'predictions', label: 'Predictions', icon: TrendingUp },
        { id: 'marketplace', label: 'Marketplace', icon: ShoppingCart },
    ];

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
                <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Analytics</h2>
                <p className="text-red-800 mb-4">{error}</p>
                <button
                    onClick={fetchAllData}
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
                    <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
                    <p className="text-gray-600 mt-1">Comprehensive insights and data analysis</p>
                </div>
                <div className="flex items-center space-x-3">
                    {/* Date Range Selector */}
                    <select
                        value={dateRange}
                        onChange={(e) => setDateRange(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                        <option value="7">Last 7 days</option>
                        <option value="30">Last 30 days</option>
                        <option value="90">Last 90 days</option>
                    </select>

                    {/* Refresh Button */}
                    <button
                        onClick={fetchAllData}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Refresh</span>
                    </button>

                    {/* Export Button */}
                    <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2">
                        <Download className="w-4 h-4" />
                        <span>Export</span>
                    </button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
                <nav className="flex space-x-8">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                                        ? 'border-red-600 text-red-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span>{tab.label}</span>
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="mt-6">
                {activeTab === 'overview' && (
                    <OverviewTab
                        stats={dashboardStats}
                        userTrends={userTrends}
                        predictionTrends={predictionTrends}
                    />
                )}
                {activeTab === 'users' && (
                    <UsersTab
                        trends={userTrends}
                        segments={userSegments}
                        geography={userGeography}
                    />
                )}
                {activeTab === 'predictions' && (
                    <PredictionsTab
                        trends={predictionTrends}
                        devices={devicePopularity}
                        priceDistribution={priceDistribution}
                    />
                )}
                {activeTab === 'marketplace' && (
                    <MarketplaceTab
                        trends={listingTrends}
                        stats={dashboardStats}
                    />
                )}
            </div>
        </div>
    );
};

// Overview Tab Component
const OverviewTab = ({ stats, userTrends, predictionTrends }) => {
    return (
        <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    title="Total Users"
                    value={stats?.users?.total?.toLocaleString() || '0'}
                    change={stats?.users?.new_7d}
                    icon={Users}
                    color="blue"
                    trend="up"
                />
                <MetricCard
                    title="Total Predictions"
                    value={stats?.predictions?.total?.toLocaleString() || '0'}
                    change={stats?.predictions?.recent_7d}
                    icon={TrendingUp}
                    color="purple"
                    trend="up"
                />
                <MetricCard
                    title="Active Listings"
                    value={stats?.listings?.active?.toLocaleString() || '0'}
                    change={stats?.listings?.recent_7d}
                    icon={ShoppingCart}
                    color="green"
                    trend="up"
                />
                <MetricCard
                    title="Engagement Rate"
                    value={`${stats?.users?.verification_rate || 0}%`}
                    icon={BarChart3}
                    color="indigo"
                />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {userTrends && (
                    <LineChart
                        data={userTrends.registration_trend}
                        lines={[
                            { dataKey: 'count', name: 'New Users', color: '#3B82F6' }
                        ]}
                        title="User Registration Trend"
                        height={300}
                    />
                )}
                {predictionTrends && (
                    <LineChart
                        data={predictionTrends.prediction_trend}
                        lines={[
                            { dataKey: 'laptop', name: 'Laptops', color: '#DC2626' },
                            { dataKey: 'smartphone', name: 'Smartphones', color: '#10B981' }
                        ]}
                        title="Prediction Volume"
                        height={300}
                    />
                )}
            </div>
        </div>
    );
};

// Users Tab Component
const UsersTab = ({ trends, segments, geography }) => {
    // Transform segments data for pie chart
    const segmentsData = segments ? [
        { name: 'Power Users', value: segments.power_users },
        { name: 'Active Users', value: segments.active_users },
        { name: 'Inactive Users', value: segments.inactive_users },
        { name: 'New Users', value: segments.new_users },
        { name: 'Churned Users', value: segments.churned_users },
    ] : [];

    return (
        <div className="space-y-6">
            {/* User Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                    title="Active Users (7d)"
                    value={segments?.active_users?.toLocaleString() || '0'}
                    icon={Users}
                    color="green"
                />
                <MetricCard
                    title="Power Users"
                    value={segments?.power_users?.toLocaleString() || '0'}
                    icon={TrendingUp}
                    color="purple"
                    subtitle="5+ predictions or 3+ listings"
                />
                <MetricCard
                    title="New Users (7d)"
                    value={segments?.new_users?.toLocaleString() || '0'}
                    icon={Users}
                    color="blue"
                />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {trends && (
                    <LineChart
                        data={trends.registration_trend}
                        lines={[
                            { dataKey: 'count', name: 'Registrations', color: '#3B82F6' }
                        ]}
                        title="User Registration Trend"
                        height={300}
                    />
                )}
                <PieChart
                    data={segmentsData}
                    title="User Segmentation"
                    height={300}
                />
            </div>

            {/* Geography Table */}
            {geography && geography.geography && (
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Top Locations</h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Location
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Users
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {geography.geography.slice(0, 10).map((loc, index) => (
                                    <tr key={index}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {loc.location}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {loc.count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

// Predictions Tab Component
const PredictionsTab = ({ trends, devices, priceDistribution }) => {
    // Transform device data for charts
    const deviceDistData = devices ? [
        { name: 'Laptops', value: devices.device_distribution.laptop },
        { name: 'Smartphones', value: devices.device_distribution.smartphone }
    ] : [];

    const topLaptopBrands = devices?.top_laptop_brands?.slice(0, 10).map(b => ({
        name: b.brand,
        count: b.count
    })) || [];

    const topSmartphoneBrands = devices?.top_smartphone_brands?.slice(0, 10).map(b => ({
        name: b.brand,
        count: b.count
    })) || [];

    return (
        <div className="space-y-6">
            {/* Prediction Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                    title="Total Predictions"
                    value={trends?.total_predictions?.toLocaleString() || '0'}
                    icon={TrendingUp}
                    color="purple"
                />
                <MetricCard
                    title="Avg Laptop Price"
                    value={`₹${devices?.average_prices?.laptop?.toLocaleString() || '0'}`}
                    icon={BarChart3}
                    color="blue"
                />
                <MetricCard
                    title="Avg Smartphone Price"
                    value={`₹${devices?.average_prices?.smartphone?.toLocaleString() || '0'}`}
                    icon={BarChart3}
                    color="green"
                />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {trends && (
                    <LineChart
                        data={trends.prediction_trend}
                        lines={[
                            { dataKey: 'laptop', name: 'Laptops', color: '#DC2626' },
                            { dataKey: 'smartphone', name: 'Smartphones', color: '#10B981' },
                            { dataKey: 'total', name: 'Total', color: '#3B82F6' }
                        ]}
                        title="Prediction Volume Trends"
                        height={300}
                    />
                )}
                <PieChart
                    data={deviceDistData}
                    title="Device Type Distribution"
                    height={300}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BarChart
                    data={topLaptopBrands}
                    bars={[{ dataKey: 'count', name: 'Predictions', color: '#DC2626' }]}
                    xKey="name"
                    title="Top Laptop Brands"
                    height={300}
                />
                <BarChart
                    data={topSmartphoneBrands}
                    bars={[{ dataKey: 'count', name: 'Predictions', color: '#10B981' }]}
                    xKey="name"
                    title="Top Smartphone Brands"
                    height={300}
                />
            </div>

            {/* Price Distribution */}
            {priceDistribution && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <BarChart
                        data={priceDistribution.laptop_distribution}
                        bars={[{ dataKey: 'count', name: 'Laptops', color: '#DC2626' }]}
                        xKey="range"
                        title="Laptop Price Distribution"
                        height={300}
                    />
                    <BarChart
                        data={priceDistribution.smartphone_distribution}
                        bars={[{ dataKey: 'count', name: 'Smartphones', color: '#10B981' }]}
                        xKey="range"
                        title="Smartphone Price Distribution"
                        height={300}
                    />
                </div>
            )}
        </div>
    );
};

// Marketplace Tab Component
const MarketplaceTab = ({ trends, stats }) => {
    return (
        <div className="space-y-6">
            {/* Marketplace Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <MetricCard
                    title="Active Listings"
                    value={stats?.listings?.active?.toLocaleString() || '0'}
                    icon={ShoppingCart}
                    color="green"
                />
                <MetricCard
                    title="Sold Listings"
                    value={stats?.listings?.sold?.toLocaleString() || '0'}
                    icon={TrendingUp}
                    color="blue"
                />
                <MetricCard
                    title="Pending Moderation"
                    value={stats?.listings?.pending_moderation?.toLocaleString() || '0'}
                    icon={Activity}
                    color="yellow"
                />
                <MetricCard
                    title="Avg Time to Sell"
                    value={`${trends?.avg_time_to_sell_days || 0} days`}
                    icon={BarChart3}
                    color="purple"
                />
            </div>

            {/* Charts */}
            {trends && (
                <div className="grid grid-cols-1 gap-6">
                    <LineChart
                        data={trends.listing_trend}
                        lines={[
                            { dataKey: 'created', name: 'Created', color: '#3B82F6' },
                            { dataKey: 'sold', name: 'Sold', color: '#10B981' }
                        ]}
                        title="Listing Activity Trends"
                        height={300}
                    />
                </div>
            )}
        </div>
    );
};

export default Analytics;
