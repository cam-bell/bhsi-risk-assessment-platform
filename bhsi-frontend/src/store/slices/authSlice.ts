import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface User {
  id: string;
  email: string;
  name: string;
  role?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Load persisted auth state from localStorage
const loadPersistedAuthState = (): Partial<AuthState> => {
  try {
    const token = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      const user = JSON.parse(userStr);
      return {
        user,
        token,
        isAuthenticated: true,
      };
    }
  } catch (error) {
    console.error('Error loading persisted auth state:', error);
  }
  return {};
};

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    ...initialState,
    ...loadPersistedAuthState(),
  },
  reducers: {
    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
      state.error = null;
    },
    
    // Login success
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      state.isLoading = false;
      state.error = null;
      
      // Persist to localStorage
      localStorage.setItem('authToken', action.payload.token);
      localStorage.setItem('user', JSON.stringify(action.payload.user));
    },
    
    // Login failure
    loginFailure: (state, action: PayloadAction<string>) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.error = action.payload;
      
      // Clear localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    },
    
    // Logout
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.error = null;
      
      // Clear localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    },
    
    // Update user profile
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
        localStorage.setItem('user', JSON.stringify(state.user));
      }
    },
    
    // Clear error
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  loginSuccess,
  loginFailure,
  logout,
  updateUser,
  clearError,
} = authSlice.actions;

export default authSlice.reducer; 