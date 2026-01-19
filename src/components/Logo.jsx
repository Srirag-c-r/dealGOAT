import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const Logo = ({ size = 'md', showText = true, className = '', linkTo = '/' }) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
    xl: 'h-20 w-20'
  }

  const textSizeClasses = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-3xl',
    xl: 'text-4xl'
  }

  return (
    <Link 
      to={linkTo} 
      className={`flex items-center gap-3 ${className}`}
    >
      <motion.img
        src="/logo.png"
        alt="DealGoat Logo"
        className={`${sizeClasses[size]} object-contain`}
        whileHover={{ scale: 1.05 }}
        transition={{ duration: 0.2 }}
      />
      {showText && (
        <span className={`font-bold text-gradient ${textSizeClasses[size]}`}>
          DealGoat
        </span>
      )}
    </Link>
  )
}

export default Logo

