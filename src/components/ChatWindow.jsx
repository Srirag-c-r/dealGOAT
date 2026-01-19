import { useState, useEffect, useRef } from 'react'
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion'
import api from '../services/api'
import websocket from '../services/websocket'

const LocationCard = ({ content, isMine, createdAt }) => {
    const [isExpanded, setIsExpanded] = useState(false)

    const mapUrl = content.match(/https:\/\/\S+/)?.[0]
    const title = content.split('https')[0].replace('📍', '').trim() || "Meetup Point"

    return (
        <motion.div
            layout
            onHoverStart={() => setIsExpanded(true)}
            onHoverEnd={() => setIsExpanded(false)}
            onClick={() => setIsExpanded(!isExpanded)}
            className={`relative cursor-pointer overflow-hidden transition-all duration-300 ${isExpanded
                    ? 'w-72 sm:w-80 rounded-2xl bg-black/40 border-white/20'
                    : 'w-48 rounded-full bg-white/10 border-white/10 hover:bg-white/20'
                } border backdrop-blur-md m-2 shadow-xl`}
        >
            <motion.div layout className="p-3 flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isExpanded ? 'bg-primary-green' : 'bg-primary-green/20'
                    } transition-colors`}>
                    <span className="text-lg">📍</span>
                </div>

                <div className="flex-1 min-w-0">
                    <motion.h4 layout className={`text-white font-bold truncate ${isExpanded ? 'text-sm' : 'text-xs'}`}>
                        {title}
                    </motion.h4>
                    {!isExpanded && (
                        <p className="text-[10px] text-primary-grey truncate">Click to view map</p>
                    )}
                </div>

                {isExpanded && (
                    <motion.button
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-primary-grey hover:text-white"
                    >
                        ✕
                    </motion.button>
                )}
            </motion.div>

            {isExpanded && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                >
                    <div className="px-3 pb-3">
                        <div className="relative group/map w-full h-32 rounded-xl bg-gradient-to-br from-primary-green/10 to-blue-900/20 border border-white/5 overflow-hidden">
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-3xl opacity-50">🗺️</span>
                                <div className="absolute inset-0 bg-black/20 group-hover/map:bg-transparent transition-colors" />
                            </div>
                            <div className="absolute top-2 right-2 px-2 py-1 rounded bg-black/60 text-[8px] text-white/70 font-mono">
                                PREVIEW_MODE
                            </div>
                        </div>

                        <div className="mt-3 flex items-center justify-between gap-4">
                            <div className="flex-1">
                                <p className="text-[10px] text-white/50 line-clamp-1 leading-tight mb-1">
                                    {content.split('\n')[1] || "Shared Location"}
                                </p>
                                <span className="text-[10px] text-primary-green font-bold">Verified Spot</span>
                            </div>
                            <a
                                href={mapUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-4 py-2 bg-primary-green text-white text-xs font-bold rounded-lg hover:shadow-[0_0_15px_rgba(34,197,94,0.4)] transition-all flex items-center gap-2 whitespace-nowrap"
                            >
                                Navigate ↗
                            </a>
                        </div>
                    </div>
                </motion.div>
            )}

            <div className={`px-3 pb-1 flex justify-end opacity-40 ${isExpanded ? 'mt-1' : '-mt-1'}`}>
                <span className="text-[8px] text-white font-mono">
                    {new Date(createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>
        </motion.div>
    )
}

const ChatWindow = ({ conversation, currentUser, onClose }) => {
    const [messages, setMessages] = useState([])
    const [newMessage, setNewMessage] = useState('')
    const [loading, setLoading] = useState(true)
    const [suggestion, setSuggestion] = useState(null)
    const [isSearchingLocation, setIsSearchingLocation] = useState(false)
    const [locationQuery, setLocationQuery] = useState('')
    const [locationResults, setLocationResults] = useState([])
    const [isSearching, setIsSearching] = useState(false)
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    useEffect(() => {
        if (conversation) {
            loadMessages()
            connectWebSocket()
            markAsRead()
        }

        return () => {
            websocket.disconnect()
        }
    }, [conversation?.id])

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const loadMessages = async () => {
        try {
            const response = await api.getConversationMessages(conversation.id)
            if (response.success) {
                const loadedMessages = response.data
                setMessages(loadedMessages)

                // Check last message for smart suggestions
                const isSeller = currentUser.id === conversation.seller
                if (isSeller && loadedMessages.length > 0) {
                    const lastMsg = loadedMessages[loadedMessages.length - 1]
                    detectIntent(lastMsg)
                }
            }
            setLoading(false)
        } catch (error) {
            console.error('Failed to load messages:', error)
            setLoading(false)
        }
    }

    const detectIntent = (message) => {
        const isFromBuyer = message.sender_email !== currentUser.email
        if (!isFromBuyer) return

        const content = message.content.toLowerCase()
        const locationKeywords = ['location', 'place', 'where', 'meet', 'address', 'city', 'pincode', 'area', 'map']
        const contactKeywords = ['phone', 'number', 'call', 'whatsapp', 'contact', 'mobile']

        if (locationKeywords.some(k => content.includes(k))) {
            setSuggestion({ type: 'location' })
        } else if (contactKeywords.some(k => content.includes(k))) {
            setSuggestion({ type: 'contact' })
        }
    }

    const connectWebSocket = () => {
        websocket.connect(conversation.id, (message) => {
            setMessages(prev => [...prev, message])

            // Smart Suggestion NLP Detection
            const isSeller = currentUser.id === conversation.seller
            if (isSeller) {
                detectIntent(message)
            }
        })
    }

    const markAsRead = async () => {
        try {
            await api.markMessagesRead(conversation.id)
        } catch (error) {
            console.error('Failed to mark as read:', error)
        }
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const handleSend = () => {
        if (!newMessage.trim()) return

        const success = websocket.sendMessage(newMessage)
        if (success) {
            setNewMessage('')
            inputRef.current?.focus()
            // Hide suggestion when seller sends any message
            setSuggestion(null)
        }
    }

    const handleShareContact = () => {
        const phone = currentUser.phone || 'not provided'
        const message = `Sure! You can reach me at ${phone}`
        const success = websocket.sendMessage(message)
        if (success) {
            setSuggestion(null)
        }
    }

    const handleShareLocation = (type) => {
        if (type === 'search') {
            setIsSearchingLocation(true)
            return
        }

        let message = ""
        if (type === 'city') {
            const city = conversation.listing_city || "our city"
            const pin = conversation.listing_pincode || ""
            message = `I'm located in ${city}${pin ? `, ${pin}` : ''}. We can meet near here.`
        } else if (type === 'gps') {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    const { latitude, longitude } = position.coords
                    const mapUrl = `https://www.google.com/maps?q=${latitude},${longitude}`
                    websocket.sendMessage(`📍 My precise meetup location: ${mapUrl}`)
                    setSuggestion(null)
                }, (error) => {
                    console.error("GPS Error:", error)
                    alert("Could not get your location. Please check your browser permissions.")
                })
                return // sendMessage happens in callback
            } else {
                alert("Geolocation is not supported by your browser.")
                return
            }
        }

        const success = websocket.sendMessage(message)
        if (success) {
            setSuggestion(null)
        }
    }

    const searchLocations = async (query) => {
        if (!query.trim()) return
        setIsSearching(true)
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`)
            const data = await response.json()
            setLocationResults(data)
        } catch (error) {
            console.error("Search error:", error)
        } finally {
            setIsSearching(false)
        }
    }

    const selectLocation = (loc) => {
        const mapUrl = `https://www.google.com/maps?q=${loc.lat},${loc.lon}`
        websocket.sendMessage(`📍 Meetup Spot: ${loc.display_name.split(',')[0]}\n${loc.display_name}\n${mapUrl}`)
        setIsSearchingLocation(false)
        setLocationQuery('')
        setLocationResults([])
        setSuggestion(null)
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const otherUser = conversation.buyer === currentUser.id ? conversation.seller_name : conversation.buyer_name

    return (
        <div className="glass-effect rounded-xl h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-primary-grey/30 flex justify-between items-center bg-white/5">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full overflow-hidden bg-primary-grey/20 border border-primary-grey/30 flex-shrink-0">
                        {((conversation.buyer === currentUser.id ? conversation.seller_profile_picture : conversation.buyer_profile_picture)) ? (
                            <img
                                src={(conversation.buyer === currentUser.id ? conversation.seller_profile_picture : conversation.buyer_profile_picture).startsWith('http')
                                    ? (conversation.buyer === currentUser.id ? conversation.seller_profile_picture : conversation.buyer_profile_picture)
                                    : `http://localhost:8000${(conversation.buyer === currentUser.id ? conversation.seller_profile_picture : conversation.buyer_profile_picture)}`}
                                alt="Avatar"
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-lg text-white font-bold bg-gradient-to-br from-primary-red to-red-900">
                                {otherUser[0].toUpperCase()}
                            </div>
                        )}
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">{otherUser}</h2>
                        <div className="flex items-center gap-2">
                            <img
                                src={conversation.listing_type === 'laptop' || (conversation.listing_title && conversation.listing_title.toLowerCase().includes('laptop')) ? '/laptopicon.png' : '/mobileicon.png'}
                                alt="icon"
                                className="w-4 h-4 object-contain opacity-70"
                            />
                            <p className="text-xs text-primary-grey">{conversation.listing_title}</p>
                        </div>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="lg:hidden text-primary-grey hover:text-white transition-colors"
                >
                    ✕
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {loading ? (
                    <div className="text-center text-primary-grey">Loading messages...</div>
                ) : messages.length === 0 ? (
                    <div className="text-center text-primary-grey py-8">
                        <div className="text-4xl mb-2">👋</div>
                        <p>No messages yet. Start the conversation!</p>
                    </div>
                ) : (
                    messages.map((message, index) => {
                        // Check if message is from current user by comparing emails
                        const isMine = message.sender === currentUser.email || message.sender_email === currentUser.email
                        return (
                            <motion.div
                                key={message.id || index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex items-end gap-2 ${isMine ? 'flex-row-reverse' : 'flex-row'}`}
                            >
                                {/* Message Avatar */}
                                <div className="w-8 h-8 rounded-full overflow-hidden bg-primary-grey/20 flex-shrink-0 mb-1 border border-primary-grey/30">
                                    {isMine ? (
                                        currentUser.profile_picture ? (
                                            <img
                                                src={currentUser.profile_picture.startsWith('http') ? currentUser.profile_picture : `http://localhost:8000${currentUser.profile_picture}`}
                                                alt="Me"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-[10px] text-white bg-primary-green">ME</div>
                                        )
                                    ) : (
                                        message.sender_profile_picture ? (
                                            <img
                                                src={message.sender_profile_picture.startsWith('http') ? message.sender_profile_picture : `http://localhost:8000${message.sender_profile_picture}`}
                                                alt="Sender"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-[10px] text-white bg-red-800">
                                                {message.sender_name?.[0]?.toUpperCase() || 'U'}
                                            </div>
                                        )
                                    )}
                                </div>

                                <div
                                    className={`max-w-[80%] rounded-2xl p-0 overflow-hidden ${isMine
                                        ? 'bg-primary-green text-white rounded-br-none'
                                        : 'bg-white/10 text-white rounded-bl-none'
                                        }`}
                                >
                                    {message.content.includes('google.com/maps') ? (
                                        <LocationCard
                                            content={message.content}
                                            isMine={isMine}
                                            createdAt={message.created_at}
                                        />
                                    ) : (
                                        <div className="p-3">
                                            <p className="text-sm break-words">{message.content}</p>
                                            <p className={`text-[10px] mt-1 text-right ${isMine ? 'text-white/70' : 'text-primary-grey/70'}`}>
                                                {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )
                    })
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Smart Suggestion Banner */}
            {suggestion && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mx-4 mb-2 p-3 bg-primary-green/20 border border-primary-green/30 rounded-lg flex flex-col sm:flex-row items-center justify-between gap-4"
                >
                    <div className="flex items-center gap-2">
                        <span className="text-xl animate-pulse">
                            {suggestion.type === 'location' ? '📍' : '💡'}
                        </span>
                        <p className="text-sm text-white">
                            {suggestion.type === 'location'
                                ? 'Buyer is asking about meetup location. Share yours?'
                                : 'Buyer is asking for contact. Share your phone number?'
                            }
                        </p>
                    </div>
                    <div className="flex gap-2 w-full sm:w-auto">
                        <button
                            onClick={() => setSuggestion(null)}
                            className="flex-1 sm:flex-none px-3 py-2 text-xs text-primary-grey hover:text-white transition-colors"
                        >
                            Dismiss
                        </button>
                        {suggestion.type === 'location' ? (
                            <>
                                <button
                                    onClick={() => handleShareLocation('city')}
                                    className="flex-1 sm:flex-none px-4 py-2 bg-primary-green/30 border border-primary-green/50 text-white text-xs font-bold rounded hover:bg-primary-green/50 transition-all"
                                >
                                    City/Pin
                                </button>
                                <button
                                    onClick={() => handleShareLocation('search')}
                                    className="flex-1 sm:flex-none px-4 py-2 bg-primary-green text-white text-xs font-bold rounded hover:bg-primary-green/80 transition-all"
                                >
                                    Pick a Spot
                                </button>
                                <button
                                    onClick={() => handleShareLocation('gps')}
                                    className="flex-1 sm:flex-none px-4 py-2 bg-white/10 border border-white/20 text-white text-xs font-bold rounded hover:bg-white/20 transition-all"
                                >
                                    Live GPS
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={handleShareContact}
                                className="flex-1 sm:flex-none px-4 py-2 bg-primary-green text-white text-xs font-bold rounded hover:bg-primary-green/80 transition-all"
                            >
                                Share Number
                            </button>
                        )}
                    </div>
                </motion.div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-primary-grey/30">
                <div className="flex gap-2">
                    <input
                        ref={inputRef}
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type a message..."
                        className="flex-1 bg-white/5 border border-primary-grey/30 rounded-lg px-4 py-3 text-white placeholder-primary-grey/50 focus:outline-none focus:border-primary-green transition-colors"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!newMessage.trim()}
                        className="px-6 py-3 bg-primary-green hover:bg-primary-green/80 disabled:bg-primary-grey/30 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
                    >
                        Send
                    </button>
                </div>
            </div>

            {/* Location Search Modal */}
            {isSearchingLocation && (
                <div className="absolute inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm rounded-xl">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="glass-effect w-full max-w-md p-6 rounded-2xl border border-white/20 shadow-2xl"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <span className="text-primary-green">📍</span> Choose Meeting Spot
                            </h3>
                            <button
                                onClick={() => setIsSearchingLocation(false)}
                                className="text-primary-grey hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="relative">
                                <input
                                    autoFocus
                                    type="text"
                                    value={locationQuery}
                                    onChange={(e) => setLocationQuery(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && searchLocations(locationQuery)}
                                    placeholder="Search for a mall, shop, or landmark..."
                                    className="w-full bg-black/50 border border-primary-grey/30 rounded-xl px-4 py-3 text-white focus:border-primary-green outline-none transition-all"
                                />
                                <button
                                    onClick={() => searchLocations(locationQuery)}
                                    className="absolute right-2 top-2 px-4 py-1.5 bg-primary-green text-white rounded-lg text-sm font-bold shadow-lg shadow-primary-green/20"
                                >
                                    {isSearching ? '...' : 'Search'}
                                </button>
                            </div>

                            <div className="max-h-60 overflow-y-auto space-y-2 scrollbar-hide">
                                {locationResults.length > 0 ? (
                                    locationResults.map((loc, i) => (
                                        <button
                                            key={i}
                                            onClick={() => selectLocation(loc)}
                                            className="w-full text-left p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 hover:border-primary-green/30 transition-all flex flex-col gap-1 group"
                                        >
                                            <span className="text-sm font-bold text-white group-hover:text-primary-green transition-colors">
                                                {loc.display_name.split(',')[0]}
                                            </span>
                                            <span className="text-[10px] text-primary-grey truncate">
                                                {loc.display_name}
                                            </span>
                                        </button>
                                    ))
                                ) : locationQuery && !isSearching ? (
                                    <p className="text-center text-xs text-primary-grey py-4">No spots found. Try a different name.</p>
                                ) : (
                                    <p className="text-center text-xs text-primary-grey py-4 italic">Type a landmark or area to find meeting spots</p>
                                )}
                            </div>
                        </div>

                        <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-white/10">
                            <button
                                onClick={() => setIsSearchingLocation(false)}
                                className="px-4 py-2 text-sm text-primary-grey hover:text-white"
                            >
                                Cancel
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    )
}

export default ChatWindow
