import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import Logo from '../components/Logo'

const HomePage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const features = [
    {
      icon: '📱',
      title: 'Smartphone Price Prediction',
      description: 'Get accurate resale value predictions using AI',
      color: 'from-primary-red to-primary-red/50'
    },
    {
      icon: '💻',
      title: 'Laptop Price Prediction',
      description: 'Know your device worth before selling',
      color: 'from-primary-green to-primary-green/50'
    },
    {
      icon: '🤖',
      title: 'AI Tech Advisor',
      description: '24/7 intelligent chatbot for tech queries',
      color: 'from-primary-red to-primary-green'
    },
    {
      icon: '💬',
      title: 'Live Chat',
      description: 'Real-time discussions with tech enthusiasts',
      color: 'from-primary-green to-primary-red'
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
      <nav className="relative z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Logo size="md" />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex gap-4"
          >
            <Link
              to="/login"
              className="px-6 py-2 text-primary-grey hover:text-white transition-colors duration-300"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="px-6 py-2 bg-primary-red hover:bg-primary-red/80 text-white rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
            >
              Register
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          {/* Main Heading */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <h1 className="text-6xl md:text-8xl font-bold mb-6">
              <span className="text-white">AI-Powered</span>
              <br />
              <span className="text-gradient">Tech Advisor</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary-grey max-w-3xl mx-auto">
              Make smart decisions when buying or selling tech products with the power of AI
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex justify-center gap-6 mb-20"
          >
            <Link
              to="/register"
              className="group relative px-8 py-4 bg-primary-red text-white rounded-lg font-semibold text-lg overflow-hidden transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
            >
              <span className="relative z-10">Get Started</span>
              <div className="absolute inset-0 bg-primary-green transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
            </Link>
            <Link
              to="/login"
              className="px-8 py-4 border-2 border-primary-grey text-white rounded-lg font-semibold text-lg hover:border-primary-green hover:text-primary-green transition-all duration-300"
            >
              Sign In
            </Link>
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
                <p className="text-primary-grey text-sm">
                  {feature.description}
                </p>
                <div className={`mt-4 h-1 bg-gradient-to-r ${feature.color} rounded-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300`} />
              </motion.div>
            ))}
          </motion.div>

          {/* Stats Section */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20"
          >
            {[
              { number: '82K+', label: 'Price Predictions' },
              { number: '24/7', label: 'AI Support' },
              { number: '100%', label: 'Free to Use' },
              { number: 'AI', label: 'Powered' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.9 + index * 0.1 }}
                className="text-center glass-effect rounded-xl p-6"
              >
                <div className="text-4xl font-bold text-gradient mb-2">{stat.number}</div>
                <div className="text-primary-grey">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>

          {/* How It Works Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="text-center"
          >
            <h2 className="text-4xl font-bold mb-12 text-white">
              How It <span className="text-gradient">Works</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              {[
                { step: '01', title: 'Enter Device Details', desc: 'Provide basic information about your device' },
                { step: '02', title: 'AI Analysis', desc: 'Our ML models analyze and predict accurate prices' },
                { step: '03', title: 'Get Results', desc: 'Receive instant predictions and recommendations' }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 1.2 + index * 0.2 }}
                  className="relative"
                >
                  <div className="text-6xl font-bold text-primary-red/20 mb-4">{item.step}</div>
                  <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-primary-grey">{item.desc}</p>
                  {index < 2 && (
                    <div className="hidden md:block absolute top-10 left-full w-full h-0.5 bg-gradient-to-r from-primary-red to-primary-green transform translate-x-4" />
                  )}
                </motion.div>
              ))}
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

export default HomePage

