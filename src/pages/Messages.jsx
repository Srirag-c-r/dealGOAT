import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import UserNavbar from '../components/UserNavbar'
import api from '../services/api'
import ChatWindow from '../components/ChatWindow'
import ConversationList from '../components/ConversationList'

const Messages = () => {
    const navigate = useNavigate()
    const [user, setUser] = useState(null)
    const [conversations, setConversations] = useState([])
    const [selectedConversation, setSelectedConversation] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const userData = localStorage.getItem('user')
        if (userData) {
            setUser(JSON.parse(userData))
        } else {
            navigate('/login')
        }
    }, [navigate])

    useEffect(() => {
        if (user) {
            fetchConversations()
        }
    }, [user])

    const fetchConversations = async () => {
        try {
            const response = await api.getConversations()
            if (response.success) {
                setConversations(response.data)
                setLoading(false)
            }
        } catch (error) {
            console.error('Failed to fetch conversations:', error)
            setLoading(false)
        }
    }

    const handleConversationSelect = (conversation) => {
        setSelectedConversation(conversation)
    }

    if (!user) return null

    return (
        <div className="min-h-screen bg-black">
            <UserNavbar user={user} />

            <div className="max-w-7xl mx-auto px-4 py-24">
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-4xl font-bold text-white mb-8"
                >
                    Messages
                </motion.h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
                    {/* Left Sidebar - Conversation List */}
                    <div className="lg:col-span-1">
                        <ConversationList
                            conversations={conversations}
                            selectedConversation={selectedConversation}
                            onSelect={handleConversationSelect}
                            loading={loading}
                            currentUserId={user.id}
                        />
                    </div>

                    {/* Right Panel - Chat Window */}
                    <div className="lg:col-span-2">
                        {selectedConversation ? (
                            <ChatWindow
                                conversation={selectedConversation}
                                currentUser={user}
                                onClose={() => setSelectedConversation(null)}
                            />
                        ) : (
                            <div className="glass-effect rounded-xl h-full flex items-center justify-center">
                                <div className="text-center text-primary-grey">
                                    <div className="text-6xl mb-4">💬</div>
                                    <p className="text-xl">Select a conversation to start chatting</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Messages
