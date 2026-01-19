import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState } from 'react'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'
import Logo from '../components/Logo'
import { validateEmail } from '../utils/validation'

const ForgotPassword = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [emailSent, setEmailSent] = useState(false)
  const [validation, setValidation] = useState({ isValid: false, isTouched: false, message: '' })

  const handleEmailChange = (value) => {
    setEmail(value)
    setValidation({ ...validateEmail(value), isTouched: true })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validation.isValid) {
      setMessage({ type: 'error', text: 'Please enter a valid email address.' })
      return
    }

    setIsSubmitting(true)
    try {
      const response = await api.requestPasswordReset({ email: email.trim().toLowerCase() })

      if (response.success) {
        setEmailSent(true)
        setMessage({
          type: 'success',
          text: response.message || 'Password reset link sent to your email!'
        })

        // If token is provided in debug mode, show it
        if (response.token && response.reset_url) {
          console.log('Reset Token (DEBUG):', response.token)
          console.log('Reset URL (DEBUG):', response.reset_url)
        }
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to send password reset email.' })
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
          <h2 className="text-3xl font-bold text-white mb-2">Forgot Password?</h2>
          <p className="text-primary-grey">
            {emailSent
              ? 'Check your email for password reset instructions'
              : 'Enter your email address and we\'ll send you a link to reset your password'
            }
          </p>
        </div>

        {!emailSent ? (
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-white mb-2">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                onBlur={() => setValidation(prev => ({ ...prev, isTouched: true }))}
                className={`w-full px-4 py-3 bg-black/50 border rounded-lg text-white focus:outline-none transition-colors ${validation.isTouched && !validation.isValid ? 'border-primary-red' : 'border-primary-grey/30 focus:border-primary-green'}`}
                placeholder="your@email.com"
                required
              />
              {validation.isTouched && !validation.isValid && (
                <p className="text-primary-red text-sm mt-1">{validation.message}</p>
              )}
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 bg-primary-red hover:bg-primary-red/80 disabled:bg-primary-grey disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
            >
              {isSubmitting ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="text-center py-4">
              <div className="text-6xl mb-4">📧</div>
              <p className="text-white mb-2">Email sent successfully!</p>
              <p className="text-primary-grey text-sm">
                Please check your inbox (and spam folder) for the password reset link.
              </p>
            </div>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-3 bg-primary-green hover:bg-primary-green/80 text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-green/50"
            >
              Back to Login
            </button>
          </div>
        )}

        <div className="mt-6 text-center">
          <Link to="/login" className="text-primary-grey hover:text-white transition-colors text-sm">
            ← Back to Login
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

export default ForgotPassword

