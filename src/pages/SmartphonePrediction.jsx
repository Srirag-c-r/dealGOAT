import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import UserNavbar from '../components/UserNavbar'
import {
  validateModel,
  validatePrice,
  validateLocation,
  validateIMEI
} from '../utils/validation'

const brandOptions = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Nothing', 'Xiaomi', 'Realme', 'Poco', 'Motorola', 'Vivo', 'Oppo', 'Nokia', 'Asus', 'Tecno', 'Infinix', 'Other']
const processorOptions = ['Snapdragon 8 Gen 1', 'Snapdragon 8+ Gen 1', 'Snapdragon 7s Gen 2', 'MediaTek Dimensity 9200', 'MediaTek Dimensity 8300', 'Apple A17 Pro', 'Apple A16 Bionic', 'Google Tensor G3', 'Google Tensor G2', 'Exynos 2400', 'Exynos 2200', 'Other']
const displayTypes = ['AMOLED', 'Super AMOLED', 'OLED', 'LCD', 'IPS LCD', 'LTPO', 'Unknown']
const conditionOptions = ['Like New', 'Good', 'Fair', 'Average', 'Used', 'Refurbished', 'Screen Damage', 'No Box']
const sellerTypes = ['Store', 'Refurbisher', 'Individual']

const SmartphonePrediction = () => {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [predictionResult, setPredictionResult] = useState(null)

  const [imei, setImei] = useState('')
  const [imeiLoading, setImeiLoading] = useState(false)

  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    launch_year: 2022,
    launch_price: '',
    processor: '',
    storage_gb: 256,
    ram_gb: 8,
    battery_percentage: 90,
    battery_health: 90,
    camera_rear_mp: 50,
    camera_front_mp: 16,
    display_type: 'AMOLED',
    display_size_inch: 6.5,
    supports_5g: true,
    condition: 'Good',
    warranty_months: 6,
    screen_cracked: false,
    body_damage: false,
    accessories: 'Charger, Box',
    seller_type: 'Store',
    seller_location: ''
  })

  const [validations, setValidations] = useState({
    brand: { isValid: false, isTouched: false, message: '' },
    model: { isValid: false, isTouched: false, message: '' },
    launch_price: { isValid: false, isTouched: false, message: '' },
    seller_location: { isValid: false, isTouched: false, message: '' },
    imei: { isValid: true, isTouched: false, message: '' } // Initially true as it's optional
  })

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    } else {
      navigate('/login')
    }
  }, [navigate])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }))

    // Real-time validation
    let validation = { isValid: true, message: '' }
    if (name === 'brand') {
      validation = value ? { isValid: true, message: '' } : { isValid: false, message: 'Brand is required' }
    } else if (name === 'model') {
      validation = validateModel(value)
    } else if (name === 'launch_price') {
      validation = validatePrice(value, 5000, 250000)
    } else if (name === 'seller_location') {
      validation = validateLocation(value)
    }

    if (validations[name] !== undefined || name === 'brand') {
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
      return `${baseClass} border-primary-grey/30 focus:border-primary-green`
    }
    if (validation.isValid) {
      return `${baseClass} border-primary-green border-2`
    }
    return `${baseClass} border-primary-red border-2`
  }


  const handleIMEICheck = async () => {
    if (!imei || imei.length < 14) {
      setError('Please enter a valid IMEI number (15 digits)')
      return
    }

    setImeiLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        'http://localhost:8000/api/predictions/imei-lookup/',
        { imei }
      )

      if (response.data.success && response.data.data) {
        const specs = response.data.data
        setFormData(prev => ({
          ...prev,
          ...specs
        }))
        setError(null)
        alert('Device details fetched successfully! Please fill in the condition details.')
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Failed to fetch device details'
      setError(message)
    } finally {
      setImeiLoading(false)
    }
  }

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: checked
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPredictionResult(null)

    const payload = {
      brand: formData.brand,
      model: formData.model,
      launch_year: Number(formData.launch_year),
      launch_price: Number(formData.launch_price),
      processor: formData.processor,
      storage_gb: Number(formData.storage_gb),
      ram_gb: Number(formData.ram_gb),
      battery_percentage: Number(formData.battery_percentage),
      battery_health: Number(formData.battery_health),
      camera_rear_mp: Number(formData.camera_rear_mp),
      camera_front_mp: Number(formData.camera_front_mp),
      display_type: formData.display_type,
      display_size_inch: Number(formData.display_size_inch),
      supports_5g: Boolean(formData.supports_5g),
      condition: formData.condition,
      warranty_months: Number(formData.warranty_months),
      screen_cracked: Boolean(formData.screen_cracked),
      body_damage: Boolean(formData.body_damage),
      accessories: formData.accessories,
      seller_type: formData.seller_type,
      seller_location: formData.seller_location
    }

    try {
      const response = await axios.post(
        'http://localhost:8000/api/predictions/smartphone/',
        payload
      )

      if (response.data.success) {
        setPredictionResult(response.data)
        setTimeout(() => {
          document.getElementById('smartphone-results')?.scrollIntoView({ behavior: 'smooth' })
        }, 100)
      }
    } catch (err) {
      const message = err.response?.data?.message || err.message || 'Prediction failed. Please try again.'
      setError(message)
      console.error('Smartphone prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-black overflow-hidden relative">
      <div className="fixed inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-green via-black to-primary-red" />
      </div>

      <UserNavbar user={user} />

      <main className="relative z-10 px-6 py-16">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <div className="text-6xl mb-4">📱</div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="text-white">Smartphone Price</span>
              <br />
              <span className="text-gradient">Prediction</span>
            </h1>
            <p className="text-xl text-primary-grey max-w-3xl mx-auto">
              Find the accurate resale value of your smartphone using our XGBoost model trained on 80k+ listings.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="glass-effect rounded-xl p-8 mb-8"
          >
            {/* IMEI Lookup Section */}
            <div className="mb-10 p-6 bg-primary-darkGrey/50 rounded-xl border border-primary-grey/20">
              <h2 className="text-2xl font-bold text-white mb-4">Quick Fill with IMEI</h2>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={imei}
                  onChange={(e) => {
                    setImei(e.target.value)
                    const v = validateIMEI(e.target.value)
                    setValidations(prev => ({ ...prev, imei: { ...v, isTouched: true } }))
                  }}
                  onBlur={() => handleBlur('imei')}
                  placeholder="Enter IMEI Number (e.g., 354890...)"
                  className={`flex-1 px-4 py-3 bg-black/40 text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('imei')}`}
                />
                <button
                  type="button"
                  onClick={handleIMEICheck}
                  disabled={imeiLoading || !validations.imei.isValid}
                  className="px-6 py-3 bg-primary-green text-white rounded-lg font-semibold hover:bg-emerald-600 transition-colors disabled:opacity-50"
                >
                  {imeiLoading ? 'Checking...' : 'Check'}
                </button>
              </div>
              {validations.imei.isTouched && !validations.imei.isValid && (
                <p className="text-primary-red text-sm mt-1">{validations.imei.message}</p>
              )}
              <p className="text-sm text-primary-grey mt-2">
                * We will try to fetch your device specs automatically. If not found, please fill the form below.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Device Basics</h2>
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
                      {brandOptions.map((brand) => (
                        <option key={brand} value={brand}>{brand}</option>
                      ))}
                    </select>
                    {validations.brand.isTouched && !validations.brand.isValid && (
                      <p className="text-primary-red text-sm mt-1">{validations.brand.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Model <span className="text-primary-red">*</span>
                    </label>
                    <input
                      type="text"
                      name="model"
                      value={formData.model}
                      onChange={handleInputChange}
                      onBlur={() => handleBlur('model')}
                      placeholder="e.g., Galaxy S23 Ultra"
                      required
                      className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('model')}`}
                    />
                    {validations.model.isTouched && !validations.model.isValid && (
                      <p className="text-primary-red text-sm mt-1">{validations.model.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Launch Year <span className="text-primary-red">*</span>
                    </label>
                    <input
                      type="number"
                      name="launch_year"
                      min="2015"
                      max="2025"
                      value={formData.launch_year}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Original Price (₹) <span className="text-primary-red">*</span>
                    </label>
                    <input
                      type="number"
                      name="launch_price"
                      min="5000"
                      max="250000"
                      value={formData.launch_price}
                      onChange={handleInputChange}
                      onBlur={() => handleBlur('launch_price')}
                      placeholder="e.g., 79999"
                      required
                      className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('launch_price')}`}
                    />
                    {validations.launch_price.isTouched && !validations.launch_price.isValid && (
                      <p className="text-primary-red text-sm mt-1">{validations.launch_price.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Processor <span className="text-primary-red">*</span>
                    </label>
                    <select
                      name="processor"
                      value={formData.processor}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    >
                      <option value="">Select Processor</option>
                      {processorOptions.map((item) => (
                        <option key={item} value={item}>{item}</option>
                      ))}
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Display Type
                    </label>
                    <select
                      name="display_type"
                      value={formData.display_type}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    >
                      {displayTypes.map((display) => (
                        <option key={display} value={display}>{display}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Hardware Specs</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[
                    { label: 'Storage (GB)', name: 'storage_gb', min: 32, max: 2048 },
                    { label: 'RAM (GB)', name: 'ram_gb', min: 2, max: 24 },
                    { label: 'Display Size (in)', name: 'display_size_inch', min: 4.5, max: 8.5, step: 0.01 }
                  ].map((field) => (
                    <div key={field.name}>
                      <label className="block text-white font-semibold mb-2">
                        {field.label} <span className="text-primary-red">*</span>
                      </label>
                      <input
                        type="number"
                        name={field.name}
                        min={field.min}
                        max={field.max}
                        step={field.step || 1}
                        value={formData[field.name]}
                        onChange={handleInputChange}
                        required
                        className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                      />
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  {[
                    { label: 'Rear Camera (MP)', name: 'camera_rear_mp', min: 5, max: 200 },
                    { label: 'Front Camera (MP)', name: 'camera_front_mp', min: 2, max: 64 },
                    { label: 'Battery %', name: 'battery_percentage', min: 40, max: 100 },
                    { label: 'Battery Health %', name: 'battery_health', min: 40, max: 100 },
                  ].map((field) => (
                    <div key={field.name}>
                      <label className="block text-white font-semibold mb-2">
                        {field.label} <span className="text-primary-red">*</span>
                      </label>
                      <input
                        type="number"
                        name={field.name}
                        min={field.min}
                        max={field.max}
                        value={formData[field.name]}
                        onChange={handleInputChange}
                        required
                        className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                      />
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                  <label className="flex items-center gap-3 text-white font-semibold">
                    <input
                      type="checkbox"
                      name="supports_5g"
                      checked={formData.supports_5g}
                      onChange={handleCheckboxChange}
                      className="h-5 w-5 accent-primary-green"
                    />
                    Supports 5G
                  </label>
                  <label className="flex items-center gap-3 text-white font-semibold">
                    <input
                      type="checkbox"
                      name="screen_cracked"
                      checked={formData.screen_cracked}
                      onChange={handleCheckboxChange}
                      className="h-5 w-5 accent-primary-red"
                    />
                    Screen Damage
                  </label>
                  <label className="flex items-center gap-3 text-white font-semibold">
                    <input
                      type="checkbox"
                      name="body_damage"
                      checked={formData.body_damage}
                      onChange={handleCheckboxChange}
                      className="h-5 w-5 accent-primary-red"
                    />
                    Body Damage
                  </label>
                </div>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Condition & Seller Info</h2>
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
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    >
                      {conditionOptions.map((condition) => (
                        <option key={condition} value={condition}>{condition}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Warranty Remaining (months)
                    </label>
                    <input
                      type="number"
                      name="warranty_months"
                      min="0"
                      max="36"
                      value={formData.warranty_months}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Seller Type <span className="text-primary-red">*</span>
                    </label>
                    <select
                      name="seller_type"
                      value={formData.seller_type}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    >
                      {sellerTypes.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-white font-semibold mb-2">
                      Location <span className="text-primary-red">*</span>
                    </label>
                    <input
                      type="text"
                      name="seller_location"
                      value={formData.seller_location}
                      onChange={handleInputChange}
                      onBlur={() => handleBlur('seller_location')}
                      placeholder="City / Region"
                      required
                      className={`w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors ${getFieldClassName('seller_location')}`}
                    />
                    {validations.seller_location.isTouched && !validations.seller_location.isValid && (
                      <p className="text-primary-red text-sm mt-1">{validations.seller_location.message}</p>
                    )}
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-white font-semibold mb-2">
                      Accessories Included
                    </label>
                    <input
                      type="text"
                      name="accessories"
                      value={formData.accessories}
                      onChange={handleInputChange}
                      placeholder="e.g., Charger, Box, Earphones"
                      className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                    />
                  </div>
                </div>
              </section>

              {error && (
                <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <motion.button
                type="submit"
                disabled={loading || !validations.brand.isValid || !validations.model.isValid || !validations.launch_price.isValid || !validations.seller_location.isValid}
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
                className="w-full py-4 bg-gradient-to-r from-primary-green to-emerald-600 text-white rounded-lg font-semibold text-lg transition-all duration-300 shadow-lg shadow-primary-green/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Predicting...' : '🔮 Get Smartphone Price Prediction'}
              </motion.button>
            </form>
          </motion.div>

          {predictionResult && (
            <motion.div
              id="smartphone-results"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="glass-effect rounded-xl p-8 mb-8"
            >
              <div className="text-center mb-8">
                <div className="text-5xl mb-4">🎯</div>
                <h2 className="text-4xl font-bold text-white mb-2">Prediction Complete</h2>
                <p className="text-primary-grey">Here's the estimated resale price for your smartphone</p>
              </div>

              <div className="bg-gradient-to-r from-primary-green to-emerald-600 rounded-xl p-8 mb-8 text-center">
                <div className="text-primary-grey text-sm mb-2">Estimated Resale Price</div>
                <div className="text-5xl md:text-6xl font-bold text-white mb-2">
                  ₹{predictionResult.prediction.predicted_price.toLocaleString()}
                </div>
                <div className="text-white/80">
                  Range: ₹{predictionResult.prediction.price_range.min.toLocaleString()} - ₹{predictionResult.prediction.price_range.max.toLocaleString()}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-primary-darkGrey rounded-lg p-6 text-center">
                  <div className="text-3xl mb-2">🎯</div>
                  <div className="text-2xl font-bold text-primary-green mb-1">
                    {predictionResult.prediction.confidence_score}%
                  </div>
                  <div className="text-primary-grey text-sm">Confidence Score</div>
                </div>
                <div className="bg-primary-darkGrey rounded-lg p-6 text-center">
                  <div className="text-3xl mb-2">📈</div>
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

              <div className="bg-primary-darkGrey rounded-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4">Device Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-primary-grey">Brand / Model:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.brand} {predictionResult.data.model}</span>
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
                    <span className="text-primary-grey">Memory:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.storage} GB / {predictionResult.data.ram} GB</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Display:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.screen_size}" {predictionResult.data.display_type || ''}</span>
                  </div>
                  <div>
                    <span className="text-primary-grey">Condition:</span>
                    <span className="text-white ml-2 font-semibold">{predictionResult.data.condition}</span>
                  </div>
                </div>
              </div>

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
                  Explore Resale Options
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
                      deviceType: 'smartphone'
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

      <footer className="relative z-10 border-t border-primary-grey/30 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-primary-grey">
          <p>&copy; 2024 DealGoat. AI-powered predictions for every device.</p>
        </div>
      </footer>
    </div>
  )
}

export default SmartphonePrediction

