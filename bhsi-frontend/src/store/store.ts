import { configureStore } from '@reduxjs/toolkit';
import { riskAssessmentApi } from './api/riskAssessmentApi';
import authSlice from './slices/authSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    // RTK Query API slice
    [riskAssessmentApi.reducerPath]: riskAssessmentApi.reducer,
    // Regular slices
    auth: authSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [riskAssessmentApi.util.resetApiState.type],
      },
    }).concat(riskAssessmentApi.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 