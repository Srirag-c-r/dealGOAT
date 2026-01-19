import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import UserNavbar from '../components/UserNavbar';
import MessagePopup from '../components/MessagePopup';
import {
    validateIMEI,
    validatePincode,
    validatePrice,
    validateLocation
} from '../utils/validation';

const CreateListing = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { predictionData, deviceType } = location.state || {};

    const [user, setUser] = useState(null);

    useEffect(() => {
        // Check authentication
        const userData = localStorage.getItem('user')
        if (userData) {
            setUser(JSON.parse(userData))
        } else {
            navigate('/login')
        }
    }, [navigate])

    // Steps: 1. Identity, 2. Ownership, 3. Condition, 4. Images, 5. Price, 6. Preferences, 7. Consent
    const [step, setStep] = useState(1);
    const totalSteps = 7;

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });

    const [formData, setFormData] = useState({
        imei_or_serial: '',
        invoice_available: false,
        invoice_date: '',

        // Laptop specific
        laptop_repair_history: '',

        // Conditions
        screen_condition: 'No scratches',
        body_condition: 'Like new',
        port_condition: 'Fully working',
        camera_condition: 'Fully working',

        // Price
        expected_price: predictionData?.predicted_price || '',
        is_negotiable: false,

        // Preferences
        delivery_option: 'Pickup',
        city: predictionData?.seller_location || '',
        pincode: '',
        is_willing_to_ship: false,

        // Consent
        is_legal_owner: false,
        is_no_issues: false,
        is_details_accurate: false,
    });

    const [validations, setValidations] = useState({
        imei_or_serial: { isValid: false, isTouched: false, message: '' },
        expected_price: { isValid: true, isTouched: false, message: '' },
        city: { isValid: true, isTouched: false, message: '' },
        pincode: { isValid: false, isTouched: false, message: '' },
        image_front: { isValid: false, isTouched: false, message: '' },
        image_back: { isValid: false, isTouched: false, message: '' },
        image_side: { isValid: false, isTouched: false, message: '' },
        image_screen_on: { isValid: false, isTouched: false, message: '' },
        image_proof: { isValid: false, isTouched: false, message: '' },
    });

    const [images, setImages] = useState({
        image_front: null,
        image_back: null,
        image_side: null,
        image_screen_on: null,
        image_proof: null,
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        const val = type === 'checkbox' ? checked : value;
        setFormData({
            ...formData,
            [name]: val
        });

        // Real-time validation
        let validation = { isValid: true, message: '' };
        if (name === 'imei_or_serial') {
            validation = validateIMEI(val);
        } else if (name === 'expected_price') {
            validation = validatePrice(val, 1, 1000000);
        } else if (name === 'city') {
            validation = validateLocation(val);
        } else if (name === 'pincode') {
            validation = validatePincode(val);
        }

        if (validations[name]) {
            setValidations(prev => ({
                ...prev,
                [name]: { ...validation, isTouched: true }
            }));
        }
    };

    const handleBlur = (name) => {
        if (validations[name]) {
            setValidations(prev => ({
                ...prev,
                [name]: { ...prev[name], isTouched: true }
            }));
        }
    };

    const handleImageChange = (e, fieldName) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setImages({
                ...images,
                [fieldName]: file
            });

            // Update image validation
            setValidations(prev => ({
                ...prev,
                [fieldName]: { isValid: true, isTouched: true, message: '' }
            }));
        }
    };

    const getFieldClassName = (field, baseClass = "") => {
        const validation = validations[field];
        if (!validation || !validation.isTouched) {
            return `${baseClass} border-primary-grey/30 focus:border-primary-green`;
        }
        if (validation.isValid) {
            return `${baseClass} border-primary-green border-2`;
        }
        return `${baseClass} border-primary-red border-2`;
    };

    const nextStep = () => setStep(step + 1);
    const prevStep = () => setStep(step - 1);

    const handleSubmit = async () => {
        setLoading(true);
        setError('');

        try {
            const data = new FormData();

            // prediction link
            if (deviceType === 'smartphone') {
                data.append('smartphone_prediction', predictionData.id);
                data.append('device_type', 'smartphone');
            } else {
                data.append('laptop_prediction', predictionData?.id);
                data.append('device_type', 'laptop');
            }

            // form fields
            Object.keys(formData).forEach(key => {
                data.append(key, formData[key]);
            });

            // images
            Object.keys(images).forEach(key => {
                if (images[key]) {
                    data.append(key, images[key]);
                }
            });

            await api.createListing(data);
            setMessage({ type: 'success', text: 'Listing created successfully!' });
            setTimeout(() => {
                navigate('/user-home');
            }, 1500);

        } catch (err) {
            setMessage({ type: 'error', text: err.message || 'Failed to create listing' });
        } finally {
            setLoading(false);
        }
    };

    // Reusable Input Components
    const InputField = ({ label, name, type = "text", value, onChange, onBlur, placeholder, required = false, min, max, error }) => (
        <div>
            <label className="block text-primary-grey text-sm font-semibold mb-2">
                {label} {required && <span className="text-primary-red">*</span>}
            </label>
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                onBlur={() => onBlur && onBlur(name)}
                placeholder={placeholder}
                required={required}
                min={min}
                max={max}
                className={getFieldClassName(name, "w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border focus:outline-none transition-colors")}
            />
            {error && <p className="text-primary-red text-xs mt-1">{error}</p>}
        </div>
    );

    const SelectField = ({ label, name, value, onChange, options }) => (
        <div>
            <label className="block text-primary-grey text-sm font-semibold mb-2">{label}</label>
            <select
                name={name}
                value={value}
                onChange={onChange}
                className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
            >
                {options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
        </div>
    );

    // --- Step Components ---

    const renderStep1_Identity = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">1. Confirm Identity</h3>
            <div className="p-6 bg-primary-darkGrey/50 border border-blue-500/30 rounded-lg">
                <p className="text-blue-200">Please confirm your seller details.</p>
                <div className="mt-4 space-y-2">
                    <p className="text-white"><strong>User:</strong> {user?.username || 'Authenticated User'}</p>
                    <p className="text-white"><strong>Email:</strong> {user?.email || ''}</p>
                    <p className="text-sm text-primary-grey mt-2">These details will be shown to potential buyers.</p>
                </div>
            </div>
            <button onClick={nextStep} className="w-full py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 transition-all">
                Confirm & Continue
            </button>
        </div>
    );

    const renderStep2_Ownership = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">2. Device Ownership</h3>

            <InputField
                label={deviceType === 'smartphone' ? "IMEI Number" : "Serial Number"}
                name="imei_or_serial"
                value={formData.imei_or_serial}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={deviceType === 'smartphone' ? "e.g. 3548..." : "e.g. C02..."}
                required
                error={validations.imei_or_serial.isTouched && validations.imei_or_serial.message}
            />

            <div className="flex items-center space-x-3 p-4 bg-primary-darkGrey/30 rounded-lg border border-primary-grey/20">
                <input
                    type="checkbox"
                    name="invoice_available"
                    checked={formData.invoice_available}
                    onChange={handleChange}
                    className="h-5 w-5 accent-primary-green"
                />
                <label className="text-white">Original Invoice Available?</label>
            </div>

            {formData.invoice_available && (
                <InputField
                    label="Invoice Date"
                    name="invoice_date"
                    type="date"
                    value={formData.invoice_date}
                    onChange={handleChange}
                />
            )}

            {deviceType === 'laptop' && (
                <div>
                    <label className="block text-primary-grey text-sm font-semibold mb-2">Repair History</label>
                    <textarea
                        name="laptop_repair_history"
                        value={formData.laptop_repair_history}
                        onChange={handleChange}
                        className="w-full px-4 py-3 bg-primary-darkGrey text-white rounded-lg border border-primary-grey/30 focus:border-primary-green focus:outline-none transition-colors"
                        placeholder="Details of any repairs..."
                        rows={3}
                    />
                </div>
            )}

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button
                    onClick={nextStep}
                    disabled={!validations.imei_or_serial.isValid}
                    className="flex-1 py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 disabled:opacity-50 transition-all"
                >
                    Next
                </button>
            </div>
        </div>
    );

    const renderStep3_Condition = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">3. Physical Condition</h3>

            <SelectField
                label="Screen Condition"
                name="screen_condition"
                value={formData.screen_condition}
                onChange={handleChange}
                options={['No scratches', 'Minor scratches', 'Cracks']}
            />

            <SelectField
                label="Body Condition"
                name="body_condition"
                value={formData.body_condition}
                onChange={handleChange}
                options={['Like new', 'Minor dents', 'Major dents']}
            />

            <SelectField
                label="Ports & Buttons"
                name="port_condition"
                value={formData.port_condition}
                onChange={handleChange}
                options={['Fully working', 'Minor issues']}
            />

            {deviceType === 'smartphone' && (
                <SelectField
                    label="Camera / Speaker / Mic"
                    name="camera_condition"
                    value={formData.camera_condition}
                    onChange={handleChange}
                    options={['Fully working', 'Minor issues']}
                />
            )}

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button onClick={nextStep} className="flex-1 py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 transition-all">Next</button>
            </div>
        </div>
    );

    const renderStep4_Images = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">4. Upload Real Images</h3>
            <div className="bg-primary-darkGrey/50 p-4 rounded-lg flex items-start gap-3">
                <span className="text-2xl">📸</span>
                <p className="text-gray-300 text-sm">Listings with clear, real images get 3x more visibility. Add photos of all angles.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {['image_front', 'image_back', 'image_side', 'image_screen_on', 'image_proof'].map((field) => (
                    <div key={field} className="border border-primary-grey/30 p-4 rounded-lg bg-black/20 hover:bg-primary-darkGrey/30 transition-colors">
                        <label className="block text-white text-sm font-medium capitalize mb-2">
                            {field.replace('image_', '').replace('_', ' ')} {field === 'image_proof' && <span className="text-primary-red text-xs ml-1">(Blurred IMEI/Serial)</span>}
                        </label>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => handleImageChange(e, field)}
                            className={`text-sm text-primary-grey file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-darkGrey file:text-white hover:file:bg-primary-grey/50 ${validations[field].isTouched && !validations[field].isValid ? 'ring-2 ring-primary-red' : ''}`}
                        />
                        {validations[field].isTouched && !validations[field].isValid && (
                            <p className="text-primary-red text-[10px] mt-1">Image required</p>
                        )}
                    </div>
                ))}
            </div>

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button
                    onClick={nextStep}
                    disabled={!validations.image_front.isValid || !validations.image_back.isValid || !validations.image_side.isValid || !validations.image_screen_on.isValid || !validations.image_proof.isValid}
                    className="flex-1 py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 disabled:opacity-50 transition-all"
                >
                    Next
                </button>
            </div>
        </div>
    );

    const renderStep5_Price = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">5. Price & Flexibility</h3>

            <div className="p-6 bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-500/30 rounded-xl relative overflow-hidden">
                <div className="relative z-10">
                    <p className="text-green-300 text-sm font-medium mb-1">AI Suggested Price</p>
                    <p className="text-4xl font-bold text-white">₹{predictionData?.predicted_price ? predictionData.predicted_price.toLocaleString() : 'N/A'}</p>
                </div>
            </div>

            <InputField
                label="Your Expected Price (₹)"
                name="expected_price"
                type="number"
                value={formData.expected_price}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                error={validations.expected_price.isTouched && validations.expected_price.message}
            />

            <div className="flex items-center space-x-3 p-4 bg-primary-darkGrey/30 rounded-lg border border-primary-grey/20">
                <input
                    type="checkbox"
                    name="is_negotiable"
                    checked={formData.is_negotiable}
                    onChange={handleChange}
                    className="h-5 w-5 accent-primary-green"
                />
                <label className="text-white">Price is Negotiable</label>
            </div>

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button
                    onClick={nextStep}
                    disabled={!validations.expected_price.isValid}
                    className="flex-1 py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 disabled:opacity-50 transition-all"
                >
                    Next
                </button>
            </div>
        </div>
    );

    const renderStep6_Preferences = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">6. Selling Preferences</h3>

            <SelectField
                label="Delivery Option"
                name="delivery_option"
                value={formData.delivery_option}
                onChange={handleChange}
                options={['Pickup', 'Ship via courier', 'Local meet-up']}
            />

            <InputField
                label="City"
                name="city"
                value={formData.city}
                onChange={handleChange}
                onBlur={handleBlur}
                error={validations.city.isTouched && validations.city.message}
            />

            <InputField
                label="Pincode"
                name="pincode"
                value={formData.pincode}
                onChange={handleChange}
                onBlur={handleBlur}
                error={validations.pincode.isTouched && validations.pincode.message}
            />

            <div className="flex items-center space-x-3 p-4 bg-primary-darkGrey/30 rounded-lg border border-primary-grey/20">
                <input
                    type="checkbox"
                    name="is_willing_to_ship"
                    checked={formData.is_willing_to_ship}
                    onChange={handleChange}
                    className="h-5 w-5 accent-primary-green"
                />
                <label className="text-white">Willing to ship outside city?</label>
            </div>

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button
                    onClick={nextStep}
                    disabled={!validations.city.isValid || !validations.pincode.isValid}
                    className="flex-1 py-3 bg-primary-green text-white rounded-lg font-bold hover:bg-emerald-600 disabled:opacity-50 transition-all"
                >
                    Next
                </button>
            </div>
        </div>
    );

    const renderStep7_Consent = () => (
        <div className="space-y-6">
            <h3 className="text-2xl font-bold text-white">7. Legal & Consent</h3>

            <div className="space-y-4 bg-primary-darkGrey/30 p-6 rounded-lg border border-primary-grey/20">
                <label className="flex items-start space-x-3 cursor-pointer">
                    <input type="checkbox" name="is_legal_owner" checked={formData.is_legal_owner} onChange={handleChange} className="mt-1 h-5 w-5 accent-primary-green" />
                    <span className="text-white text-sm">I confirm this device is legally owned by me, not stolen.</span>
                </label>
                <label className="flex items-start space-x-3 cursor-pointer">
                    <input type="checkbox" name="is_no_issues" checked={formData.is_no_issues} onChange={handleChange} className="mt-1 h-5 w-5 accent-primary-green" />
                    <span className="text-white text-sm">I confirm the device has no hidden issues not listed in the condition.</span>
                </label>
                <label className="flex items-start space-x-3 cursor-pointer">
                    <input type="checkbox" name="is_details_accurate" checked={formData.is_details_accurate} onChange={handleChange} className="mt-1 h-5 w-5 accent-primary-green" />
                    <span className="text-white text-sm">All details provided are accurate to the best of my knowledge.</span>
                </label>
            </div>

            {error && <div className="text-red-400 text-sm mt-4 bg-red-900/20 p-3 rounded">{error}</div>}

            <div className="flex gap-4 pt-4">
                <button onClick={prevStep} className="flex-1 py-3 border border-primary-grey text-white rounded-lg hover:border-white transition-all">Back</button>
                <button
                    onClick={handleSubmit}
                    disabled={loading || !formData.is_legal_owner || !formData.is_no_issues || !formData.is_details_accurate}
                    className="flex-1 py-3 bg-gradient-to-r from-primary-green to-emerald-600 text-white rounded-lg font-bold hover:shadow-lg hover:shadow-primary-green/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? 'Processing...' : '✅ Post Listing'}
                </button>
            </div>
        </div>
    );

    const getStepContent = () => {
        switch (step) {
            case 1: return renderStep1_Identity();
            case 2: return renderStep2_Ownership();
            case 3: return renderStep3_Condition();
            case 4: return renderStep4_Images();
            case 5: return renderStep5_Price();
            case 6: return renderStep6_Preferences();
            case 7: return renderStep7_Consent();
            default: return renderStep1_Identity();
        }
    };

    if (!user) return null;

    return (
        <div className="min-h-screen bg-black overflow-hidden relative">
            {/* Background Effects */}
            <div className="fixed inset-0 opacity-10 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-green via-black to-primary-red" />
            </div>

            <UserNavbar user={user} />

            <main className="relative z-10 px-6 py-12">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-3xl mx-auto"
                >
                    <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 text-center md:text-left">
                        <div>
                            <h2 className="text-3xl md:text-4xl font-bold text-white">Sell Your Device</h2>
                            <p className="text-primary-grey">Turn your predicted value into cash.</p>
                        </div>
                        <div className="bg-primary-darkGrey/50 px-4 py-2 rounded-full border border-primary-grey/30">
                            <span className="text-sm font-medium text-white">Step {step} of {totalSteps}</span>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-primary-darkGrey rounded-full h-2 mb-10 overflow-hidden">
                        <div className="bg-gradient-to-r from-primary-green to-emerald-500 h-full rounded-full transition-all duration-300 shadow-[0_0_10px_rgba(16,185,129,0.5)]" style={{ width: `${(step / totalSteps) * 100}%` }}></div>
                    </div>

                    <AnimatePresence mode='wait'>
                        <motion.div
                            key={step}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.2 }}
                            className="glass-effect rounded-2xl p-6 md:p-10 shadow-2xl"
                        >
                            {getStepContent()}
                        </motion.div>
                    </AnimatePresence>
                </motion.div>
            </main>

            {message.text && (
                <MessagePopup
                    type={message.type}
                    message={message.text}
                    onClose={() => setMessage({ type: '', text: '' })}
                />
            )}
        </div>
    );
};

export default CreateListing;
