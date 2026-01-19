import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const OTPVerification = ({ email, onVerify, onResend, onClose }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [isVerifying, setIsVerifying] = useState(false)
  const inputRefs = useRef([])

  useEffect(() => {
    inputRefs.current[0]?.focus()
  }, [])

  const handleChange = (index, value) => {
    if (!/^\d*$/.test(value)) return

    const newOtp = [...otp]
    newOtp[index] = value.slice(-1)
    setOtp(newOtp)

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text').slice(0, 6)
    if (/^\d+$/.test(pastedData)) {
      const newOtp = pastedData.split('').concat(Array(6 - pastedData.length).fill(''))
      setOtp(newOtp.slice(0, 6))
      inputRefs.current[Math.min(pastedData.length, 5)]?.focus()
    }
  }

  const handleVerify = async () => {
    const otpString = otp.join('')
    if (otpString.length !== 6) return

    setIsVerifying(true)
    try {
      await onVerify(otpString)
    } catch (error) {
      console.error('OTP verification failed:', error)
    } finally {
      setIsVerifying(false)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center px-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="glass-effect rounded-2xl p-8 max-w-md w-full"
        >
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">Verify Your Email</h3>
            <p className="text-primary-grey text-sm">
              We've sent a 6-digit code to
            </p>
            <p className="text-primary-green font-semibold">{email}</p>
          </div>

          <div className="flex justify-center gap-2 mb-6">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (inputRefs.current[index] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                className="w-12 h-14 text-center text-2xl font-bold bg-black/50 border-2 border-primary-grey/30 rounded-lg text-white focus:outline-none focus:border-primary-green transition-colors"
              />
            ))}
          </div>

          <button
            onClick={handleVerify}
            disabled={otp.join('').length !== 6 || isVerifying}
            className="w-full py-3 bg-primary-green hover:bg-primary-green/80 disabled:bg-primary-grey disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all duration-300 mb-4"
          >
            {isVerifying ? 'Verifying...' : 'Verify OTP'}
          </button>

          <div className="text-center">
            <button
              onClick={onResend}
              className="text-primary-grey hover:text-primary-green text-sm transition-colors"
            >
              Didn't receive code? <span className="font-semibold">Resend</span>
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default OTPVerification

