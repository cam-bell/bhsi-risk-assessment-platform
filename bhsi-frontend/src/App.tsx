import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AuthProvider } from './auth/AuthProvider';
import { RouterConfig } from './router';
import { theme } from './styles/theme';
import { ErrorBoundary } from './components/ErrorBoundary';
import { NotificationProvider } from './components/NotificationSystem';
import { CompaniesProvider } from './context/CompaniesContext';
import { store } from './store/store';

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <BrowserRouter>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <NotificationProvider>
              <CompaniesProvider>
                <AuthProvider>
                  <RouterConfig />
                </AuthProvider>
              </CompaniesProvider>
            </NotificationProvider>
          </ThemeProvider>
        </BrowserRouter>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;