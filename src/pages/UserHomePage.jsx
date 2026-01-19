import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'
import ConfirmationModal from '../components/ConfirmationModal'

const UserHomePage = () => {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [listings, setListings] = useState([])
  const [loadingListings, setLoadingListings] = useState(true)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [modal, setModal] = useState({
    isOpen: false,
    type: 'info',
    title: '',
    message: '',
    onConfirm: () => { }
  });

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    } else {
      // If no user data, redirect to login
      navigate('/login')
    }
  }, [navigate])

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await api.getUserListings();
        if (response.success) {
          setListings(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch listings:', error);
      } finally {
        setLoadingListings(false);
      }
    };
    if (user) {
      fetchListings();
    }
  }, [user]);

  if (!user) {
    return null // Will redirect to login
  }

  const features = [
    {
      icon: '📱',
      title: 'Smartphone Price Prediction',
      description: 'Get accurate resale value predictions using AI',
      color: 'from-primary-red to-primary-red/50',
      link: '/predictions/smartphone'
    },
    {
      icon: '💻',
      title: 'Laptop Price Prediction',
      description: 'Know your device worth before selling',
      color: 'from-primary-green to-primary-green/50',
      link: '/predictions/laptop'
    },
    {
      icon: '🎯',
      title: 'Smart Product Finder',
      description: 'AI finds best products matching your needs with direct links',
      color: 'from-yellow-500 to-orange-500',
      link: '/smart-finder'
    },
    {
      icon: '🤖',
      title: 'AI Tech Advisor',
      description: '24/7 intelligent chatbot for tech queries',
      color: 'from-primary-red to-primary-green',
      link: '/chatbot'
    }
  ]

  return (
    <div className="min-h-screen bg-black overflow-hidden relative">
      {/* Animated Background Gradient */}
      <div
        className="fixed inset-0 opacity-20 pointer-events-none"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(220, 38, 38, 0.3), transparent 40%)`
        }}
      />

      {/* Floating Particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary-green rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [null, Math.random() * window.innerHeight],
              x: [null, Math.random() * window.innerWidth],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
          />
        ))}
      </div>

      {/* Navigation Bar */}
      <UserNavbar user={user} />

      {/* Main Content */}
      <main className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-white">Welcome Back,</span>
              <br />
              <span className="text-gradient">{user.first_name || 'User'}!</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary-grey max-w-3xl mx-auto">
              Explore our AI-powered features and make smart tech decisions
            </p>
          </motion.div>

          {/* Profile Picture Reminder */}
          {!user.profile_picture && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-4xl mx-auto mb-8 bg-gradient-to-r from-primary-red/20 to-orange-500/20 border border-primary-red/30 rounded-xl p-6 backdrop-blur-sm"
            >
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-primary-red/30 rounded-full flex items-center justify-center text-3xl">
                    👤
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Complete Your Profile!</h3>
                    <p className="text-primary-grey">Sharing a profile picture helps build trust in the marketplace.</p>
                  </div>
                </div>
                <label className="cursor-pointer px-6 py-3 bg-primary-red hover:bg-primary-red/80 text-white rounded-lg font-semibold transition-all transform hover:scale-105">
                  Update Picture
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={async (e) => {
                      const file = e.target.files[0];
                      if (file) {
                        const formData = new FormData();
                        formData.append('profile_picture', file);
                        try {
                          const res = await api.updateProfile(formData);
                          if (res.success) {
                            const updatedUser = { ...user, profile_picture: res.profile_picture };
                            setUser(updatedUser);
                            localStorage.setItem('user', JSON.stringify(updatedUser));
                            setMessage({ type: 'success', text: 'Profile picture updated!' });
                          }
                        } catch (err) {
                          setMessage({ type: 'error', text: err.message });
                        }
                      }
                    }}
                  />
                </label>
              </div>
            </motion.div>
          )}

          {/* User Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="max-w-2xl mx-auto mb-12 glass-effect rounded-xl p-6"
          >
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="w-24 h-24 rounded-full overflow-hidden border-2 border-primary-green flex-shrink-0">
                {user.profile_picture ? (
                  <img
                    src={user.profile_picture.startsWith('http') ? user.profile_picture : `http://localhost:8000${user.profile_picture}`}
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-primary-grey/20 flex items-center justify-center text-3xl">
                    {user.first_name?.[0]?.toUpperCase() || 'U'}
                  </div>
                )}
              </div>
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold text-white mb-4">Your Profile</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-primary-grey text-sm mb-1">Email</p>
                    <p className="text-white font-semibold">{user.email}</p>
                  </div>
                  {user.first_name && (
                    <div>
                      <p className="text-primary-grey text-sm mb-1">Name</p>
                      <p className="text-white font-semibold">{user.first_name} {user.last_name}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>



          {/* My Listings Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mb-12"
          >
            <h2 className="text-2xl font-bold text-white mb-6 pl-2 border-l-4 border-primary-green">My Active Listings</h2>

            {loadingListings ? (
              <div className="text-primary-grey text-center py-8">Loading your listings...</div>
            ) : listings.length === 0 ? (
              <div className="glass-effect rounded-xl p-8 text-center border-dashed border-2 border-primary-grey/30">
                <p className="text-primary-grey mb-4">You haven't listed any devices yet.</p>
                <Link to="/resale" className="text-primary-green font-semibold hover:underline">Start selling now →</Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {listings.map((listing) => (
                  <div key={listing.id} className="glass-effect rounded-xl overflow-hidden hover:bg-white/5 transition-all group">
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
                      <div className="absolute top-2 right-2 px-2 py-1 bg-green-500/90 text-white text-xs font-bold rounded uppercase">
                        {listing.status}
                      </div>
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
                      <div className="flex gap-2">
                        <button
                          onClick={() => navigate(`/marketplace/${listing.id}`)}
                          className="flex-1 py-2 bg-primary-darkGrey hover:bg-primary-grey/20 text-white border border-primary-grey/30 rounded-lg text-sm transition-colors"
                        >
                          View Details
                        </button>
                        {listing.status === 'active' && (
                          <button
                            onClick={() => setModal({
                              isOpen: true,
                              type: 'warning',
                              title: 'Mark as Sold?',
                              message: 'This item will be removed from the public marketplace. You cannot undo this easily.',
                              confirmText: 'Mark Sold',
                              onConfirm: async () => {
                                const res = await api.updateListingStatus(listing.id, 'sold');
                                if (res.success) {
                                  setMessage({ type: 'success', text: 'Marked as Sold!' });
                                  setListings(listings.map(l => l.id === listing.id ? { ...l, status: 'sold' } : l));
                                }
                              }
                            })}
                            className="px-3 py-2 bg-yellow-600/20 hover:bg-yellow-600/40 text-yellow-500 border border-yellow-600/30 rounded-lg text-sm transition-colors"
                            title="Mark as Sold"
                          >
                            💰
                          </button>
                        )}
                        <button
                          onClick={() => setModal({
                            isOpen: true,
                            type: 'danger',
                            title: 'Delete Listing?',
                            message: 'Are you sure you want to delete this listing permanently? This action cannot be undone.',
                            confirmText: 'Delete',
                            onConfirm: async () => {
                              const res = await api.deleteListing(listing.id);
                              if (res.success) {
                                setMessage({ type: 'success', text: 'Listing deleted.' });
                                setListings(listings.filter(l => l.id !== listing.id));
                              }
                            }
                          })}
                          className="px-3 py-2 bg-red-600/20 hover:bg-red-600/40 text-red-500 border border-red-600/30 rounded-lg text-sm transition-colors"
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -10 }}
                className="glass-effect rounded-xl p-6 cursor-pointer group"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-green transition-colors">
                  {feature.title}
                </h3>
                <p className="text-primary-grey text-sm mb-4">
                  {feature.description}
                </p>
                <Link
                  to={feature.link}
                  className="text-primary-green hover:text-primary-green/80 text-sm font-semibold"
                >
                  Explore →
                </Link>
                <div className={`mt-4 h-1 bg-gradient-to-r ${feature.color} rounded-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300`} />
              </motion.div>
            ))}
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="text-center"
          >
            <h2 className="text-4xl font-bold mb-12 text-white">
              Quick <span className="text-gradient">Actions</span>
            </h2>
            <div className="flex justify-center gap-6 flex-wrap">
              <Link
                to="/predictions/smartphone"
                className="px-8 py-4 bg-primary-red hover:bg-primary-red/80 text-white rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
              >
                Predict Smartphone Price
              </Link>
              <Link
                to="/predictions/laptop"
                className="px-8 py-4 bg-primary-green hover:bg-primary-green/80 text-white rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-green/50"
              >
                Predict Laptop Price
              </Link>
              <Link
                to="/smart-finder"
                className="px-8 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-orange-600/50"
              >
                Find Best Products
              </Link>
              <Link
                to="/chatbot"
                className="px-8 py-4 border-2 border-primary-grey text-white rounded-lg font-semibold text-lg hover:border-primary-green hover:text-primary-green transition-all duration-300"
              >
                Chat with AI
              </Link>
            </div>
          </motion.div>
        </div>
      </main >

      {/* Footer */}
      <footer className="relative z-10 border-t border-primary-grey/30 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-primary-grey">
          <p>&copy; 2024 DealGoat. All rights reserved. Powered by AI & ML.</p>
        </div>
      </footer>

      {
        message.text && (
          <MessagePopup
            type={message.type}
            message={message.text}
            onClose={() => setMessage({ type: '', text: '' })}
          />
        )
      }

      <ConfirmationModal
        isOpen={modal.isOpen}
        onClose={() => setModal({ ...modal, isOpen: false })}
        onConfirm={modal.onConfirm}
        title={modal.title}
        message={modal.message}
        type={modal.type}
        confirmText={modal.confirmText}
      />
    </div >
  )
}

export default UserHomePage

