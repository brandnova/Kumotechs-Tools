import React, { useState } from 'react';
import { User, Mail, Phone, Building2, Send, Check, AlertCircle } from 'lucide-react';
import { Logo } from './Logo';
import { motion, AnimatePresence } from 'framer-motion';

const inputClasses = "w-full px-4 py-3 pl-12 bg-gray-50 border-0 rounded-lg focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all duration-200";
const labelClasses = "block text-sm font-medium text-gray-600 mb-1";
const iconClasses = "h-5 w-5 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2";

export default function ContactForm() {
  const [formData, setFormData] = useState({
    prefix: '',
    name: '',
    email: '',
    phone: '',
    organization: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await fetch('https://mrnova.pythonanywhere.com/api/submit-contact/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      setStatus({
        type: 'success',
        message: data.message || 'Contact submitted successfully!'
      });
      
      setFormData({
        prefix: '',
        name: '',
        email: '',
        phone: '',
        organization: ''
      });
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Failed to submit contact. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl"
      >
        <div className="text-center">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Logo className="w-20 h-20 mx-auto" />
          </motion.div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Contact Details
          </h2>
          <p className="mt-2 text-gray-600">Please fill in your information below</p>
        </div>

        <AnimatePresence>
          {status.message && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`p-4 rounded-lg flex items-center gap-3 ${
                status.type === 'success' 
                  ? 'bg-green-50 text-green-700 border border-green-200' 
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {status.type === 'success' ? (
                <Check className="h-5 w-5" />
              ) : (
                <AlertCircle className="h-5 w-5" />
              )}
              {status.message}
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="space-y-4">
            <div>
              <label className={labelClasses}>
                Prefix
              </label>
              <select
                value={formData.prefix}
                onChange={(e) => setFormData({...formData, prefix: e.target.value})}
                className={inputClasses}
              >
                <option value="">Select prefix</option>
                <option value="Mr.">Mr.</option>
                <option value="Mrs.">Mrs.</option>
                <option value="Ms.">Ms.</option>
                <option value="Dr.">Dr.</option>
              </select>
            </div>

            {[
              { label: 'Name', icon: User, value: 'name', type: 'text', required: true },
              { label: 'Email', icon: Mail, value: 'email', type: 'email', required: false },
              { label: 'Phone', icon: Phone, value: 'phone', type: 'tel', required: true },
              { label: 'Organization', icon: Building2, value: 'organization', type: 'text', required: false }
            ].map((field) => (
              <div key={field.value}>
                <label className={labelClasses}>
                  {field.label}
                </label>
                <div className="relative">
                  <field.icon className={iconClasses} />
                  <input
                    type={field.type}
                    required={field.required}
                    value={formData[field.value]}
                    onChange={(e) => setFormData({...formData, [field.value]: e.target.value})}
                    className={inputClasses}
                  />
                </div>
              </div>
            ))}
          </div>

          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            type="submit"
            disabled={isSubmitting}
            className="relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <span className="absolute left-4 inset-y-0 flex items-center">
              <Send className="h-5 w-5" />
            </span>
            {isSubmitting ? 'Submitting...' : 'Submit Contact'}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
}