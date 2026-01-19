import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState } from 'react'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'
import Logo from '../components/Logo'
import { validateEmail } from '../utils/validation'

const Login = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [validations, setValidations] = useState({
    email: { isValid: false, isTouched: false, message: '' }
  })

  const handleEmailChange = (value) => {
    setEmail(value)
    const validation = validateEmail(value)
    setValidations(prev => ({
      ...prev,
      email: { ...validation, isTouched: true }
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validations.email.isValid || !password) {
      setMessage({ type: 'error', text: 'Please enter a valid email and password.' })
      return
    }

    setIsSubmitting(true)
    try {
      const response = await api.login({ email: email.trim().toLowerCase(), password })
      // Store user data and token in localStorage
      if (response.user) {
        localStorage.setItem('user', JSON.stringify(response.user))
      }
      if (response.token) {
        localStorage.setItem('token', response.token)
      }
      setMessage({ type: 'success', text: 'Login successful! Redirecting...' })
      setTimeout(() => {
        navigate('/user-home')
      }, 1500)
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Login failed. Please check your credentials.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-effect rounded-2xl p-8 md:p-12 max-w-md w-full"
      >
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="lg" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
          <p className="text-primary-grey">Sign in to your account</p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="block text-white mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => handleEmailChange(e.target.value)}
              onBlur={() => setValidations(prev => ({ ...prev, email: { ...prev.email, isTouched: true } }))}
              className={`w-full px-4 py-3 bg-black/50 border rounded-lg text-white focus:outline-none transition-colors ${validations.email.isTouched && !validations.email.isValid ? 'border-primary-red' : 'border-primary-grey/30 focus:border-primary-green'}`}
              placeholder="your@email.com"
            />
            {validations.email.isTouched && !validations.email.isValid && (
              <p className="text-primary-red text-sm mt-1">{validations.email.message}</p>
            )}
          </div>
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-white">Password</label>
              <Link
                to="/forgot-password"
                className="text-primary-green hover:text-primary-green/80 text-sm transition-colors"
              >
                Forgot Password?
              </Link>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-black/50 border border-primary-grey/30 rounded-lg text-white focus:outline-none focus:border-primary-green transition-colors"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-primary-red hover:bg-primary-red/80 disabled:bg-primary-grey disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
          >
            {isSubmitting ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-primary-grey">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-green hover:text-primary-green/80 transition-colors">
              Register
            </Link>
          </p>
        </div>

        <div className="mt-6 text-center">
          <Link to="/" className="text-primary-grey hover:text-white transition-colors text-sm">
            ← Back to Home
          </Link>
        </div>
      </motion.div>

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

export default Login

