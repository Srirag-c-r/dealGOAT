import { motion, AnimatePresence } from 'framer-motion'
import { useEffect } from 'react'

const MessagePopup = ({ type, message, onClose, duration = 5000 }) => {
  useEffect(() => {
    if (type === 'success' || type === 'error' || type === 'warning' || type === 'info') {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [type, duration, onClose])

  if (!message) return null

  const config = {
    success: {
      bg: 'bg-primary-green',
      icon: '✓',
      border: 'border-primary-green'
    },
    error: {
      bg: 'bg-primary-red',
      icon: '✕',
      border: 'border-primary-red'
    },
    warning: {
      bg: 'bg-yellow-500',
      icon: '⚠',
      border: 'border-yellow-500'
    },
    info: {
      bg: 'bg-primary-grey',
      icon: 'ℹ',
      border: 'border-primary-grey'
    }
  }

  const style = config[type] || config.info

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -50, scale: 0.9 }}
        className="fixed top-4 right-4 z-50 max-w-md w-full"
      >
        <div className={`${style.bg} border-2 ${style.border} rounded-lg p-4 shadow-2xl flex items-start gap-3`}>
          <div className="text-2xl font-bold text-white flex-shrink-0">{style.icon}</div>
          <div className="flex-1">
            <p className="text-white font-semibold">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-black transition-colors flex-shrink-0"
          >
            ✕
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

export default MessagePopup

