import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import UserNavbar from '../components/UserNavbar'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'

const Marketplace = () => {
    const navigate = useNavigate()
    const [user, setUser] = useState(null)
    const [listings, setListings] = useState([])
    const [loading, setLoading] = useState(true)
    const [filters, setFilters] = useState({
        device_type: '',
        brand: '',
        min_price: '',
        max_price: ''
    });
    const [message, setMessage] = useState({ type: '', text: '' })

    // Check auth
    useEffect(() => {
        const userData = localStorage.getItem('user')
        if (userData) {
            setUser(JSON.parse(userData))
        }
        // Note: Marketplace can be public, so we don't redirect if no user
    }, [])


    const fetchListings = async () => {
        setLoading(true)
        try {
            const response = await api.getActiveListings(filters)
            if (response.success) {
                setListings(response.data)
            }
        } catch (error) {
            console.error('Failed to fetch listings:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchListings()
    }, [filters]) // Refetch when filters change

    const handleFilterChange = (e) => {
        const { name, value } = e.target
        setFilters(prev => ({ ...prev, [name]: value }))
    }

    const handleTypeSelect = (type) => {
        setFilters(prev => ({ ...prev, type: prev.type === type ? '' : type }))
    }

    const brands = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer']

    return (
        <div className="min-h-screen bg-black text-white">
            {user ? <UserNavbar user={user} /> : (
                <nav className="fixed w-full z-50 top-0 start-0 border-b border-primary-grey/30 bg-black/80 backdrop-blur-md">
                    <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
                        <span className="self-center text-2xl font-semibold whitespace-nowrap text-white">DealGoat</span>
                        <div className="flex md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
                            <button onClick={() => navigate('/login')} className="text-white bg-primary-green hover:bg-primary-green/80 focus:ring-4 focus:outline-none focus:ring-primary-green/50 font-medium rounded-lg text-sm px-4 py-2 text-center">Login</button>
                        </div>
                    </div>
                </nav>
            )}

            <div className="max-w-7xl mx-auto px-4 py-24 flex flex-col md:flex-row gap-8">
                {/* Sidebar Filters */}
                <div className="w-full md:w-64 flex-shrink-0">
                    <div className="glass-effect rounded-xl p-6 sticky top-24">
                        <h3 className="text-xl font-bold mb-6 text-primary-green">Filters</h3>

                        {/* Device Type */}
                        <div className="mb-6">
                            <h4 className="font-semibold mb-3">Device Type</h4>
                            <div className="flex flex-col gap-2">
                                <button
                                    onClick={() => handleTypeSelect('smartphone')}
                                    className={`px-4 py-2 rounded-lg border transition-all ${filters.type === 'smartphone' ? 'bg-primary-green/20 border-primary-green text-primary-green' : 'border-primary-grey/30 hover:border-primary-green/50'}`}
                                >
                                    Smartphones
                                </button>
                                <button
                                    onClick={() => handleTypeSelect('laptop')}
                                    className={`px-4 py-2 rounded-lg border transition-all ${filters.type === 'laptop' ? 'bg-primary-green/20 border-primary-green text-primary-green' : 'border-primary-grey/30 hover:border-primary-green/50'}`}
                                >
                                    Laptops
                                </button>
                            </div>
                        </div>

                        {/* Price Range */}
                        <div className="mb-6">
                            <h4 className="font-semibold mb-3">Price Range</h4>
                            <div className="flex gap-2 mb-2">
                                <input
                                    type="number"
                                    name="min_price"
                                    placeholder="Min"
                                    value={filters.min_price}
                                    onChange={handleFilterChange}
                                    className="w-full bg-primary-darkGrey border border-primary-grey/30 rounded px-3 py-2 text-sm focus:border-primary-green outline-none"
                                />
                                <input
                                    type="number"
                                    name="max_price"
                                    placeholder="Max"
                                    value={filters.max_price}
                                    onChange={handleFilterChange}
                                    className="w-full bg-primary-darkGrey border border-primary-grey/30 rounded px-3 py-2 text-sm focus:border-primary-green outline-none"
                                />
                            </div>
                        </div>

                        {/* Brand */}
                        <div className="mb-6">
                            <h4 className="font-semibold mb-3">Brand</h4>
                            <select
                                name="brand"
                                value={filters.brand}
                                onChange={handleFilterChange}
                                className="w-full bg-primary-darkGrey border border-primary-grey/30 rounded px-3 py-2 text-sm focus:border-primary-green outline-none"
                            >
                                <option value="">All Brands</option>
                                {brands.map(b => <option key={b} value={b}>{b}</option>)}
                            </select>
                        </div>

                        <button
                            onClick={() => setFilters({ type: '', brand: '', min_price: '', max_price: '' })}
                            className="w-full py-2 text-sm text-primary-grey hover:text-white transition-colors underline"
                        >
                            Clear Filters
                        </button>
                    </div>
                </div>

                {/* Listings Grid */}
                <div className="flex-1">
                    <h1 className="text-3xl font-bold mb-8">Marketplace</h1>

                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {[1, 2, 3, 4, 5, 6].map(i => (
                                <div key={i} className="glass-effect rounded-xl h-80 animate-pulse"></div>
                            ))}
                        </div>
                    ) : listings.length === 0 ? (
                        <div className="text-center py-20 bg-white/5 rounded-xl border border-dashed border-white/10">
                            <p className="text-xl text-primary-grey">No listings found matching your criteria.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            <AnimatePresence>
                                {listings.map((listing) => (
                                    <motion.div
                                        key={listing.id}
                                        layout
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="glass-effect rounded-xl overflow-hidden hover:bg-white/5 transition-all group"
                                    >
                                        <div className="aspect-video bg-black/50 relative overflow-hidden">
                                            {listing.image_front ? (
                                                <img
                                                    src={listing.image_front.startsWith('http') ? listing.image_front : `http://localhost:8000${listing.image_front}`}
                                                    alt="Device"
                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-4xl">📱</div>
                                            )}
                                        </div>
                                        <div className="p-5">
                                            <div className="flex justify-between items-start mb-2">
                                                <h3 className="text-white font-bold text-lg truncate pr-2">
                                                    {listing.device_type === 'smartphone' ? 'Smartphone' : 'Laptop'}
                                                    <span className="text-primary-grey text-sm font-normal block font-thin">{listing.brand} {listing.model}</span>
                                                </h3>
                                                <span className="text-primary-green font-bold whitespace-nowrap">₹{Number(listing.expected_price).toLocaleString()}</span>
                                            </div>
                                            <div className="text-sm text-primary-grey mb-4 h-10 overflow-hidden text-ellipsis line-clamp-2">
                                                {listing.specs} <br />
                                                <span className="text-xs text-primary-grey/70">Condition: {listing.body_condition}</span>
                                            </div>
                                            <button
                                                onClick={() => navigate(`/marketplace/${listing.id}`)}
                                                className="w-full py-2 bg-primary-green hover:bg-primary-green/80 text-white font-semibold rounded-lg text-sm transition-colors shadow-lg shadow-primary-green/20"
                                            >
                                                View Details
                                            </button>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    )}
                </div>
            </div>
            {message.text && (
                <MessagePopup
                    type={message.type}
                    message={message.text}
                    onClose={() => setMessage({ type: '', text: '' })}
                />
            )}
        </div>
    )
}

export default Marketplace
