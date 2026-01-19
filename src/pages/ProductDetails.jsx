import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'

const ProductDetails = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [user, setUser] = useState(null)
    const [listing, setListing] = useState(null)
    const [loading, setLoading] = useState(true)
    const [selectedImage, setSelectedImage] = useState(0)
    const [message, setMessage] = useState({ type: '', text: '' })

    useEffect(() => {
        const userData = localStorage.getItem('user')
        if (userData) {
            setUser(JSON.parse(userData))
        }
        fetchListingDetails()
    }, [id])

    const fetchListingDetails = async () => {
        try {
            const response = await api.getListingDetails(id)
            if (response.success) {
                setListing(response.data)
            } else {
                setMessage({ type: 'error', text: 'Listing not found' })
                setTimeout(() => navigate('/marketplace'), 2000)
            }
        } catch (error) {
            console.error('Failed to fetch listing:', error)
            setMessage({ type: 'error', text: 'Failed to load details' })
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-white animate-pulse">Loading Details...</div>
            </div>
        )
    }

    if (!listing) return null

    const images = [
        listing.image_front,
        listing.image_back,
        listing.image_side,
        listing.image_screen_on,
        listing.image_proof
    ].filter(Boolean).map(img => img.startsWith('http') ? img : `http://localhost:8000${img}`)

    return (
        <div className="min-h-screen bg-black text-white">
            {user ? <UserNavbar user={user} /> : (
                <nav className="fixed w-full z-50 top-0 start-0 border-b border-primary-grey/30 bg-black/80 backdrop-blur-md">
                    <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
                        <span className="self-center text-2xl font-semibold whitespace-nowrap text-white">DealGoat</span>
                        <button onClick={() => navigate('/marketplace')} className="text-primary-grey hover:text-white">Back to Marketplace</button>
                    </div>
                </nav>
            )}

            <div className="max-w-7xl mx-auto px-4 py-24">
                <button
                    onClick={() => navigate(-1)}
                    className="mb-8 text-primary-grey hover:text-white flex items-center gap-2 transition-colors"
                >
                    ← Back
                </button>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Left Column: Image Gallery */}
                    <div>
                        <div className="aspect-video bg-black/50 rounded-xl overflow-hidden mb-4 border border-primary-grey/30">
                            <motion.img
                                key={selectedImage}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                src={images[selectedImage]}
                                alt="Product View"
                                className="w-full h-full object-contain"
                            />
                        </div>
                        <div className="grid grid-cols-5 gap-2">
                            {images.map((img, index) => (
                                <button
                                    key={index}
                                    onClick={() => setSelectedImage(index)}
                                    className={`aspect-square rounded-lg overflow-hidden border-2 transition-colors ${selectedImage === index ? 'border-primary-green' : 'border-transparent hover:border-primary-grey/50'}`}
                                >
                                    <img src={img} alt={`Thumbnail ${index + 1}`} className="w-full h-full object-cover" />
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Right Column: Key Info */}
                    <div>
                        <h1 className="text-4xl font-bold mb-2">
                            {listing.device_type === 'smartphone' ? 'Smartphone' : 'Laptop'}
                            <span className="block text-2xl font-normal text-primary-grey mt-1">{listing.brand} {listing.model}</span>
                        </h1>

                        <div className="text-5xl font-bold text-primary-green mb-8">
                            ₹{Number(listing.expected_price).toLocaleString()}
                            {listing.is_negotiable && <span className="text-lg text-primary-grey font-normal ml-2">(Negotiable)</span>}
                        </div>

                        <div className="glass-effect rounded-xl p-6 mb-8">
                            <h3 className="text-xl font-bold mb-4">Key Specifications</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="bg-white/5 p-3 rounded-lg">
                                    <span className="text-primary-grey block text-xs uppercase tracking-wider mb-1">RAM & Storage</span>
                                    <span className="font-semibold">{listing.specs}</span>
                                </div>
                                <div className="bg-white/5 p-3 rounded-lg">
                                    <span className="text-primary-grey block text-xs uppercase tracking-wider mb-1">Condition</span>
                                    <span className="font-semibold text-primary-green">{listing.body_condition}</span>
                                </div>
                                {listing.invoice_available && (
                                    <div className="bg-white/5 p-3 rounded-lg">
                                        <span className="text-primary-grey block text-xs uppercase tracking-wider mb-1">Warranty</span>
                                        <span className="font-semibold text-blue-400">Bill Available</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Seller Info */}
                        <div className="glass-effect rounded-xl p-6 mb-8 border-l-4 border-primary-green/50">
                            <h3 className="text-lg font-bold mb-4">Seller Information</h3>
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 rounded-full overflow-hidden bg-primary-grey/20 border border-primary-grey/30">
                                    {listing.seller_profile_picture ? (
                                        <img
                                            src={listing.seller_profile_picture.startsWith('http') ? listing.seller_profile_picture : `http://localhost:8000${listing.seller_profile_picture}`}
                                            alt="Seller"
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-lg text-white font-bold bg-primary-green">
                                            {(listing.seller_name || 'G')[0].toUpperCase()}
                                        </div>
                                    )}
                                </div>
                                <div>
                                    <p className="text-lg font-semibold">{listing.seller_name || 'Generic Seller'}</p>
                                    <p className="text-primary-grey text-sm">📍 {listing.city} - {listing.pincode}</p>
                                </div>
                            </div>
                            <div className="text-sm text-primary-grey space-y-1">
                                <p>🚚 Delivery: <span className="text-white">{listing.delivery_option}</span></p>
                                {listing.is_willing_to_ship && <p>📦 Willing to ship</p>}
                            </div>
                        </div>

                        <button
                            onClick={async () => {
                                try {
                                    const response = await api.startConversation(id)
                                    if (response.success) {
                                        navigate('/messages')
                                    } else {
                                        setMessage({ type: 'error', text: response.message || 'Failed to start conversation' })
                                    }
                                } catch (error) {
                                    setMessage({ type: 'error', text: 'Failed to start conversation' })
                                }
                            }}
                            className="w-full py-4 bg-primary-green hover:bg-primary-green/80 text-white font-bold text-lg rounded-xl shadow-lg shadow-primary-green/20 transition-all transform hover:scale-[1.02]"
                        >
                            Contact Seller
                        </button>
                    </div>
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

export default ProductDetails
