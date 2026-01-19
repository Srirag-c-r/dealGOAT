// Validation utilities

export const validateFirstName = (value) => {
  if (!value.trim()) {
    return { isValid: false, message: 'First name is required' }
  }
  if (value.trim().length < 2) {
    return { isValid: false, message: 'First name must be at least 2 characters' }
  }
  if (!/^[a-zA-Z\s]+$/.test(value.trim())) {
    return { isValid: false, message: 'First name can only contain letters' }
  }
  return { isValid: true, message: '' }
}

export const validateLastName = (value) => {
  if (!value.trim()) {
    return { isValid: false, message: 'Last name is required' }
  }
  if (value.trim().length < 2) {
    return { isValid: false, message: 'Last name must be at least 2 characters' }
  }
  if (!/^[a-zA-Z\s]+$/.test(value.trim())) {
    return { isValid: false, message: 'Last name can only contain letters' }
  }
  return { isValid: true, message: '' }
}

export const validateEmail = (value) => {
  if (!value.trim()) {
    return { isValid: false, message: 'Email is required' }
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value.trim())) {
    return { isValid: false, message: 'Please enter a valid email address' }
  }
  return { isValid: true, message: '' }
}

export const validatePhone = (value) => {
  if (!value.trim()) {
    return { isValid: false, message: 'Phone number is required' }
  }
  // Remove spaces, dashes, and parentheses
  const cleaned = value.replace(/[\s\-\(\)]/g, '')
  // Check if it's 10 digits (for most countries) or starts with + for international
  if (!/^(\+?\d{10,15})$/.test(cleaned)) {
    return { isValid: false, message: 'Please enter a valid phone number' }
  }
  return { isValid: true, message: '' }
}

export const validateLocation = (value) => {
  if (!value.trim()) {
    return { isValid: false, message: 'Location is required' }
  }
  if (value.trim().length < 3) {
    return { isValid: false, message: 'Location must be at least 3 characters' }
  }
  return { isValid: true, message: '' }
}

export const validateGender = (value) => {
  if (!value) {
    return { isValid: false, message: 'Please select your gender' }
  }
  return { isValid: true, message: '' }
}

export const validateAge = (value) => {
  if (!value) {
    return { isValid: false, message: 'Age is required' }
  }
  const age = parseInt(value)
  if (isNaN(age)) {
    return { isValid: false, message: 'Age must be a number' }
  }
  if (age < 18) {
    return { isValid: false, message: 'You must be at least 18 years old' }
  }
  if (age > 120) {
    return { isValid: false, message: 'Please enter a valid age' }
  }
  return { isValid: true, message: '' }
}

export const validatePassword = (value) => {
  if (!value) {
    return { isValid: false, message: 'Password is required' }
  }
  if (value.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters' }
  }
  if (!/(?=.*[a-z])/.test(value)) {
    return { isValid: false, message: 'Password must contain at least one lowercase letter' }
  }
  if (!/(?=.*[A-Z])/.test(value)) {
    return { isValid: false, message: 'Password must contain at least one uppercase letter' }
  }
  if (!/(?=.*\d)/.test(value)) {
    return { isValid: false, message: 'Password must contain at least one number' }
  }
  if (!/(?=.*[@$!%*?&])/.test(value)) {
    return { isValid: false, message: 'Password must contain at least one special character (@$!%*?&)' }
  }
  return { isValid: true, message: '' }
}

export const validateConfirmPassword = (password, confirmPassword) => {
  if (!confirmPassword) {
    return { isValid: false, message: 'Please confirm your password' }
  }
  if (password !== confirmPassword) {
    return { isValid: false, message: 'Passwords do not match' }
  }
  return { isValid: true, message: '' }
}

export const validateIMEI = (value) => {
  if (!value) {
    return { isValid: false, message: 'IMEI/Serial number is required' }
  }
  const cleaned = value.trim()
  if (cleaned.length < 8) {
    return { isValid: false, message: 'Number is too short' }
  }
  if (cleaned.length > 20) {
    return { isValid: false, message: 'Number is too long' }
  }
  // Allow alphanumeric for serial numbers, but mostly digits for IMEI
  if (!/^[a-zA-Z0-9]+$/.test(cleaned)) {
    return { isValid: false, message: 'Invalid characters' }
  }
  return { isValid: true, message: '' }
}

export const validatePincode = (value) => {
  if (!value) {
    return { isValid: false, message: 'Pincode is required' }
  }
  const cleaned = value.trim()
  if (!/^\d{6}$/.test(cleaned)) {
    return { isValid: false, message: 'Pincode must be exactly 6 digits' }
  }
  return { isValid: true, message: '' }
}

export const validatePrice = (value, min = 1, max = 1000000) => {
  if (value === undefined || value === null || value === '') {
    return { isValid: false, message: 'Price is required' }
  }
  const price = parseFloat(value)
  if (isNaN(price)) {
    return { isValid: false, message: 'Price must be a number' }
  }
  if (price < min) {
    return { isValid: false, message: `Price must be at least ₹${min.toLocaleString()}` }
  }
  if (price > max) {
    return { isValid: false, message: `Price cannot exceed ₹${max.toLocaleString()}` }
  }
  return { isValid: true, message: '' }
}

export const validateModel = (value) => {
  if (!value || !value.trim()) {
    return { isValid: false, message: 'Model name is required' }
  }
  if (value.trim().length < 2) {
    return { isValid: false, message: 'Model name is too short' }
  }
  return { isValid: true, message: '' }
}

