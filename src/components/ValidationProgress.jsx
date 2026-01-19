import { motion } from 'framer-motion'

const ValidationProgress = ({ validations }) => {
  const totalFields = Object.keys(validations).length
  const validatedFields = Object.values(validations).filter(v => v.isValid).length
  const progress = (validatedFields / totalFields) * 100

  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-primary-grey">Validation Progress</span>
        <span className="text-sm font-semibold text-white">{validatedFields}/{totalFields}</span>
      </div>
      <div className="w-full bg-primary-darkGrey rounded-full h-2 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-primary-red to-primary-green"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        {Object.entries(validations).map(([field, validation]) => (
          <div key={field} className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${validation.isValid ? 'bg-primary-green' : validation.isTouched ? 'bg-primary-red' : 'bg-primary-grey'}`} />
            <span className={`capitalize ${validation.isValid ? 'text-primary-green' : validation.isTouched ? 'text-primary-red' : 'text-primary-grey'}`}>
              {field.replace(/([A-Z])/g, ' $1').trim()}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ValidationProgress

