// src/components/Auth/Login.jsx
import React from 'react';

const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Logo Section - Exact like yours */}
        <div className="text-center mb-8">
          <img 
            src="/images/logo.jpg" 
            alt="Wallet Logo" 
            className="w-20 h-20 rounded-2xl mx-auto mb-4 object-cover"
          />
          <h1 className="text-4xl font-bold text-white mb-2">Your Wallet</h1>
          <p className="text-slate-400">Secure P2P Wallet</p>
        </div>
        
        {/* Login Card - Glass effect */}
        <div className="glass-card p-6">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Sign In</h2>
          
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <input 
                type="email" 
                className="w-full input-field" 
                placeholder="Enter your email" 
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <input 
                  type="password" 
                  className="w-full input-field pr-10" 
                  placeholder="Enter your password" 
                  required
                />
                <button type="button" className="toggle-password absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-cyan-400">
                  👁️
                </button>
              </div>
            </div>
            
            <button type="submit" className="w-full btn-primary mt-2">
              Sign In
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
