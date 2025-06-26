import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: number;
}

export interface UIState {
  // Sidebar state
  sidebarOpen: boolean;
  
  // Loading states
  globalLoading: boolean;
  
  // Notifications
  notifications: Notification[];
  
  // Modals
  modals: {
    [key: string]: boolean;
  };
  
  // Theme
  darkMode: boolean;
}

const initialState: UIState = {
  sidebarOpen: true,
  globalLoading: false,
  notifications: [],
  modals: {},
  darkMode: false,
};

// Load persisted UI state from localStorage
const loadPersistedUIState = (): Partial<UIState> => {
  try {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    const sidebarOpen = localStorage.getItem('sidebarOpen') !== 'false'; // Default to true
    
    return {
      darkMode,
      sidebarOpen,
    };
  } catch (error) {
    console.error('Error loading persisted UI state:', error);
  }
  return {};
};

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    ...initialState,
    ...loadPersistedUIState(),
  },
  reducers: {
    // Sidebar
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
      localStorage.setItem('sidebarOpen', state.sidebarOpen.toString());
    },
    
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
      localStorage.setItem('sidebarOpen', action.payload.toString());
    },
    
    // Global loading
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
    },
    
    // Notifications
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        timestamp: Date.now(),
      };
      state.notifications.push(notification);
    },
    
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    // Modals
    openModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = true;
    },
    
    closeModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = false;
    },
    
    closeAllModals: (state) => {
      Object.keys(state.modals).forEach((key) => {
        state.modals[key] = false;
      });
    },
    
    // Theme
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
      localStorage.setItem('darkMode', state.darkMode.toString());
    },
    
    setDarkMode: (state, action: PayloadAction<boolean>) => {
      state.darkMode = action.payload;
      localStorage.setItem('darkMode', action.payload.toString());
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  setGlobalLoading,
  addNotification,
  removeNotification,
  clearNotifications,
  openModal,
  closeModal,
  closeAllModals,
  toggleDarkMode,
  setDarkMode,
} = uiSlice.actions;

export default uiSlice.reducer; 