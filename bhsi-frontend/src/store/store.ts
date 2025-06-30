import { configureStore } from "@reduxjs/toolkit";
import { riskAssessmentApi } from "./api/riskAssessmentApi";
import { analyticsApi } from "./api/analyticsApi";
import authSlice from "./slices/authSlice";
import uiSlice from "./slices/uiSlice";

export const store = configureStore({
  reducer: {
    // RTK Query API slices
    [riskAssessmentApi.reducerPath]: riskAssessmentApi.reducer,
    [analyticsApi.reducerPath]: analyticsApi.reducer,
    // Regular slices
    auth: authSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          riskAssessmentApi.util.resetApiState.type,
          analyticsApi.util.resetApiState.type,
        ],
      },
    }).concat(riskAssessmentApi.middleware, analyticsApi.middleware),
  devTools: process.env.NODE_ENV !== "production",
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
