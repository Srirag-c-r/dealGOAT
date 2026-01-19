import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Eye, Play } from 'lucide-react';
import { adminAPI } from '../../services/adminApi';

const ListingModeration = () => {
    const [listings, setListings] = useState([]);
    const [pendingListings, setPendingListings] = useState([]);
    const [flaggedListings, setFlaggedListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('all'); // all, pending, flagged
    const [selectedListing, setSelectedListing] = useState(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        fetchListings();
        fetchPendingListings();
        fetchFlaggedListings();
    }, []);

    const fetchListings = async () => {
        try {
            const response = await adminAPI.getListingList();
            setListings(response.data.listings);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch listings:', err);
            setLoading(false);
        }
    };

    const fetchPendingListings = async () => {
        try {
            const response = await adminAPI.getPendingListings();
            setPendingListings(response.data.pending_listings);
        } catch (err) {
            console.error('Failed to fetch pending listings:', err);
        }
    };

    const fetchFlaggedListings = async () => {
        try {
            const response = await adminAPI.getFlaggedListings();
            setFlaggedListings(response.data.flagged_listings);
        } catch (err) {
            console.error('Failed to fetch flagged listings:', err);
        }
    };

    const moderateListing = async (listingId, action) => {
        const notes = prompt(`Enter notes for ${action}:`);
        if (!notes && action !== 'approve') return;

        try {
            await adminAPI.moderateListing(listingId, { action, notes });
            alert(`Listing ${action}d successfully`);
            fetchListings();
            fetchPendingListings();
            fetchFlaggedListings();
            setShowModal(false);
        } catch (err) {
            alert('Failed to moderate listing');
        }
    };

    const runFraudCheck = async () => {
        if (!confirm('Run automated fraud detection on all listings?')) return;

        try {
            const response = await adminAPI.runFraudCheck({});
            alert(response.data.message);
            fetchFlaggedListings();
        } catch (err) {
            alert('Failed to run fraud check');
        }
    };

    const displayListings = activeTab === 'pending' ? pendingListings :
        activeTab === 'flagged' ? flaggedListings : listings;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Listing Moderation</h1>
                    <p className="text-gray-600 mt-1">Review and moderate marketplace listings</p>
                </div>
                <button
                    onClick={runFraudCheck}
                    className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                    <Play className="w-5 h-5" />
                    <span>Run Fraud Detection</span>
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Pending Approval</p>
                            <p className="text-3xl font-bold text-yellow-600">{pendingListings.length}</p>
                        </div>
                        <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                            <AlertTriangle className="w-6 h-6 text-yellow-600" />
                        </div>
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Flagged Items</p>
                            <p className="text-3xl font-bold text-red-600">{flaggedListings.length}</p>
                        </div>
                        <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                            <XCircle className="w-6 h-6 text-red-600" />
                        </div>
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Total Listings</p>
                            <p className="text-3xl font-bold text-blue-600">{listings.length}</p>
                        </div>
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <CheckCircle className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-md">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6" aria-label="Tabs">
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'all'
                                ? 'border-red-600 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            All Listings ({listings.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('pending')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'pending'
                                ? 'border-red-600 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            Pending ({pendingListings.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('flagged')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'flagged'
                                ? 'border-red-600 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            Flagged ({flaggedListings.length})
                        </button>
                    </nav>
                </div>

                {/* Listings Table */}
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Device
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Seller
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Price
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Created
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-4 text-center">
                                        <div className="flex justify-center">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
                                        </div>
                                    </td>
                                </tr>
                            ) : displayListings.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                                        No listings found
                                    </td>
                                </tr>
                            ) : (
                                displayListings.map((listing) => (
                                    <tr key={listing.id || listing.listing_id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">
                                                {listing.device_type || 'Unknown'}
                                            </div>
                                            {listing.city && (
                                                <div className="text-sm text-gray-500">{listing.city}</div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">
                                                {listing.seller?.email || listing.seller_email || 'N/A'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">
                                                ₹{listing.expected_price?.toLocaleString() || 0}
                                            </div>
                                            {listing.price_deviation && (
                                                <div className={`text-xs ${listing.price_deviation < -20 ? 'text-red-600' : 'text-gray-500'}`}>
                                                    {listing.price_deviation > 0 ? '+' : ''}{listing.price_deviation.toFixed(1)}% vs predicted
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {listing.moderation_status === 'pending' || listing.status === 'pending' ? (
                                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                                    Pending
                                                </span>
                                            ) : listing.moderation_status === 'approved' ? (
                                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                                    Approved
                                                </span>
                                            ) : listing.moderation_status === 'flagged' || listing.flag_reason ? (
                                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                                    Flagged
                                                </span>
                                            ) : (
                                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                                    {listing.moderation_status || listing.status || 'Unknown'}
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(listing.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                                            <button
                                                onClick={() => {
                                                    setSelectedListing(listing);
                                                    setShowModal(true);
                                                }}
                                                className="text-blue-600 hover:text-blue-900"
                                            >
                                                <Eye className="w-5 h-5" />
                                            </button>
                                            {(listing.moderation_status === 'pending' || !listing.moderation_status) && (
                                                <>
                                                    <button
                                                        onClick={() => moderateListing(listing.id || listing.listing_id, 'approve')}
                                                        className="text-green-600 hover:text-green-900"
                                                    >
                                                        <CheckCircle className="w-5 h-5" />
                                                    </button>
                                                    <button
                                                        onClick={() => moderateListing(listing.id || listing.listing_id, 'reject')}
                                                        className="text-red-600 hover:text-red-900"
                                                    >
                                                        <XCircle className="w-5 h-5" />
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Listing Details Modal */}
            {showModal && selectedListing && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-2xl font-bold text-gray-900">Listing Details</h2>
                                <button
                                    onClick={() => setShowModal(false)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    <XCircle className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-sm font-medium text-gray-500">Device Type</label>
                                        <p className="text-gray-900 capitalize">{selectedListing.device_type}</p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-gray-500">Expected Price</label>
                                        <p className="text-gray-900">₹{selectedListing.expected_price?.toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-gray-500">Predicted Price</label>
                                        <p className="text-gray-900">₹{selectedListing.predicted_price?.toLocaleString() || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-gray-500">Price Deviation</label>
                                        <p className={selectedListing.price_deviation < -20 ? 'text-red-600 font-bold' : 'text-gray-900'}>
                                            {selectedListing.price_deviation?.toFixed(1)}%
                                        </p>
                                    </div>
                                </div>

                                {selectedListing.flag_reason && (
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                        <h3 className="font-bold text-red-900 mb-2">Flagged</h3>
                                        <p className="text-sm text-red-800">
                                            Reason: {selectedListing.flag_reason}
                                        </p>
                                        {selectedListing.description && (
                                            <p className="text-sm text-red-700 mt-1">{selectedListing.description}</p>
                                        )}
                                    </div>
                                )}

                                <div className="flex space-x-3 pt-4">
                                    <button
                                        onClick={() => moderateListing(selectedListing.id || selectedListing.listing_id, 'approve')}
                                        className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                                    >
                                        Approve
                                    </button>
                                    <button
                                        onClick={() => moderateListing(selectedListing.id || selectedListing.listing_id, 'reject')}
                                        className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
                                    >
                                        Reject
                                    </button>
                                    <button
                                        onClick={() => setShowModal(false)}
                                        className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-medium text-gray-900"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ListingModeration;
