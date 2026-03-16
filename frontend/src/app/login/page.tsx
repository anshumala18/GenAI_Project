"use client";

import React, { useState } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Mail, Lock, Loader2, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { login: setAuthContext } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (isLogin) {
        // Login flow
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await api.post('http://localhost:8000/login', formData);
        setAuthContext(response.data.access_token, response.data.user);
      } else {
        // Register flow
        console.log("DEBUG: Sending signup request:", { name, email });
        await api.post('http://localhost:8000/register', { name, email, password });
        setSuccess(true);
        setTimeout(() => {
          setIsLogin(true);
          setSuccess(false);
          setError(null);
        }, 2000);
      }
    } catch (err: any) {
      console.error('Auth Error:', err);
      setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#f8fafc] flex items-center justify-center p-4 font-sans relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-1/4 -right-1/4 w-1/2 h-1/2 bg-blue-50/50 rounded-full blur-[120px]" />
        <div className="absolute -bottom-1/4 -left-1/4 w-1/2 h-1/2 bg-indigo-50/50 rounded-full blur-[120px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-[440px] bg-white rounded-[32px] shadow-2xl shadow-blue-500/5 p-8 md:p-10 z-10 border border-gray-100 relative"
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-10">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 mb-6"
          >
            <ShieldAlert className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-3xl font-black tracking-tight text-gray-900 mb-2">
            Doc<span className="text-blue-600">AI</span>
          </h1>
          <p className="text-sm font-semibold text-gray-400 uppercase tracking-[0.2em]">
            {isLogin ? 'Welcome Back' : 'Join DocAI'}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {success ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex flex-col items-center justify-center py-10"
            >
              <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
              <p className="font-bold text-gray-900">Registration Successful!</p>
              <p className="text-sm text-gray-400">Redirecting to login...</p>
            </motion.div>
          ) : (
            <motion.form
              key={isLogin ? 'login' : 'register'}
              initial={{ opacity: 0, x: isLogin ? -10 : 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: isLogin ? 10 : -10 }}
              transition={{ duration: 0.3 }}
              onSubmit={handleSubmit}
              className="space-y-6"
            >
              <div className="space-y-4">
                {!isLogin && (
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <div className="w-5 h-5 flex items-center justify-center text-gray-300 group-focus-within:text-blue-500 transition-colors font-bold text-xs">A</div>
                    </div>
                    <input
                      type="text"
                      required
                      placeholder="Full Name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full bg-gray-50 border-2 border-transparent focus:border-blue-600 focus:bg-white rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold transition-all outline-none text-gray-900"
                    />
                  </div>
                )}
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="w-5 h-5 text-gray-300 group-focus-within:text-blue-500 transition-colors" />
                  </div>
                  <input
                    type="email"
                    required
                    placeholder="Email Address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-gray-50 border-2 border-transparent focus:border-blue-600 focus:bg-white rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold transition-all outline-none text-gray-900"
                  />
                </div>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-gray-300 group-focus-within:text-blue-500 transition-colors" />
                  </div>
                  <input
                    type="password"
                    required
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-gray-50 border-2 border-transparent focus:border-blue-600 focus:bg-white rounded-2xl pl-12 pr-4 py-4 text-sm font-semibold transition-all outline-none text-gray-900"
                  />
                </div>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-red-50 border border-red-100 p-3 rounded-xl text-xs font-bold text-red-600 flex items-center gap-2"
                >
                  <div className="w-1.5 h-1.5 bg-red-600 rounded-full" />
                  {error}
                </motion.div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl hover:bg-blue-700 transition-all shadow-xl shadow-blue-600/10 active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100 flex items-center justify-center gap-2 group"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    {isLogin ? 'Sign In' : 'Create Account'}
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-sm font-bold text-gray-400 hover:text-blue-600 transition-colors"
                >
                  {isLogin ? (
                    <>Don't have an account? <span className="text-blue-600 underline underline-offset-4 font-black">Register</span></>
                  ) : (
                    <>Already have an account? <span className="text-blue-600 underline underline-offset-4 font-black">Sign In</span></>
                  )}
                </button>
              </div>
            </motion.form>
          )}
        </AnimatePresence>
      </motion.div>
      
      {/* Footer Branding */}
      <div className="absolute bottom-8 left-0 w-full text-center z-10">
        <p className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-400">
          Enterprise Document Intelligence Platform
        </p>
      </div>
    </div>
  );
}
