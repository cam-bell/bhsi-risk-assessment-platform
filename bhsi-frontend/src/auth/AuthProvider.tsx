import { createContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface User {
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

// Mock user database
const mockUsers = {
  'john@bhsi.com': {
    password: 'password123',
    name: 'John Smith',
    role: 'underwriter'
  },
  'sarah@bhsi.com': {
    password: 'password456',
    name: 'Sarah Johnson',
    role: 'underwriter'
  },
  'mike@bhsi.com': {
    password: 'password789',
    name: 'Mike Wilson',
    role: 'underwriter'
  }
};

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      const userData = JSON.parse(storedUser);
      setToken(storedToken);
      setUser(userData);
      setIsAuthenticated(true);
      
      // Load user-specific saved results
      const savedResults = localStorage.getItem(`savedResults-${userData.email}`);
      if (savedResults) {
        localStorage.setItem('savedResults', savedResults);
      }
      
      if (location.pathname === '/login') {
        navigate('/', { replace: true });
      }
    } else if (location.pathname !== '/login') {
      navigate('/login', { replace: true });
    }
    
    setIsLoading(false);
  }, [navigate, location.pathname]);
  
  const login = async (email: string, password: string): Promise<boolean> => {
    const mockUser = mockUsers[email.toLowerCase()];
    
    if (mockUser && mockUser.password === password) {
      const userData = {
        email: email.toLowerCase(),
        name: mockUser.name,
        role: mockUser.role,
      };
      const mockToken = 'mock-jwt-' + Math.random().toString(36).substring(2);
      
      // Load user-specific saved results before setting them in localStorage
      const userSavedResults = localStorage.getItem(`savedResults-${userData.email}`);
      if (userSavedResults) {
        localStorage.setItem('savedResults', userSavedResults);
      } else {
        localStorage.removeItem('savedResults');
      }
      
      localStorage.setItem('token', mockToken);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      setToken(mockToken);
      setIsAuthenticated(true);
      
      return true;
    }
    
    return false;
  };
  
  const logout = () => {
    if (user) {
      // Save current results to user-specific storage before clearing
      const currentResults = localStorage.getItem('savedResults');
      if (currentResults) {
        localStorage.setItem(`savedResults-${user.email}`, currentResults);
      }
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('savedResults');
    
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    
    navigate('/login', { replace: true });
  };
  
  if (isLoading) {
    return null;
  }
  
  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};