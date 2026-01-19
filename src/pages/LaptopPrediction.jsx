import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'
import axios from 'axios'
import {
  validateModel,
  validatePrice,
  validateLocation
} from '../utils/validation'

const LaptopPrediction = () => {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [predictionResult, setPredictionResult] = useState(null)
  const [error, setError] = useState(null)

  // Form data
  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    launch_year: 2022,
    launch_price: '',
    processor: '',
    ram: 8,
    storage_type: 'SSD',
    storage_size: 512,
    gpu: '',
    screen_size: 15.6,
    battery_cycle_count: 100,
    condition: 'Good',
    warranty_remaining: 0,
    seller_location: ''
  })

  const [validations, setValidations] = useState({
    brand: { isValid: false, isTouched: false, message: '' },
    model: { isValid: true, isTouched: false, message: '' }, // Model is optional in this form sometimes, but let's validate if entered
    launch_price: { isValid: false, isTouched: false, message: '' },
    seller_location: { isValid: false, isTouched: false, message: '' }
  })

  // Dropdown options
  const [specs, setSpecs] = useState({
    brands: [],
    processors: [],
    gpus: [],
    ram_options: [],
    storage_options: [],
    storage_types: [],
    screen_sizes: [],
    conditions: []
  })

  useEffect(() => {
    // Check authentication
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    } else {
      navigate('/login')
    }

    // Fetch specs for dropdowns
    fetchSpecs()
  }, [navigate])

  const fetchSpecs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/predictions/specs/')
      if (response.data.success) {
        setSpecs(response.data.data)
      }
    } catch (err) {
      console.error('Error fetching specs:', err)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))

    // Real-time validation
    let validation = { isValid: true, message: '' }
    if (name === 'brand') {
      validation = value ? { isValid: true, message: '' } : { isValid: false, message: 'Brand is required' }
    } else if (name === 'model' && value) {
      validation = validateModel(value)
    } else if (name === 'launch_price') {
      validation = validatePrice(value, 10000, 500000)
    } else if (name === 'seller_location') {
      validation = validateLocation(value)
    }

    if (validations[name]) {
      setValidations(prev => ({
        ...prev,
        [name]: { ...validation, isTouched: true }
      }))
    }
  }

  const handleBlur = (field) => {
    setValidations(prev => ({
      ...prev,
      [field]: { ...prev[field], isTouched: true }
    }))
  }

  const getFieldClassName = (field, baseClass = "") => {
    const validation = validations[field]
    if (!validation || !validation.isTouched) {
      return `${baseClass} border-primary-grey/30 focus:border-primary-red`
    }
    if (validation.isValid) {
      return `${baseClass} border-primary-green border-2`
    }
    return `${baseClass} border-primary-red border-2`
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPredictionResult(null)

    try {
      const response = await axios.post(
        'http://localhost:8000/api/predictions/laptop/',
        formData
      )

      if (response.data.success) {
        setPredictionResult(response.data)
        // Scroll to results
        setTimeout(() => {
          document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' })
        }, 100)
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Prediction failed. Please try again.')
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-black overflow-hidden relative">
      {/* Background Effects */}
      <div className="fixed inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-red via-black to-primary-green" />
      </div>

      {/* Navigation */}
      <UserNavbar user={user} />

      {/* Main Content */}
      <main className="relative z-10 px-6 py-16">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <div className="text-6xl mb-4">💻</div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="text-white">Laptop Price</span>
              <br />
              <span className="text-gradient">Prediction</span>
            </h1>
            <p className="text-xl text-primary-grey max-w-2xl mx-auto">
              Get an accurate AI-powered prediction of your laptop's resale value
            </p>
          </motion.div>

          {/* Form */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="glass-effect rounded-xl p-8 mb-8"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Brand & Model */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Brand <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="brand"
                    value={formData.brand}
                    onChange={handleInputChange}
                    onBlur={() => handleBlur('brand')}
                    required
                    className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('brand')}`}
                  >
                    <option value="">Select Brand</option>
                    {specs.brands.map((brand) => (
                      <option key={brand} value={brand}>{brand}</option>
                    ))}
                  </select>
                  {validations.brand.isTouched && !validations.brand.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.brand.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Model
                  </label>
                  <input
                    type="text"
                    name="model"
                    value={formData.model}
                    onChange={handleInputChange}
                    onBlur={() => handleBlur('model')}
                    placeholder="e.g., Inspiron 15 5000"
                    className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('model')}`}
                  />
                  {validations.model.isTouched && !validations.model.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.model.message}</p>
                  )}
                </div>
              </div>

              {/* Launch Year & Price */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Launch Year <span className="text-primary-red">*</span>
                  </label>
                  <input
                    type="number"
                    name="launch_year"
                    value={formData.launch_year}
                    onChange={handleInputChange}
                    min="2010"
                    max="2025"
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Launch Price (₹) <span className="text-primary-red">*</span>
                  </label>
                  <input
                    type="number"
                    name="launch_price"
                    value={formData.launch_price}
                    onChange={handleInputChange}
                    onBlur={() => handleBlur('launch_price')}
                    min="10000"
                    max="500000"
                    required
                    placeholder="e.g., 65000"
                    className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('launch_price')}`}
                  />
                  {validations.launch_price.isTouched && !validations.launch_price.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.launch_price.message}</p>
                  )}
                </div>
              </div>

              {/* Processor & GPU */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Processor <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="processor"
                    value={formData.processor}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    <option value="">Select Processor</option>
                    {specs.processors.map((proc) => (
                      <option key={proc} value={proc}>{proc}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    GPU <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="gpu"
                    value={formData.gpu}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    <option value="">Select GPU</option>
                    {specs.gpus.map((gpu) => (
                      <option key={gpu} value={gpu}>{gpu}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* RAM & Storage Type */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    RAM (GB) <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="ram"
                    value={formData.ram}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    {specs.ram_options.map((ram) => (
                      <option key={ram} value={ram}>{ram} GB</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Storage Type <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="storage_type"
                    value={formData.storage_type}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    {specs.storage_types.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Storage Size & Screen Size */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Storage Size (GB) <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="storage_size"
                    value={formData.storage_size}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    {specs.storage_options.map((size) => (
                      <option key={size} value={size}>{size} GB</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Screen Size (inches) <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="screen_size"
                    value={formData.screen_size}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    {specs.screen_sizes.map((size) => (
                      <option key={size} value={size}>{size}"</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Condition & Warranty */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Condition <span className="text-primary-red">*</span>
                  </label>
                  <select
                    name="condition"
                    value={formData.condition}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  >
                    {specs.conditions.map((cond) => (
                      <option key={cond} value={cond}>{cond}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Warranty Remaining (months)
                  </label>
                  <input
                    type="number"
                    name="warranty_remaining"
                    value={formData.warranty_remaining}
                    onChange={handleInputChange}
                    min="0"
                    max="60"
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  />
                </div>
              </div>

              {/* Battery Cycles & Location */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white font-semibold mb-2">
                    Battery Cycle Count
                  </label>
                  <input
                    type="number"
                    name="battery_cycle_count"
                    value={formData.battery_cycle_count}
                    onChange={handleInputChange}
                    min="0"
                    max="2000"
                    className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-red focus:outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white font-semibold mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    name="seller_location"
                    value={formData.seller_location}
                    onChange={handleInputChange}
                    onBlur={() => handleBlur('seller_location')}
                    placeholder="e.g., Mumbai"
                    className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('seller_location')}`}
                  />
                  {validations.seller_location.isTouched && !validations.seller_location.isValid && (
                    <p className="text-primary-red text-sm mt-1">{validations.seller_location.message}</p>
                  )}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading || !validations.brand.isValid || !validations.launch_price.isValid || !validations.seller_location.isValid}
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
                className="w-full py-4 bg-gradient-to-r from-primary-red to-red-600 text-white rounded-lg font-semibold text-lg transition-all duration-300 shadow-lg shadow-primary-red/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Predicting...
                  </span>
                ) : (
                  '🔮 Get Price Prediction'
                )}
              </motion.button>
            </form>
          </motion.div>

          {/* Prediction Results */}
          {predictionResult && (
            <motion.div
              id="results"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="glass-effect rounded-xl p-8 mb-8"
            >
              <div className="text-center mb-8">
                <div className="text-5xl mb-4">🎉</div>
                <h2 className="text-4xl font-bold text-white mb-2">Prediction Complete!</h2>
                <p className="text-primary-grey">Here's your laptop's estimated resale value</p>
              </div>

              {/* Price Display */}
              <div className="bg-gradient-to-r from-primary-red to-red-600 rounded-xl p-8 mb-8 text-center">
                <div className="text-primary-grey text-sm mb-2">Estimated Resale Price</div>
                <div className="text-5xl md:text-6xl font-bold text-white mb-2">
                  ₹{predictionResult.prediction.predicted_price.toLocaleString()}
                </div>
                <div className="text-white/80">
                  Range: ₹{predictionResult.prediction.price_range.min.toLocaleString()} -
                  ₹{predictionResult.prediction.price_range.max.toLocaleString()}
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-primary-darkGrey rounded-lg p-6 text-center">
                  <div className="text-3xl mb-2">🎯</div>
                  <div className="text-2xl font-bold text-primary-green mb-1">
                    {predictionResult.prediction.confidence_score}%
                  </div>
                  <div className="text-primary-grey text-sm">Confidence Score</div>
                </div>

                <div className="bg-primary-darkGrey rounded-lg p-6 text-center">
                  <div className="text-3xl mb-2">📊</div>
                  <div className="text-2xl font-bold text-primary-green mb-1">
                    {(predictionResult.model_info.r2_score * 100).toFixed(2)}%
                  </div>
                  <div className="text-primary-grey text-sm">Model Accuracy</div>
                </div>

                <div className="bg-primary-darkGrey rounded-lg p-6 text-center">
                  <div className="text-3xl mb-2">💸</div>
                  <div className="text-2xl font-bold text-primary-red mb-1">
                    {predictionResult.data.depreciation_percentage.toFixed(1)}%
                  </div>
                  <div className="text-primary-grey text-sm">Depreciation</div>
                </div>
              </div>

              {/* Device Info */}
              <div className="bg-primary-darkGrey rounded-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4">📝 Device Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-primary-grey">Brand:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.brand}</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Launch Price:</span>
                    <span className="text-white ml-2 font-semibold">₹{predictionResult.data.launch_price}</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Processor:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.processor}</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">RAM:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.ram} GB</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Storage:</span>
                    <span className="text-white ml-2 font-semibold">
                      {predictionResult.data.storage_size} GB {predictionResult.data.storage_type}
                    </span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Condition:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.condition}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mt-8">
                <button
                  onClick={() => {
                    setPredictionResult(null)
                    window.scrollTo({ top: 0, behavior: 'smooth' })
                  }}
                  className="flex-1 py-3 border-2 border-primary-grey text-white rounded-lg font-semibold hover:border-primary-green hover:text-primary-green transition-all duration-300"
                >
                  New Prediction
                </button>
                <button
                  onClick={() => navigate('/resale')}
                  className="flex-1 py-3 bg-primary-green text-white rounded-lg font-semibold hover:bg-primary-green/80 transition-all duration-300"
                >
                  View Other Options
                </button>
              </div>

              {/* SELL NOW BUTTON */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 p-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-center border border-blue-400/30 shadow-lg shadow-blue-500/20"
              >
                <h3 className="text-2xl font-bold text-white mb-2">Ready to sell this device?</h3>
                <p className="text-blue-100 mb-6">Create a verified listing instantly with this predicted price.</p>
                <button
                  onClick={() => navigate('/sell-device', {
                    state: {
                      predictionData: predictionResult.data,
                      deviceType: 'laptop'
                    }
                  })}
                  className="w-full md:w-auto px-8 py-3 bg-white text-blue-600 rounded-full font-bold hover:bg-blue-50 transition-all transform hover:scale-105 shadow-md"
                >
                  🚀 Sell Now for ₹{predictionResult.prediction.predicted_price.toLocaleString()}
                </button>
              </motion.div>

            </motion.div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-primary-grey/30 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-primary-grey">
          <p>&copy; 2024 DealGoat. AI-Powered Price Predictions.</p>
        </div>
      </footer>
    </div>
  )
}

export default LaptopPrediction

