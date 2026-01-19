import { useState } from 'react'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'

export default function SmartProductFinder() {
  const [requirements, setRequirements] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [showDetailedRequirements, setShowDetailedRequirements] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!requirements.trim()) return

    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        'http://localhost:8000/api/recommendations/find-products/',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Token ${token}` } : {})
          },
          body: JSON.stringify({ requirements })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Failed to find products')
      }

      setResults(data.query)
      setRequirements('')
      fetchHistory()
    } catch (err) {
      setError(err.message || 'Error finding products. Please try again or check your internet connection.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        'http://localhost:8000/api/recommendations/query-history/',
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Token ${token}` } : {})
          }
        }
      )
      const data = await response.json()
      if (response.ok) {
        setHistory(data.queries)
      }
    } catch (err) {
      console.error('Error fetching history:', err)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      <UserNavbar />

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-5xl font-bold mb-4">
            <span className="text-gradient">🧠 Smart Intent-Driven Buying Assistant</span>
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            Describe your problem, not just specs. Our AI understands your intent and finds products that match your real needs.
          </p>
          <p className="text-sm text-gray-500">
            ✨ No filters, no forms. Just tell us what you need, and we'll explain why each product matches.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            <form onSubmit={handleSubmit} className="mb-8">
              <div className="bg-gray-900 rounded-lg border border-red-600/30 p-8">
                <label className="block text-white font-bold mb-4">
                  📝 Describe Your Requirements
                </label>
                <textarea
                  value={requirements}
                  onChange={(e) => setRequirements(e.target.value)}
                  placeholder="Example: I'm an MCA student, budget 80k, I do coding, ML, light gaming, want future-proof laptop, good battery, not too heavy..."
                  className="w-full bg-gray-800 text-white p-4 rounded border border-gray-700 h-40 mb-4 focus:border-red-600 focus:outline-none resize-none"
                />
                <p className="text-gray-400 text-sm mb-6">
                  💡 Tip: Describe your situation and needs naturally. Include your role (student/professional), use cases, budget, and priorities. Our AI will understand trade-offs and explain why each product matches.
                </p>
                <button
                  type="submit"
                  disabled={loading || !requirements.trim()}
                  className="w-full bg-gradient-to-r from-red-600 to-red-700 text-white px-8 py-3 rounded-lg font-bold hover:from-red-700 hover:to-red-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="animate-spin">⏳</span>
                      Finding Products...
                    </span>
                  ) : (
                    'Find Best Products'
                  )}
                </button>
              </div>
            </form>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-red-900/20 text-red-300 p-4 rounded-lg border border-red-600/30 mb-8"
              >
                ❌ {error}
              </motion.div>
            )}

            {/* Results */}
            {results && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* SIDBA Persona & Trade-offs */}
                {results.parsed_requirements.persona && (
                  <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-6 mb-4">
                    <h3 className="text-blue-400 font-bold mb-3 text-lg">🧠 AI Analysis:</h3>
                    <div className="mb-3">
                      <span className="text-blue-300 font-semibold text-sm">
                        {results.parsed_requirements.persona.description || 'General User'}
                      </span>
                    </div>
                    {results.parsed_requirements.tradeoff_explanation && (
                      <div className="bg-yellow-900/20 border border-yellow-600/30 rounded p-3 mt-3">
                        <p className="text-yellow-300 text-sm">
                          ⚠️ <strong>Trade-off Detected:</strong> {results.parsed_requirements.tradeoff_explanation}
                        </p>
                      </div>
                    )}
                    {results.parsed_requirements.conflicts && results.parsed_requirements.conflicts.length > 0 && (
                      <div className="bg-orange-900/20 border border-orange-600/30 rounded p-3 mt-3">
                        <p className="text-orange-300 text-sm">
                          💡 <strong>Note:</strong> Some requirements may conflict. We've balanced priorities to find the best matches.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Requirements Summary */}
                <div className="bg-green-900/20 border border-green-600/30 rounded-lg p-6">
                  <h3 className="text-green-400 font-bold mb-4 text-lg">✅ Your Requirements Understood:</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 text-sm">
                    {/* Device Type */}
                    {results.parsed_requirements.device_type && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Device</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.device_type.charAt(0).toUpperCase() + results.parsed_requirements.device_type.slice(1)}</span>
                      </div>
                    )}

                    {/* Budget */}
                    {results.parsed_requirements.budget_max && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Budget</span>
                        <span className="text-green-300 font-semibold">₹{results.parsed_requirements.budget_max.toLocaleString()}</span>
                      </div>
                    )}

                    {/* Processor */}
                    {results.parsed_requirements.processor_min && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Processor</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.processor_min}</span>
                      </div>
                    )}

                    {/* RAM */}
                    {results.parsed_requirements.ram_needed_gb && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">RAM</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.ram_needed_gb}GB</span>
                      </div>
                    )}

                    {/* Storage */}
                    {results.parsed_requirements.storage_needed_gb && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Storage</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.storage_needed_gb}GB SSD</span>
                      </div>
                    )}

                    {/* Screen Size */}
                    {(results.parsed_requirements.screen_size_min || results.parsed_requirements.screen_size_max) && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Screen Size</span>
                        <span className="text-green-300 font-semibold">
                          {results.parsed_requirements.screen_size_min || results.parsed_requirements.screen_size_max}
                          {results.parsed_requirements.screen_size_min && results.parsed_requirements.screen_size_max &&
                            `-${results.parsed_requirements.screen_size_max}`
                          }
                          "
                        </span>
                      </div>
                    )}

                    {/* OS */}
                    {results.parsed_requirements.os_required && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">OS</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.os_required}</span>
                      </div>
                    )}

                    {/* Performance Tier */}
                    {results.parsed_requirements.performance_tier && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Tier</span>
                        <span className="text-green-300 font-semibold capitalize">{results.parsed_requirements.performance_tier}</span>
                      </div>
                    )}

                    {/* Battery */}
                    {results.parsed_requirements.battery_hours && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Battery</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.battery_hours}h+</span>
                      </div>
                    )}

                    {/* GPU */}
                    {results.parsed_requirements.gpu_required && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">GPU</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.gpu_required}</span>
                      </div>
                    )}

                    {/* Use Cases */}
                    {results.parsed_requirements.use_case && results.parsed_requirements.use_case.length > 0 && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20 md:col-span-2">
                        <span className="text-gray-400 text-xs block">Use Cases</span>
                        <span className="text-green-300 font-semibold">{results.parsed_requirements.use_case.join(', ')}</span>
                      </div>
                    )}

                    {/* Priority */}
                    {results.parsed_requirements.priority && (
                      <div className="bg-gray-800/50 p-3 rounded border border-green-600/20">
                        <span className="text-gray-400 text-xs block">Priority</span>
                        <span className="text-green-300 font-semibold capitalize">{results.parsed_requirements.priority}</span>
                      </div>
                    )}
                  </div>

                  {/* Must-Have Features */}
                  {results.parsed_requirements.must_have_features && results.parsed_requirements.must_have_features.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-green-600/30">
                      <p className="text-gray-300 font-semibold text-sm mb-2">🎯 Must-Have Features:</p>
                      <div className="flex flex-wrap gap-2">
                        {results.parsed_requirements.must_have_features.map((feature, i) => (
                          <span key={i} className="bg-green-600/20 text-green-300 px-3 py-1 rounded text-xs font-medium border border-green-600/50">
                            ✓ {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Products */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-green-500">🏆 Top Recommendations</h2>
                    <button
                      onClick={() => setShowDetailedRequirements(!showDetailedRequirements)}
                      className="flex items-center gap-2 bg-green-600/20 hover:bg-green-600/30 text-green-400 px-4 py-2 rounded border border-green-600/50 transition-all"
                      title="View all tracked parameters"
                    >
                      {showDetailedRequirements ? (
                        <>
                          <span className="text-xl">👁️</span>
                          <span className="text-sm font-semibold">Hide Details</span>
                        </>
                      ) : (
                        <>
                          <span className="text-xl">👁️</span>
                          <span className="text-sm font-semibold">View All</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Detailed Requirements - Expandable */}
                  {showDetailedRequirements && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="bg-gray-800/50 border border-green-600/30 rounded-lg p-6 mb-6"
                    >
                      <h3 className="text-lg font-bold text-green-400 mb-4">📊 All Tracked Parameters</h3>

                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 text-sm">
                        {/* Device Type */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Device Type</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.device_type?.charAt(0).toUpperCase() + results.parsed_requirements.device_type?.slice(1) || 'N/A'}</span>
                        </div>

                        {/* Budget Min */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Budget Min</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.budget_min ? `₹${results.parsed_requirements.budget_min.toLocaleString()}` : 'Not Set'}</span>
                        </div>

                        {/* Budget Max */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Budget Max</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.budget_max ? `₹${results.parsed_requirements.budget_max.toLocaleString()}` : 'N/A'}</span>
                        </div>

                        {/* Processor Min */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Processor Min</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.processor_min || 'Not Set'}</span>
                        </div>

                        {/* RAM Needed */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">RAM Needed</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.ram_needed_gb ? `${results.parsed_requirements.ram_needed_gb}GB` : 'Not Set'}</span>
                        </div>

                        {/* Storage Needed */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Storage Needed</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.storage_needed_gb ? `${results.parsed_requirements.storage_needed_gb}GB` : 'Not Set'}</span>
                        </div>

                        {/* Screen Size Min */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Screen Min</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.screen_size_min ? `${results.parsed_requirements.screen_size_min}"` : 'Not Set'}</span>
                        </div>

                        {/* Screen Size Max */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Screen Max</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.screen_size_max ? `${results.parsed_requirements.screen_size_max}"` : 'Not Set'}</span>
                        </div>

                        {/* OS Required */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">OS Required</span>
                          <span className="text-blue-300 font-semibold">{results.parsed_requirements.os_required || 'Not Set'}</span>
                        </div>

                        {/* Performance Tier */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Performance Tier</span>
                          <span className="text-blue-300 font-semibold capitalize">{results.parsed_requirements.performance_tier || 'N/A'}</span>
                        </div>

                        {/* Priority */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Priority</span>
                          <span className="text-blue-300 font-semibold capitalize">{results.parsed_requirements.priority || 'N/A'}</span>
                        </div>

                        {/* Use Cases */}
                        <div className="bg-gray-700/50 p-3 rounded border border-blue-600/30">
                          <span className="text-gray-400 text-xs block">Use Cases</span>
                          <span className="text-blue-300 font-semibold text-xs">{results.parsed_requirements.use_case?.join(', ') || 'Not Set'}</span>
                        </div>
                      </div>

                      {/* Nice-to-Have Features */}
                      {results.parsed_requirements.nice_to_have && results.parsed_requirements.nice_to_have.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-blue-600/30">
                          <p className="text-gray-300 font-semibold text-sm mb-2">💎 Nice-to-Have:</p>
                          <div className="flex flex-wrap gap-2">
                            {results.parsed_requirements.nice_to_have.map((feature, i) => (
                              <span key={i} className="bg-blue-600/20 text-blue-300 px-3 py-1 rounded text-xs font-medium border border-blue-600/50">
                                ◇ {feature}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}

                  <div className="space-y-4">
                    {results.products && results.products.length > 0 ? (
                      results.products.map((product, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-green-600/50 transition-all"
                        >
                          <div className="flex items-start gap-4">
                            {/* Rank Badge */}
                            <div className="flex-shrink-0">
                              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white ${i === 0 ? 'bg-yellow-600' :
                                i === 1 ? 'bg-gray-600' :
                                  i === 2 ? 'bg-orange-600' :
                                    'bg-gray-700'
                                }`}>
                                #{i + 1}
                              </div>
                            </div>

                            {/* Product Info */}
                            <div className="flex-1">
                              <div className="flex justify-between items-start mb-3">
                                <div>
                                  <h3 className="text-lg font-bold text-white">{product.product_name}</h3>
                                  <p className="text-gray-400 text-sm">{product.brand}</p>
                                </div>
                                <div className="text-right">
                                  <div className="flex flex-col items-end gap-1">
                                    {/* Discount Badge - Extract from match_reasons.metadata */}
                                    {(() => {
                                      // Try to get discount info from various locations
                                      let discountInfo = null;
                                      if (product.discount_info) {
                                        discountInfo = product.discount_info;
                                      } else if (product.match_reasons && typeof product.match_reasons === 'object') {
                                        if (product.match_reasons.metadata && product.match_reasons.metadata.discount_info) {
                                          discountInfo = product.match_reasons.metadata.discount_info;
                                        }
                                      }

                                      return discountInfo && discountInfo.is_discount ? (
                                        <div className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                                          🔥 {discountInfo.discount_percent}% OFF
                                        </div>
                                      ) : null;
                                    })()}
                                    {/* Price */}
                                    <div className="flex items-center gap-2">
                                      {(() => {
                                        let discountInfo = null;
                                        if (product.discount_info) {
                                          discountInfo = product.discount_info;
                                        } else if (product.match_reasons && typeof product.match_reasons === 'object') {
                                          if (product.match_reasons.metadata && product.match_reasons.metadata.discount_info) {
                                            discountInfo = product.match_reasons.metadata.discount_info;
                                          }
                                        }

                                        return discountInfo && discountInfo.is_discount ? (
                                          <span className="text-gray-500 line-through text-sm">
                                            ₹{(discountInfo.original_price || product.price).toLocaleString()}
                                          </span>
                                        ) : null;
                                      })()}
                                      <div className="text-2xl font-bold text-red-600">
                                        ₹{product.price.toLocaleString()}
                                      </div>
                                    </div>
                                    {(() => {
                                      let discountInfo = null;
                                      if (product.discount_info) {
                                        discountInfo = product.discount_info;
                                      } else if (product.match_reasons && typeof product.match_reasons === 'object') {
                                        if (product.match_reasons.metadata && product.match_reasons.metadata.discount_info) {
                                          discountInfo = product.match_reasons.metadata.discount_info;
                                        }
                                      }

                                      return discountInfo && discountInfo.is_discount ? (
                                        <div className="text-green-400 text-xs">
                                          Save ₹{(discountInfo.savings || 0).toLocaleString()}
                                        </div>
                                      ) : null;
                                    })()}
                                    {product.rating > 0 && (
                                      <div className="text-yellow-400">⭐ {product.rating}/5</div>
                                    )}
                                    {(() => {
                                      let priceUpdated = null;
                                      if (product.price_updated_at) {
                                        priceUpdated = product.price_updated_at;
                                      } else if (product.match_reasons && typeof product.match_reasons === 'object') {
                                        if (product.match_reasons.metadata && product.match_reasons.metadata.price_updated_at) {
                                          priceUpdated = product.match_reasons.metadata.price_updated_at;
                                        }
                                      }

                                      return priceUpdated ? (
                                        <div className="text-gray-500 text-xs">
                                          Price updated: {new Date(priceUpdated).toLocaleDateString()}
                                        </div>
                                      ) : null;
                                    })()}
                                  </div>
                                </div>
                              </div>

                              {/* Match Score */}
                              <div className="mb-3">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-green-400 font-semibold">Match Score</span>
                                  <span className="text-green-500 font-bold">{Math.round(product.match_score)}%</span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-2">
                                  <div
                                    className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full"
                                    style={{ width: `${product.match_score}%` }}
                                  />
                                </div>
                              </div>

                              {/* SIDBA Explanations */}
                              {product.sidba_explanations && (
                                <div className="mb-4 space-y-3">
                                  {/* Why This Product */}
                                  {product.sidba_explanations.why_this_product && product.sidba_explanations.why_this_product.length > 0 && (
                                    <div>
                                      <p className="text-gray-300 font-semibold text-sm mb-2">💡 Why this product:</p>
                                      <ul className="space-y-1">
                                        {product.sidba_explanations.why_this_product.slice(0, 3).map((reason, j) => (
                                          <li key={j} className="text-green-400 text-sm">✅ {reason}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}

                                  {/* Best For */}
                                  {product.sidba_explanations.best_for && product.sidba_explanations.best_for.length > 0 && (
                                    <div>
                                      <p className="text-gray-300 font-semibold text-sm mb-1">🎯 Best for:</p>
                                      <div className="flex flex-wrap gap-2">
                                        {product.sidba_explanations.best_for.map((use, j) => (
                                          <span key={j} className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded text-xs border border-blue-600/50">
                                            {use}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* Trade-offs */}
                                  {product.sidba_explanations.trade_offs && product.sidba_explanations.trade_offs.length > 0 && (
                                    <div>
                                      <p className="text-yellow-300 font-semibold text-sm mb-1">⚖️ Trade-off:</p>
                                      <p className="text-yellow-400 text-xs">{product.sidba_explanations.trade_offs[0]}</p>
                                    </div>
                                  )}

                                  {/* Compromises */}
                                  {product.sidba_explanations.compromises && product.sidba_explanations.compromises.length > 0 && (
                                    <div>
                                      <p className="text-orange-300 font-semibold text-sm mb-1">⚠️ Compromise:</p>
                                      <p className="text-orange-400 text-xs">{product.sidba_explanations.compromises[0]}</p>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Fallback to match_reasons if SIDBA explanations not available */}
                              {(!product.sidba_explanations && product.match_reasons && product.match_reasons.length > 0) && (
                                <div className="mb-4">
                                  <p className="text-gray-300 font-semibold text-sm mb-2">Why this matches:</p>
                                  <ul className="space-y-1">
                                    {product.match_reasons.slice(0, 3).map((reason, j) => (
                                      <li key={j} className="text-green-400 text-sm">✅ {reason}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Product Summary */}
                              {product.summary && (
                                <div className="mb-4 bg-gray-800/50 p-3 rounded border border-purple-600/30">
                                  <p className="text-purple-300 text-sm font-medium">{product.summary}</p>
                                </div>
                              )}

                              {/* Links */}
                              <div className="flex gap-3 flex-wrap">
                                {product.amazon_link && (
                                  <a
                                    href={product.amazon_link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded font-semibold transition-all transform hover:scale-105"
                                  >
                                    🛒 Buy on Amazon
                                  </a>
                                )}
                                {product.flipkart_link && (
                                  <a
                                    href={product.flipkart_link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold transition-all transform hover:scale-105"
                                  >
                                    🛍️ Buy on Flipkart
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))
                    ) : (
                      <p className="text-gray-400">No products found.</p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Right Column - History */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="bg-gray-900 rounded-lg border border-gray-700 p-6 sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">📋 Search History</h3>
                <button
                  onClick={fetchHistory}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  🔄
                </button>
              </div>

              {history && history.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {history.slice(0, 10).map((query, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      onClick={() => setResults(query)}
                      className="bg-gray-800 p-3 rounded cursor-pointer hover:bg-gray-700 hover:border-l-2 hover:border-red-600 transition-all"
                    >
                      <p className="text-gray-300 text-sm truncate">
                        {query.requirements_text.substring(0, 50)}...
                      </p>
                      <p className="text-gray-500 text-xs mt-1">
                        {query.products?.length || 0} products found
                      </p>
                      <p className="text-gray-600 text-xs mt-1">
                        {new Date(query.created_at).toLocaleDateString()}
                      </p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm text-center py-8">
                  No search history yet. Start searching!
                </p>
              )}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
