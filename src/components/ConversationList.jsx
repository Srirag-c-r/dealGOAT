import { motion } from 'framer-motion'

const ConversationList = ({ conversations, selectedConversation, onSelect, loading, currentUserId }) => {
    if (loading) {
        return (
            <div className="glass-effect rounded-xl p-6 h-full">
                <div className="text-primary-grey text-center">Loading conversations...</div>
            </div>
        )
    }

    if (conversations.length === 0) {
        return (
            <div className="glass-effect rounded-xl p-6 h-full">
                <div className="text-center text-primary-grey">
                    <div className="text-4xl mb-4">📭</div>
                    <p>No conversations yet</p>
                    <p className="text-sm mt-2">Start chatting with sellers!</p>
                </div>
            </div>
        )
    }

    return (
        <div className="glass-effect rounded-xl overflow-hidden h-full flex flex-col">
            <div className="p-4 border-b border-primary-grey/30">
                <h2 className="text-xl font-bold text-white">Conversations</h2>
            </div>

            <div className="flex-1 overflow-y-auto">
                {conversations.map((conversation) => {
                    const isSelected = selectedConversation?.id === conversation.id
                    const otherUser = conversation.buyer === currentUserId ? conversation.seller_name : conversation.buyer_name
                    const unreadCount = conversation.unread_count || 0

                    return (
                        <motion.div
                            key={conversation.id}
                            whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
                            onClick={() => onSelect(conversation)}
                            className={`p-4 cursor-pointer border-b border-primary-grey/20 transition-colors ${isSelected ? 'bg-primary-green/10 border-l-4 border-l-primary-green' : ''
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                {/* Avatars & Listing Image */}
                                <div className="relative flex-shrink-0">
                                    <div className="w-14 h-14 rounded-full overflow-hidden bg-primary-grey/20 border border-primary-grey/30">
                                        {((conversation.buyer === currentUserId ? conversation.seller_profile_picture : conversation.buyer_profile_picture)) ? (
                                            <img
                                                src={(conversation.buyer === currentUserId ? conversation.seller_profile_picture : conversation.buyer_profile_picture).startsWith('http')
                                                    ? (conversation.buyer === currentUserId ? conversation.seller_profile_picture : conversation.buyer_profile_picture)
                                                    : `http://localhost:8000${(conversation.buyer === currentUserId ? conversation.seller_profile_picture : conversation.buyer_profile_picture)}`}
                                                alt="Avatar"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-xl text-white font-bold bg-gradient-to-br from-primary-red to-red-900">
                                                {otherUser[0].toUpperCase()}
                                            </div>
                                        )}
                                    </div>
                                    {/* Small Listing Thumbnail Badge */}
                                    <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-lg overflow-hidden border-2 border-black bg-black">
                                        {conversation.listing_image ? (
                                            <img
                                                src={conversation.listing_image.startsWith('http') ? conversation.listing_image : `http://localhost:8000${conversation.listing_image}`}
                                                alt="Listing"
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-[10px]">📱</div>
                                        )}
                                    </div>
                                </div>

                                {/* Conversation Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className="text-white font-semibold truncate">{otherUser}</h3>
                                        {unreadCount > 0 && (
                                            <span className="bg-primary-red text-white text-xs font-bold px-2 py-1 rounded-full ml-2">
                                                {unreadCount}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-primary-grey truncate mb-1 flex items-center gap-2">
                                        <img
                                            src={conversation.listing_type === 'laptop' || (conversation.listing_title && conversation.listing_title.toLowerCase().includes('laptop')) ? '/laptopicon.png' : '/mobileicon.png'}
                                            alt="icon"
                                            className="w-4 h-4 object-contain"
                                        />
                                        {conversation.listing_title}
                                    </p>
                                    {conversation.last_message && (
                                        <p className="text-xs text-primary-grey/70 truncate">
                                            {conversation.last_message.content}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}

export default ConversationList
