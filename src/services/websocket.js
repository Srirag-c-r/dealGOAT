class WebSocketService {
    constructor() {
        this.socket = null
        this.conversationId = null
        this.messageHandlers = []
    }

    connect(conversationId, onMessage) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.disconnect()
        }

        this.conversationId = conversationId
        const token = localStorage.getItem('token')

        // WebSocket URL (ws:// for development, wss:// for production)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${wsProtocol}//localhost:8000/ws/chat/${conversationId}/?token=${token}`

        this.socket = new WebSocket(wsUrl)

        this.socket.onopen = () => {
            console.log('WebSocket connected')
        }

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data)
            if (data.type === 'message' && onMessage) {
                onMessage(data.message)
            }
        }

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error)
        }

        this.socket.onclose = () => {
            console.log('WebSocket disconnected')
        }

        return this.socket
    }

    sendMessage(content) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                message: content
            }))
            return true
        }
        return false
    }

    disconnect() {
        if (this.socket) {
            this.socket.close()
            this.socket = null
        }
    }

    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN
    }
}

export default new WebSocketService()
