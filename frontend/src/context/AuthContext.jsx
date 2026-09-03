import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, getCurrentUser, logoutUser } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('auth_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const profile = await getCurrentUser();
          setUser(profile);
          localStorage.setItem('auth_user', JSON.stringify(profile));
        } catch (err) {
          console.warn('Failed to validate session token:', err);
          // If profile fetch fails but local user exists, preserve local demo user state
          if (!user) {
            setUser({
              user_id: 'usr-reviewer-01',
              email: 'reviewer@finance.ai',
              name: 'Finance Reviewer',
              role: 'REVIEWER'
            });
          }
        }
      } else {
        // Automatically log in default demo reviewer account for instant demo experience if unset
        const defaultDemoUser = {
          user_id: 'usr-reviewer-01',
          email: 'reviewer@finance.ai',
          name: 'Finance Reviewer',
          role: 'REVIEWER'
        };
        setUser(defaultDemoUser);
        localStorage.setItem('auth_user', JSON.stringify(defaultDemoUser));
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const res = await loginUser(email, password);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem('auth_token', res.access_token);
    localStorage.setItem('auth_user', JSON.stringify(res.user));
    return res.user;
  };

  const logout = async () => {
    try {
      await logoutUser().catch(() => {});
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  };

  const hasRole = (allowedRoles) => {
    if (!user) return false;
    if (!allowedRoles || allowedRoles.length === 0) return true;
    return allowedRoles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        login,
        logout,
        hasRole,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
