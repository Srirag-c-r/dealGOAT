import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import Logo from './Logo'

const UserNavbar = ({ user }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  const navLinks = [
    { name: 'Home', path: '/user-home', icon: '🏠' },
    { name: 'Resale', path: '/resale', icon: '💰' },
    { name: 'Marketplace', path: '/marketplace', icon: '🛍️' },
    { name: 'Messages', path: '/messages', icon: '💬' }
  ]

  return (
    <nav className="relative z-50 px-6 py-4 border-b border-primary-grey/20 backdrop-blur-md bg-black/50">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          {/* Logo Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center"
          >
            <Logo size="md" />
          </motion.div>

          {/* Desktop Navigation */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="hidden md:flex items-center gap-2"
          >
            {navLinks.map((link, index) => (
              <Link
                key={link.path}
                to={link.path}
                className={`
                  relative px-6 py-2.5 rounded-lg font-semibold transition-all duration-300
                  ${isActive(link.path)
                    ? 'bg-primary-red text-white shadow-lg shadow-primary-red/50'
                    : 'text-primary-grey hover:text-white hover:bg-primary-grey/10'
                  }
                `}
              >
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 + index * 0.1 }}
                  className="flex items-center gap-2"
                >
                  <span>{link.icon}</span>
                  <span>{link.name}</span>
                </motion.div>
              </Link>
            ))}
          </motion.div>

          {/* User Info & Logout Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="hidden md:flex items-center gap-4"
          >
            {/* User Profile Avatar */}
            <div className="w-10 h-10 rounded-full overflow-hidden border border-primary-red/30 bg-primary-red/10 flex-shrink-0">
              {user?.profile_picture ? (
                <img
                  src={user.profile_picture.startsWith('http') ? user.profile_picture : `http://localhost:8000${user.profile_picture}`}
                  alt="My Profile"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-sm font-bold text-white bg-primary-red">
                  {(user?.first_name || user?.email || 'U')[0].toUpperCase()}
                </div>
              )}
            </div>

            {/* User Welcome */}
            <div className="text-primary-grey">
              Welcome, <span className="text-white font-semibold">{user?.first_name || user?.email}</span>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="px-6 py-2.5 bg-gradient-to-r from-primary-red to-red-600 hover:from-red-600 hover:to-primary-red text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50 flex items-center gap-2"
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>
          </motion.div>

          {/* Mobile Menu Button */}
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="md:hidden text-white text-2xl"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? '✕' : '☰'}
          </motion.button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden mt-4 space-y-3 pb-4"
          >
            {/* User Info Mobile */}
            <div className="px-4 py-3 glass-effect rounded-lg">
              <p className="text-sm text-primary-grey">Welcome,</p>
              <p className="text-white font-semibold">{user?.first_name || user?.email}</p>
            </div>

            {/* Nav Links Mobile */}
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMenuOpen(false)}
                className={`
                  block px-4 py-3 rounded-lg font-semibold transition-all duration-300
                  ${isActive(link.path)
                    ? 'bg-primary-red text-white shadow-lg shadow-primary-red/50'
                    : 'text-primary-grey hover:text-white hover:bg-primary-grey/10'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{link.icon}</span>
                  <span>{link.name}</span>
                </div>
              </Link>
            ))}

            {/* Logout Mobile */}
            <button
              onClick={handleLogout}
              className="w-full px-4 py-3 bg-gradient-to-r from-primary-red to-red-600 text-white rounded-lg font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg shadow-primary-red/50"
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>
          </motion.div>
        )}
      </div>
    </nav>
  )
}

export default UserNavbar

