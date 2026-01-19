import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import ValidationProgress from '../components/ValidationProgress'
import OTPVerification from '../components/OTPVerification'
import MessagePopup from '../components/MessagePopup'
import api from '../services/api'
import Logo from '../components/Logo'
import {
  validateFirstName,
  validateLastName,
  validateEmail,
  validatePhone,
  validateLocation,
  validateGender,
  validateAge,
  validatePassword,
  validateConfirmPassword
} from '../utils/validation'

const Register = () => {
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    location: '',
    gender: '',
    age: '',
    password: '',
    confirmPassword: ''
  })

  const [validations, setValidations] = useState({
    firstName: { isValid: false, isTouched: false, message: '' },
    lastName: { isValid: false, isTouched: false, message: '' },
    email: { isValid: false, isTouched: false, message: '' },
    phone: { isValid: false, isTouched: false, message: '' },
    location: { isValid: false, isTouched: false, message: '' },
    gender: { isValid: false, isTouched: false, message: '' },
    age: { isValid: false, isTouched: false, message: '' },
    password: { isValid: false, isTouched: false, message: '' },
    confirmPassword: { isValid: false, isTouched: false, message: '' }
  })

  const [showOTP, setShowOTP] = useState(false)
  const [emailVerified, setEmailVerified] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Validate on change
    let validation
    if (field === 'confirmPassword') {
      validation = validateConfirmPassword(formData.password, value)
    } else {
      const validators = {
        firstName: validateFirstName,
        lastName: validateLastName,
        email: validateEmail,
        phone: validatePhone,
        location: validateLocation,
        gender: validateGender,
        age: validateAge,
        password: validatePassword
      }
      validation = validators[field] ? validators[field](value) : { isValid: true, message: '' }
    }

    setValidations(prev => ({
      ...prev,
      [field]: {
        ...validation,
        isTouched: true
      }
    }))
  }

  const handleBlur = (field) => {
    setValidations(prev => ({
      ...prev,
      [field]: { ...prev[field], isTouched: true }
    }))
  }

  const handleSendOTP = async () => {
    try {
      // Check email availability first
      const emailCheck = await api.checkEmail(formData.email)
      if (!emailCheck.available) {
        setMessage({ type: 'error', text: 'This email is already registered. Please use a different email.' })
        return
      }
      
      // Send OTP
      const response = await api.sendOTP(formData.email)
      
      // Check if email was actually sent
      if (response.email_sent) {
        setShowOTP(true)
        setMessage({ type: 'success', text: 'OTP sent to your email! Please check your inbox (and spam folder).' })
      } else {
        // Email not sent, but OTP was generated
        setShowOTP(true)
        let messageText = response.message || 'OTP generated successfully.'
        
        // If OTP is provided in debug mode, show it
        if (response.otp) {
          messageText += ` OTP Code: ${response.otp} (Check Django terminal for details)`
        } else {
          messageText += ' Check Django terminal/console for the OTP code.'
        }
        
        // Show warning if email configuration is missing
        if (response.error) {
          setMessage({ 
            type: 'warning', 
            text: `${messageText} Note: ${response.error}` 
          })
        } else {
          setMessage({ type: 'info', text: messageText })
        }
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to send OTP. Please try again.' })
    }
  }

  const handleVerifyOTP = async (otp) => {
    try {
      await api.verifyOTP(formData.email, otp)
      setEmailVerified(true)
      setShowOTP(false)
      setMessage({ type: 'success', text: 'Email verified successfully! Please complete your profile.' })
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Invalid OTP. Please try again.' })
      throw error
    }
  }

  const handleResendOTP = async () => {
    await handleSendOTP()
  }

  const isFormValid = () => {
    return Object.values(validations).every(v => v.isValid) && emailVerified
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate all fields
    const allValidations = {
      firstName: validateFirstName(formData.firstName),
      lastName: validateLastName(formData.lastName),
      phone: validatePhone(formData.phone),
      location: validateLocation(formData.location),
      gender: validateGender(formData.gender),
      age: validateAge(formData.age),
      password: validatePassword(formData.password),
      confirmPassword: validateConfirmPassword(formData.password, formData.confirmPassword)
    }

    const allValid = Object.values(allValidations).every(v => v.isValid)

    if (!allValid) {
      setMessage({ type: 'error', text: 'Please fix all validation errors before submitting.' })
      // Mark all as touched
      setValidations(prev => {
        const updated = { ...prev }
        Object.keys(updated).forEach(key => {
          updated[key] = {
            ...allValidations[key],
            isTouched: true
          }
        })
        return updated
      })
      return
    }

    if (!emailVerified) {
      setMessage({ type: 'error', text: 'Please verify your email address first.' })
      return
    }

    setIsSubmitting(true)

    try {
      // Prepare data for backend
      const registrationData = {
        first_name: formData.firstName.trim(),
        last_name: formData.lastName.trim(),
        email: formData.email.trim().toLowerCase(),
        phone: formData.phone.replace(/[\s\-\(\)]/g, ''),
        location: formData.location.trim(),
        gender: formData.gender,
        age: parseInt(formData.age),
        password: formData.password,
        confirm_password: formData.confirmPassword
      }

      // Complete the registration for the verified email
      await api.completeRegistration(registrationData)
      
      setMessage({ type: 'success', text: 'Registration successful! Redirecting to login...' })
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Registration failed. Please try again.' 
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const getFieldClassName = (field) => {
    const validation = validations[field]
    if (!validation.isTouched) {
      return 'w-full px-4 py-3 bg-black/50 border border-primary-grey/30 rounded-lg text-white focus:outline-none focus:border-primary-green transition-colors'
    }
    if (validation.isValid) {
      return 'w-full px-4 py-3 bg-black/50 border-2 border-primary-green rounded-lg text-white focus:outline-none transition-colors'
    }
    return 'w-full px-4 py-3 bg-black/50 border-2 border-primary-red rounded-lg text-white focus:outline-none transition-colors'
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 py-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-effect rounded-2xl p-6 md:p-10 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            <Logo size="lg" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Create Account</h2>
          <p className="text-primary-grey">Join DealGoat and start predicting</p>
        </div>

        <ValidationProgress validations={validations} />

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div>
            <label className="block text-white mb-2">
              Email <span className="text-primary-red">*</span>
            </label>
            <div className="flex gap-2">
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                onBlur={() => handleBlur('email')}
                className={getFieldClassName('email')}
                placeholder="your@email.com"
                disabled={emailVerified}
              />
              {validations.email.isValid && !emailVerified && (
                <button
                  type="button"
                  onClick={handleSendOTP}
                  className="px-4 py-3 bg-primary-green hover:bg-primary-green/80 text-white rounded-lg font-semibold transition-all duration-300 whitespace-nowrap"
                >
                  Verify Email
                </button>
              )}
              {emailVerified && (
                <div className="px-4 py-3 bg-primary-green text-white rounded-lg flex items-center gap-2">
                  <span>✓</span>
                  <span>Verified</span>
                </div>
              )}
            </div>
            {validations.email.isTouched && !validations.email.isValid && (
              <p className="text-primary-red text-sm mt-1">{validations.email.message}</p>
            )}
          </div>

          {emailVerified && (
            <>
              {/* First Name & Last Name */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-white mb-2">
                    First Name <span className="text-primary-red">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => handleChange('firstName', e.target.value)}
                    onBlur={() => handleBlur('firstName')}
                    className={getFieldClassName('firstName')}
                    placeholder="John"
                  />
                  {validations.firstName.isTouched && !validations.firstName.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.firstName.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-white mb-2">
                    Last Name <span className="text-primary-red">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => handleChange('lastName', e.target.value)}
                    onBlur={() => handleBlur('lastName')}
                    className={getFieldClassName('lastName')}
                    placeholder="Doe"
                  />
                  {validations.lastName.isTouched && !validations.lastName.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.lastName.message}</p>
                  )}
                </div>
              </div>

              {/* Phone */}
              <div>
                <label className="block text-white mb-2">
                  Phone Number <span className="text-primary-red">*</span>
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  onBlur={() => handleBlur('phone')}
                  className={getFieldClassName('phone')}
                  placeholder="+1234567890"
                />
                {validations.phone.isTouched && !validations.phone.isValid && (
                  <p className="text-primary-red text-sm mt-1">{validations.phone.message}</p>
                )}
              </div>

              {/* Location */}
              <div>
                <label className="block text-white mb-2">
                  Place / Location <span className="text-primary-red">*</span>
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleChange('location', e.target.value)}
                  onBlur={() => handleBlur('location')}
                  className={getFieldClassName('location')}
                  placeholder="New York, USA"
                />
                {validations.location.isTouched && !validations.location.isValid && (
                  <p className="text-primary-red text-sm mt-1">{validations.location.message}</p>
                )}
              </div>

              {/* Gender & Age */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-white mb-2">
                    Gender <span className="text-primary-red">*</span>
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => handleChange('gender', e.target.value)}
                    onBlur={() => handleBlur('gender')}
                    className={getFieldClassName('gender')}
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                  </select>
                  {validations.gender.isTouched && !validations.gender.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.gender.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-white mb-2">
                    Age <span className="text-primary-red">*</span>
                  </label>
                  <input
                    type="number"
                    min="18"
                    max="120"
                    value={formData.age}
                    onChange={(e) => handleChange('age', e.target.value)}
                    onBlur={() => handleBlur('age')}
                    className={getFieldClassName('age')}
                    placeholder="25"
                  />
                  {validations.age.isTouched && !validations.age.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.age.message}</p>
                  )}
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-white mb-2">
                  Password <span className="text-primary-red">*</span>
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  onBlur={() => handleBlur('password')}
                  className={getFieldClassName('password')}
                  placeholder="••••••••"
                />
                {validations.password.isTouched && !validations.password.isValid && (
                  <p className="text-primary-red text-sm mt-1">{validations.password.message}</p>
                )}
                {validations.password.isValid && (
                  <p className="text-primary-green text-sm mt-1">✓ Password meets requirements</p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-white mb-2">
                  Confirm Password <span className="text-primary-red">*</span>
                </label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  onBlur={() => handleBlur('confirmPassword')}
                  className={getFieldClassName('confirmPassword')}
                  placeholder="••••••••"
                />
                {validations.confirmPassword.isTouched && !validations.confirmPassword.isValid && (
                  <p className="text-primary-red text-sm mt-1">{validations.confirmPassword.message}</p>
                )}
                {validations.confirmPassword.isValid && (
                  <p className="text-primary-green text-sm mt-1">✓ Passwords match</p>
                )}
              </div>

              <button
                type="submit"
                disabled={!isFormValid() || isSubmitting}
                className="w-full py-3 bg-primary-green hover:bg-primary-green/80 disabled:bg-primary-grey disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg shadow-primary-green/50"
              >
                {isSubmitting ? 'Creating Account...' : 'Create Account'}
              </button>
            </>

          )}
        </form>

        <div className="mt-6 text-center">
          <p className="text-primary-grey">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-red hover:text-primary-red/80 transition-colors">
              Sign In
            </Link>
          </p>
        </div>

        <div className="mt-4 text-center">
          <Link to="/" className="text-primary-grey hover:text-white transition-colors text-sm">
            ← Back to Home
          </Link>
        </div>
      </motion.div>

      {/* OTP Verification Modal */}
      {showOTP && (
        <OTPVerification
          email={formData.email}
          onVerify={handleVerifyOTP}
          onResend={handleResendOTP}
          onClose={() => setShowOTP(false)}
        />
      )}

      {/* Message Popup */}
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

export default Register
