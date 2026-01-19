import { motion, AnimatePresence } from 'framer-motion'

const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', type = 'info' }) => {
    if (!isOpen) return null

    const config = {
        danger: {
            btnBg: 'bg-primary-red',
            btnHover: 'hover:bg-red-700',
            icon: '🗑️'
        },
        warning: {
            btnBg: 'bg-yellow-600',
            btnHover: 'hover:bg-yellow-700',
            icon: '⚠️'
        },
        info: {
            btnBg: 'bg-primary-green',
            btnHover: 'hover:bg-green-700',
            icon: 'ℹ️'
        }
    }

    const style = config[type] || config.info

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                />

                {/* Modal */}
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="relative bg-[#1a1a1a] border border-primary-grey/30 rounded-xl p-6 max-w-sm w-full shadow-2xl"
                >
                    <div className="text-center mb-6">
                        <div className="text-4xl mb-4">{style.icon}</div>
                        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
                        <p className="text-primary-grey">{message}</p>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="flex-1 py-3 px-4 bg-transparent border border-primary-grey/50 text-white rounded-lg hover:bg-white/5 transition-colors font-semibold"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={() => {
                                onConfirm()
                                onClose()
                            }}
                            className={`flex-1 py-3 px-4 ${style.btnBg} ${style.btnHover} text-white rounded-lg transition-colors font-bold shadow-lg`}
                        >
                            {confirmText}
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    )
}

export default ConfirmationModal
