import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import api from '../services/api'
import MessagePopup from '../components/MessagePopup'
import Logo from '../components/Logo'
import { validatePassword, validateConfirmPassword } from '../utils/validation'

const ResetPassword = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [validations, setValidations] = useState({
    password: { isValid: false, isTouched: false, message: '' },
    confirmPassword: { isValid: false, isTouched: false, message: '' }
  })
  const [tokenValid, setTokenValid] = useState(null)
  const [email, setEmail] = useState('')

  const handlePasswordChange = (value) => {
    setPassword(value)
    const v = validatePassword(value)
    setValidations(prev => ({
      ...prev,
      password: { ...v, isTouched: true },
      confirmPassword: { ...validateConfirmPassword(value, confirmPassword), isTouched: prev.confirmPassword.isTouched }
    }))
  }

  const handleConfirmPasswordChange = (value) => {
    setConfirmPassword(value)
    setValidations(prev => ({
      ...prev,
      confirmPassword: { ...validateConfirmPassword(password, value), isTouched: true }
    }))
  }

  useEffect(() => {
    // Verify token when component mounts
    if (token) {
      verifyToken()
    } else {
      setMessage({ type: 'error', text: 'Invalid reset link. Please request a new password reset.' })
      setTokenValid(false)
    }
  }, [token])

  const verifyToken = async () => {
    try {
      const response = await api.verifyPasswordResetToken({ token })
      if (response.success) {
        setTokenValid(true)
        setEmail(response.email || '')
      } else {
        setTokenValid(false)
        setMessage({ type: 'error', text: response.message || 'Invalid or expired reset token.' })
      }
    } catch (error) {
      setTokenValid(false)
      setMessage({ type: 'error', text: error.message || 'Invalid or expired reset token.' })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validations.password.isValid || !validations.confirmPassword.isValid) {
      setMessage({ type: 'error', text: 'Please fix the errors before submitting.' })
      return
    }

    if (!token) {
      setMessage({ type: 'error', text: 'Invalid reset token.' })
      return
    }

    setIsSubmitting(true)
    try {
      const response = await api.resetPassword({
        token,
        new_password: password,
        confirm_password: confirmPassword
      })

      if (response.success) {
        setMessage({
          type: 'success',
          text: response.message || 'Password reset successfully! Redirecting to login...'
        })
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to reset password.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  if (tokenValid === null) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="glass-effect rounded-2xl p-8 md:p-12 max-w-md w-full text-center"
        >
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-white">Verifying reset token...</p>
        </motion.div>
      </div>
    )
  }

  if (tokenValid === false) {
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
            <h2 className="text-3xl font-bold text-white mb-2">Invalid Reset Link</h2>
            <p className="text-primary-grey">
              This password reset link is invalid or has expired.
            </p>
          </div>
          <div className="space-y-4">
            <Link
              to="/forgot-password"
              className="block w-full py-3 bg-primary-red hover:bg-primary-red/80 text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50 text-center"
            >
              Request New Reset Link
            </Link>
            <Link
              to="/login"
              className="block w-full py-3 border-2 border-primary-grey text-white rounded-lg font-semibold hover:border-primary-green hover:text-primary-green transition-all duration-300 text-center"
            >
              Back to Login
            </Link>
          </div>
        </motion.div>
      </div>
    )
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
          <h2 className="text-3xl font-bold text-white mb-2">Reset Password</h2>
          <p className="text-primary-grey">
            {email && `Enter a new password for ${email}`}
            {!email && 'Enter your new password'}
          </p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="block text-white mb-2">New Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => handlePasswordChange(e.target.value)}
              onBlur={() => setValidations(prev => ({ ...prev, password: { ...prev.password, isTouched: true } }))}
              className={`w-full px-4 py-3 bg-black/50 border rounded-lg text-white focus:outline-none transition-colors ${validations.password.isTouched && !validations.password.isValid ? 'border-primary-red' : 'border-primary-grey/30 focus:border-primary-green'}`}
              placeholder="••••••••"
              required
            />
            {validations.password.isTouched && !validations.password.isValid && (
              <p className="text-primary-red text-sm mt-1">{validations.password.message}</p>
            )}
            <p className="text-primary-grey text-xs mt-1">Must be at least 8 characters</p>
          </div>
          <div>
            <label className="block text-white mb-2">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => handleConfirmPasswordChange(e.target.value)}
              onBlur={() => setValidations(prev => ({ ...prev, confirmPassword: { ...prev.confirmPassword, isTouched: true } }))}
              className={`w-full px-4 py-3 bg-black/50 border rounded-lg text-white focus:outline-none transition-colors ${validations.confirmPassword.isTouched && !validations.confirmPassword.isValid ? 'border-primary-red' : 'border-primary-grey/30 focus:border-primary-green'}`}
              placeholder="••••••••"
              required
            />
            {validations.confirmPassword.isTouched && !validations.confirmPassword.isValid && (
              <p className="text-primary-red text-sm mt-1">{validations.confirmPassword.message}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-primary-red hover:bg-primary-red/80 disabled:bg-primary-grey disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-red/50"
          >
            {isSubmitting ? 'Resetting Password...' : 'Reset Password'}
          </button>
        </form>

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

export default ResetPassword

