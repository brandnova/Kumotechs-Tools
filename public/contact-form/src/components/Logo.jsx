import React from 'react';
import { motion } from 'framer-motion';

export const Logo = ({ className = "w-12 h-12" }) => {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background container with subtle gradient */}
      <defs>
        <linearGradient id="card-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#2563EB" />
        </linearGradient>
      </defs>

      {/* Main card shape with rounded corners */}
      <rect
        x="10"
        y="20"
        width="80"
        height="60"
        rx="12"
        fill="url(#card-gradient)"
        className="drop-shadow-lg"
      />

      {/* Contact icon with improved styling */}
      <circle
        cx="50"
        cy="45"
        r="12"
        fill="white"
        opacity="0.95"
      />
      
      {/* Decorative lines representing form fields */}
      <path
        d="M30 70h40"
        stroke="white"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.9"
      />
      <path
        d="M30 62h20"
        stroke="white"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.7"
      />

      {/* Success checkmark with improved positioning */}
      <path
        d="M68 35l8 8l12-12"
        stroke="#10B981"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="drop-shadow-sm"
      />
    </svg>
  );
};
