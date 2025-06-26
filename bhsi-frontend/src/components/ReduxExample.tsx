import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { login, logout } from '../store/slices/authSlice';
import { setNotification, toggleSidebar } from '../store/slices/uiSlice';
import { 
  useSearchCompanyMutation,
  useGetRiskAssessmentMutation,
  type SearchRequest 
} from '../store/api/riskAssessmentApi';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
  Chip,
  LinearProgress
} from '@mui/material';

/**
 * Example component demonstrating Redux usage in the BHSI application
 * This shows how to:
 * 1. Use Redux state with useAppSelector
 * 2. Dispatch actions with useAppDispatch
 * 3. Make API calls with RTK Query mutations
 * 4. Handle loading states and errors
 */
const ReduxExample: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { notifications, sidebarOpen } = useAppSelector((state) => state.ui);
  
  // API hooks
  const [searchCompany, { data: searchResults, isLoading, error }] = useSearchCompanyMutation();
  const [getRiskAssessment] = useGetRiskAssessmentMutation();
  
  // Form state
  const [companyName, setCompanyName] = useState('Banco Santander');
  const [startDate, setStartDate] = useState('2025-06-01');
  const [endDate, setEndDate] = useState('2025-06-13');
  const [daysBack, setDaysBack] = useState(7);
  const [useDateRange, setUseDateRange] = useState(true);
  const [includeBoe, setIncludeBoe] = useState(true);
  const [includeNews, setIncludeNews] = useState(true);

  // Auth actions
  const handleLogin = () => {
    dispatch(login({
      id: '1',
      email: 'john@bhsi.com',
      name: 'John Doe',
      token: 'sample-token-123'
    }));
    dispatch(setNotification({
      id: Date.now().toString(),
      type: 'success',
      message: 'Successfully logged in!',
      duration: 3000
    }));
  };

  const handleLogout = () => {
    dispatch(logout());
    dispatch(setNotification({
      id: Date.now().toString(),
      type: 'info',
      message: 'You have been logged out',
      duration: 3000
    }));
  };

  // Search action using the new API specification
  const handleSearch = async () => {
    if (!companyName.trim()) {
      dispatch(setNotification({
        id: Date.now().toString(),
        type: 'error',
        message: 'Please enter a company name',
        duration: 3000
      }));
      return;
    }

    const searchData: SearchRequest = {
      company_name: companyName,
      include_boe: includeBoe,
      include_news: includeNews,
    };

    // Add date range or days back
    if (useDateRange && startDate && endDate) {
      searchData.start_date = startDate;
      searchData.end_date = endDate;
    } else {
      searchData.days_back = daysBack;
    }

    try {
      await searchCompany(searchData).unwrap();
      dispatch(setNotification({
        id: Date.now().toString(),
        type: 'success',
        message: 'Search completed successfully!',
        duration: 3000
      }));
    } catch (err) {
      dispatch(setNotification({
        id: Date.now().toString(),
        type: 'error',
        message: 'Search failed. Please try again.',
        duration: 3000
      }));
    }
  };

  // Legacy risk assessment (for backward compatibility)
  const handleLegacyRiskAssessment = async () => {
    try {
      await getRiskAssessment({
        companyName,
        dataSource: 'both',
        dateRange: {
          type: useDateRange ? 'custom' : 'preset',
          daysBack: useDateRange ? undefined : daysBack,
          startDate: useDateRange ? startDate : undefined,
          endDate: useDateRange ? endDate : undefined,
        }
      }).unwrap();
    } catch (err) {
      console.error('Legacy risk assessment failed:', err);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    if (riskLevel.toLowerCase().includes('low')) return 'success';
    if (riskLevel.toLowerCase().includes('medium')) return 'warning';
    if (riskLevel.toLowerCase().includes('high')) return 'error';
    return 'default';
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Redux Integration Example - BHSI Search API
      </Typography>

      {/* Authentication Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Authentication State</Typography>
        <Typography>
          Status: {isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
        </Typography>
        {user && (
          <Typography>User: {user.name} ({user.email})</Typography>
        )}
        <Box sx={{ mt: 1 }}>
          {!isAuthenticated ? (
            <Button variant="contained" onClick={handleLogin}>
              Login
            </Button>
          ) : (
            <Button variant="outlined" onClick={handleLogout}>
              Logout
            </Button>
          )}
        </Box>
      </Paper>

      {/* UI State Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>UI State</Typography>
        <Typography>Sidebar: {sidebarOpen ? 'Open' : 'Closed'}</Typography>
        <Typography>Active Notifications: {notifications.length}</Typography>
        <Button 
          variant="outlined" 
          onClick={() => dispatch(toggleSidebar())}
          sx={{ mt: 1 }}
        >
          Toggle Sidebar
        </Button>
      </Paper>

      {/* Company Search Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Company Search (New API)</Typography>
        
        <TextField
          fullWidth
          label="Company Name"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Box sx={{ mb: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={useDateRange}
                onChange={(e) => setUseDateRange(e.target.checked)}
              />
            }
            label="Use specific date range"
          />
        </Box>

        {useDateRange ? (
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              type="date"
              label="Start Date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              type="date"
              label="End Date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        ) : (
          <TextField
            type="number"
            label="Days Back"
            value={daysBack}
            onChange={(e) => setDaysBack(Number(e.target.value))}
            sx={{ mb: 2, width: 200 }}
          />
        )}

        <Box sx={{ mb: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={includeBoe}
                onChange={(e) => setIncludeBoe(e.target.checked)}
              />
            }
            label="Include BOE Results"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={includeNews}
                onChange={(e) => setIncludeNews(e.target.checked)}
              />
            }
            label="Include News Results"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Button 
            variant="contained" 
            onClick={handleSearch}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Search Company'}
          </Button>
          <Button 
            variant="outlined" 
            onClick={handleLegacyRiskAssessment}
          >
            Legacy Risk Assessment
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Search failed: {JSON.stringify(error)}
          </Alert>
        )}
      </Paper>

      {/* Search Results */}
      {searchResults && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Search Results for {searchResults.company_name}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Search performed on: {new Date(searchResults.search_date).toLocaleString()}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Date range: {searchResults.date_range.start || 'N/A'} to {searchResults.date_range.end || 'N/A'} 
            (Days back: {searchResults.date_range.days_back})
          </Typography>

          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            Results ({searchResults.results.length})
          </Typography>

          {searchResults.results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    {result.title}
                  </Typography>
                  <Chip 
                    label={result.source} 
                    color={result.source === 'News' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {new Date(result.date).toLocaleDateString()}
                </Typography>
                
                {result.summary && (
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {result.summary}
                  </Typography>
                )}
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                  <Chip 
                    label={result.risk_level} 
                    color={getRiskLevelColor(result.risk_level)}
                    size="small"
                  />
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 100 }}>
                    <Typography variant="body2">Confidence:</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={result.confidence * 100} 
                      sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2">{Math.round(result.confidence * 100)}%</Typography>
                  </Box>
                </Box>
                
                <Button 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  size="small"
                  variant="text"
                >
                  View Source
                </Button>
              </CardContent>
            </Card>
          ))}
        </Paper>
      )}
    </Box>
  );
};

export default ReduxExample; 