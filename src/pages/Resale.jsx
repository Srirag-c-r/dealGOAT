import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'

const Resale = () => {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

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

  if (!user) {
    return null // Will redirect to login
  }

  const resaleOptions = [
    {
      icon: '📱',
      title: 'Sell Your Smartphone',
      description: 'Get instant price prediction for your smartphone',
      gradient: 'from-primary-red to-red-600',
      link: '/predictions/smartphone',
      stats: { accuracy: '95%', avgPrice: '$250' }
    },
    {
      icon: '💻',
      title: 'Sell Your Laptop',
      description: 'Know your laptop\'s exact market value',
      gradient: 'from-primary-green to-emerald-600',
      link: '/predictions/laptop',
      stats: { accuracy: '93%', avgPrice: '$450' }
    },
    {
      icon: '⌚',
      title: 'Smartwatch (Coming Soon)',
      description: 'Wearable tech price predictions',
      gradient: 'from-purple-600 to-pink-600',
      link: '#',
      stats: { accuracy: 'N/A', avgPrice: 'TBA' },
      comingSoon: true
    },
    {
      icon: '🎧',
      title: 'Audio Devices (Coming Soon)',
      description: 'Headphones, earbuds & speakers',
      gradient: 'from-blue-600 to-cyan-600',
      link: '#',
      stats: { accuracy: 'N/A', avgPrice: 'TBA' },
      comingSoon: true
    }
  ]

  const howItWorks = [
    {
      step: '1',
      icon: '📝',
      title: 'Enter Device Details',
      description: 'Provide specifications and condition of your device'
    },
    {
      step: '2',
      icon: '🤖',
      title: 'AI Analysis',
      description: 'Our ML model analyzes market data and predicts value'
    },
    {
      step: '3',
      icon: '💰',
      title: 'Get Instant Price',
      description: 'Receive accurate resale price prediction immediately'
    },
    {
      step: '4',
      icon: '🚀',
      title: 'Sell with Confidence',
      description: 'Use the prediction to negotiate or list your device'
    }
  ]

  return (
    <div className="min-h-screen bg-black overflow-hidden relative">
      {/* Animated Background Gradient */}
      <div 
        className="fixed inset-0 opacity-20 pointer-events-none"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(16, 185, 129, 0.3), transparent 40%)`
        }}
      />

      {/* Floating Particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary-red rounded-full"
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
      <main className="relative z-10 px-6 py-16">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="text-6xl mb-6"
            >
              💰
            </motion.div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-white">Resale Your</span>
              <br />
              <span className="text-gradient">Tech Devices</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary-grey max-w-3xl mx-auto">
              AI-powered price predictions for your gadgets. Get accurate market value instantly!
            </p>
          </motion.div>

          {/* Stats Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
          >
            {[
              { label: 'Predictions Made', value: '10,000+', icon: '📊' },
              { label: 'Average Accuracy', value: '94%', icon: '🎯' },
              { label: 'Happy Users', value: '5,000+', icon: '😊' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                className="glass-effect rounded-xl p-6 text-center"
              >
                <div className="text-4xl mb-2">{stat.icon}</div>
                <div className="text-3xl font-bold text-gradient mb-1">{stat.value}</div>
                <div className="text-primary-grey">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>

          {/* Resale Options Grid */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mb-20"
          >
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              What Would You Like to <span className="text-gradient">Sell?</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {resaleOptions.map((option, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                  whileHover={{ scale: option.comingSoon ? 1 : 1.03, y: option.comingSoon ? 0 : -5 }}
                  className={`glass-effect rounded-xl p-8 ${option.comingSoon ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer group'}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl">{option.icon}</div>
                    {option.comingSoon && (
                      <span className="px-3 py-1 bg-primary-grey/30 text-primary-grey rounded-full text-xs font-semibold">
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-primary-green transition-colors">
                    {option.title}
                  </h3>
                  <p className="text-primary-grey mb-6">
                    {option.description}
                  </p>
                  
                  {!option.comingSoon && (
                    <>
                      <div className="flex justify-between mb-6 pb-6 border-b border-primary-grey/30">
                        <div>
                          <div className="text-sm text-primary-grey mb-1">Accuracy</div>
                          <div className="text-xl font-bold text-primary-green">{option.stats.accuracy}</div>
                        </div>
                        <div>
                          <div className="text-sm text-primary-grey mb-1">Avg. Price</div>
                          <div className="text-xl font-bold text-primary-green">{option.stats.avgPrice}</div>
                        </div>
                      </div>
                      <Link
                        to={option.link}
                        className={`block w-full py-3 bg-gradient-to-r ${option.gradient} text-white rounded-lg font-semibold text-center transition-all duration-300 transform group-hover:scale-105 shadow-lg`}
                      >
                        Get Price Prediction →
                      </Link>
                    </>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* How It Works Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="mb-20"
          >
            <h2 className="text-4xl font-bold text-white text-center mb-12">
              How <span className="text-gradient">It Works</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {howItWorks.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.9 + index * 0.1 }}
                  className="relative glass-effect rounded-xl p-6 text-center"
                >
                  {/* Step Number Badge */}
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 bg-gradient-to-r from-primary-red to-primary-green rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
                    {item.step}
                  </div>
                  <div className="text-5xl mb-4 mt-2">{item.icon}</div>
                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-primary-grey text-sm">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* CTA Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
            className="text-center glass-effect rounded-xl p-12"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Find Your Device Value?
            </h2>
            <p className="text-xl text-primary-grey mb-8 max-w-2xl mx-auto">
              Join thousands of users who trust our AI-powered predictions for accurate device valuations
            </p>
            <div className="flex justify-center gap-6 flex-wrap">
              <Link
                to="/predictions/smartphone"
                className="px-8 py-4 bg-gradient-to-r from-primary-red to-red-600 hover:from-red-600 hover:to-primary-red text-white rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
              >
                📱 Predict Smartphone Price
              </Link>
              <Link
                to="/predictions/laptop"
                className="px-8 py-4 bg-gradient-to-r from-primary-green to-emerald-600 hover:from-emerald-600 hover:to-primary-green text-white rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-green/50"
              >
                💻 Predict Laptop Price
              </Link>
            </div>
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-primary-grey/30 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-primary-grey">
          <p>&copy; 2024 DealGoat. All rights reserved. Powered by AI & ML.</p>
        </div>
      </footer>
    </div>
  )
}

export default Resale

