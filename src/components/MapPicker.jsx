import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const MapPicker = ({ isOpen, onClose, onConfirm, initialLocation }) => {
    const mapRef = useRef(null)
    const mapInstance = useRef(null)
    const markerInstance = useRef(null)
    const [selectedCoords, setSelectedCoords] = useState(null)

    useEffect(() => {
        if (isOpen && mapRef.current && !mapInstance.current) {
            // Wait for modal animation to finish before initializing map
            setTimeout(() => {
                const defaultLat = initialLocation?.lat || 12.9716
                const defaultLng = initialLocation?.lng || 77.5946

                mapInstance.current = L.map(mapRef.current).setView([defaultLat, defaultLng], 13)

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(mapInstance.current)

                markerInstance.current = L.marker([defaultLat, defaultLng], {
                    draggable: true
                }).addTo(mapInstance.current)

                setSelectedCoords({ lat: defaultLat, lng: defaultLng })

                markerInstance.current.on('dragend', () => {
                    const pos = markerInstance.current.getLatLng()
                    setSelectedCoords({ lat: pos.lat, lng: pos.lng })
                })

                mapInstance.current.on('click', (e) => {
                    markerInstance.current.setLatLng(e.latlng)
                    setSelectedCoords({ lat: e.latlng.lat, lng: e.latlng.lng })
                })
            }, 300)
        }

        return () => {
            if (mapInstance.current) {
                mapInstance.current.remove()
                mapInstance.current = null
            }
        }
    }, [isOpen])

    const handleConfirm = () => {
        if (selectedCoords) {
            onConfirm(selectedCoords)
            onClose()
        }
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="bg-[#1A1A1A] border border-primary-grey/30 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl"
                    >
                        <div className="p-4 border-b border-primary-grey/30 flex justify-between items-center bg-white/5">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                📍 Pick Meetup Spot
                            </h3>
                            <button onClick={onClose} className="text-primary-grey hover:text-white transition-colors">✕</button>
                        </div>

                        <div className="p-4">
                            <p className="text-sm text-primary-grey mb-4">
                                Drag the pin or click on the map to select a safe public meeting place.
                            </p>

                            <div className="h-[400px] w-full rounded-xl overflow-hidden border border-primary-grey/20">
                                <div ref={mapRef} className="h-full w-full bg-black/20" />
                            </div>

                            <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-end">
                                <button
                                    onClick={onClose}
                                    className="px-6 py-2 rounded-lg text-primary-grey hover:text-white border border-primary-grey/30 transition-all font-semibold"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleConfirm}
                                    className="px-8 py-2 rounded-lg bg-primary-green text-white font-bold hover:bg-primary-green/80 transition-all shadow-lg shadow-primary-green/20"
                                >
                                    Confirm Spot
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    )
}

export default MapPicker
