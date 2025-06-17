import { useState, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent,
  Typography,
  Tooltip,
  Zoom,
  Fab,
  Snackbar,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  ToggleButton,
  ToggleButtonGroup,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { Search, Save, Database, Newspaper, Globe, Calendar, ChevronDown } from 'lucide-react';
import TrafficLightResult from './TrafficLightResult';
import SavedResults from './SavedResults';
import BatchUpload from './BatchUpload';
import { useAuth } from '../auth/useAuth';
import { useCompanies } from '../context/CompaniesContext';

// Type for API response
export interface TrafficLightResponse {
  company: string;
  vat: string;
  overall: 'green' | 'orange' | 'red';
  blocks: {
    turnover: 'green' | 'orange' | 'red';
    shareholding: 'green' | 'orange' | 'red';
    bankruptcy: 'green' | 'orange' | 'red';
    legal: 'green' | 'orange' | 'red';
  };
  dataSource?: 'BOE' | 'NewsAPI' | 'both';
  dateRange?: {
    type: 'preset' | 'custom';
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
}

export interface SavedResult extends TrafficLightResponse {
  savedAt: string;
  savedBy: string;
}

// Test company database
const testCompanies = {
  'ACME': {
    company: 'ACME Solutions S.A.',
    vat: 'ESX78901234',
    overall: 'orange' as 'orange',
    blocks: {
      turnover: 'green' as 'green',
      shareholding: 'orange' as 'orange',
      bankruptcy: 'green' as 'green',
      legal: 'red' as 'red'
    }
  },
  'TECH': {
    company: 'TechVision Global S.A.',
    vat: 'ESX45678901',
    overall: 'green' as 'green',
    blocks: {
      turnover: 'green' as 'green',
      shareholding: 'green' as 'green',
      bankruptcy: 'green' as 'green',
      legal: 'green' as 'green'
    }
  },
  'RISK': {
    company: 'RiskCorp Industries S.A.',
    vat: 'ESX12345678',
    overall: 'red' as 'red',
    blocks: {
      turnover: 'red' as 'red',
      shareholding: 'red' as 'red',
      bankruptcy: 'orange' as 'orange',
      legal: 'red' as 'red'
    }
  },
  'NOVA': {
    company: 'Nova Enterprises S.A.',
    vat: 'ESX23456789',
    overall: 'orange' as 'orange',
    blocks: {
      turnover: 'orange' as 'orange',
      shareholding: 'green' as 'green',
      bankruptcy: 'orange' as 'orange',
      legal: 'green' as 'green'
    }
  }
};

// Mock API response function
const getMockResponse = (query: string): TrafficLightResponse => {
  const upperQuery = query.toUpperCase();
  const matchedCompany = Object.entries(testCompanies).find(([key]) => upperQuery.includes(key));
  
  if (matchedCompany) {
    return matchedCompany[1];
  }

  // Default response for unknown companies
  return {
    company: `${query} S.A.`,
    vat: upperQuery.includes('ESX') ? upperQuery : 'ESX99999999',
    overall: 'orange' as 'orange',
    blocks: {
      turnover: 'orange' as 'orange',
      shareholding: 'orange' as 'orange',
      bankruptcy: 'green' as 'green',
      legal: 'orange' as 'orange'
    }
  };
};

const TrafficLightQuery = () => {
  const { user } = useAuth();
  const { addAssessedCompany } = useCompanies();
  const [query, setQuery] = useState('');
  const [dataSource, setDataSource] = useState<'BOE' | 'NewsAPI' | 'both'>('both');
  const [dateRangeType, setDateRangeType] = useState<'preset' | 'custom'>('preset');
  const [daysBack, setDaysBack] = useState<number>(30);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TrafficLightResponse | null>(null);
  const [savedResults, setSavedResults] = useState<SavedResult[]>([]);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Helper function to format date to YYYY-MM-DD
  const formatDateToYYYYMMDD = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  // Helper function to validate date format
  const isValidDateFormat = (dateString: string): boolean => {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    return dateRegex.test(dateString) && !isNaN(Date.parse(dateString));
  };

  // Load saved results from localStorage on component mount
  useEffect(() => {
    if (user) {
      const storedResults = localStorage.getItem(`savedResults-${user.email}`);
      if (storedResults) {
        setSavedResults(JSON.parse(storedResults));
      }
    }
  }, [user]);

  const handleDataSourceChange = (event: SelectChangeEvent<'BOE' | 'NewsAPI' | 'both'>) => {
    setDataSource(event.target.value as 'BOE' | 'NewsAPI' | 'both');
  };

  const handleDateRangeTypeChange = (
    event: React.MouseEvent<HTMLElement>,
    newType: 'preset' | 'custom'
  ) => {
    if (newType !== null) {
      setDateRangeType(newType);
    }
  };

  const handleDaysBackChange = (event: SelectChangeEvent<number>) => {
    setDaysBack(event.target.value as number);
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Ensure YYYY-MM-DD format
    if (value === '' || isValidDateFormat(value)) {
      setStartDate(value);
    }
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Ensure YYYY-MM-DD format
    if (value === '' || isValidDateFormat(value)) {
      setEndDate(value);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a company name or VAT number');
      return;
    }
    
    // Validate custom date range
    if (dateRangeType === 'custom') {
      if (!startDate || !endDate) {
        setError('Please select both start and end dates for custom range (format: YYYY-MM-DD)');
        return;
      }
      if (!isValidDateFormat(startDate) || !isValidDateFormat(endDate)) {
        setError('Please enter dates in YYYY-MM-DD format');
        return;
      }
      if (new Date(startDate) > new Date(endDate)) {
        setError('Start date must be before end date');
        return;
      }
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      const data = getMockResponse(query);
      
      // Add data source and date range info to result
      const resultWithMetadata: TrafficLightResponse = { 
        ...data, 
        dataSource,
        dateRange: dateRangeType === 'preset' 
          ? { type: 'preset' as const, daysBack }
          : { type: 'custom' as const, startDate, endDate }
      };
      setResult(resultWithMetadata);
      
      // Automatically add to dashboard
      if (user) {
        addAssessedCompany({
          name: data.company,
          vat: data.vat,
          overallRisk: data.overall,
          assessedBy: user.email,
          riskFactors: {
            turnover: data.blocks.turnover,
            shareholding: data.blocks.shareholding,
            bankruptcy: data.blocks.bankruptcy,
            legal: data.blocks.legal,
          }
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = () => {
    if (result && user) {
      const savedResult: SavedResult = {
        ...result,
        savedAt: new Date().toISOString(),
        savedBy: user.email
      };
      const newSavedResults = [savedResult, ...savedResults];
      setSavedResults(newSavedResults);
      localStorage.setItem(`savedResults-${user.email}`, JSON.stringify(newSavedResults));
      setResult(null);
      setShowSaveSuccess(true);
    }
  };

  const handleSaveBatchResults = (newResults: SavedResult[]) => {
    const updatedResults = [...newResults, ...savedResults];
    setSavedResults(updatedResults);
    if (user) {
      localStorage.setItem(`savedResults-${user.email}`, JSON.stringify(updatedResults));
    }
    setShowSaveSuccess(true);
  };

  const handleDeleteResult = (resultToDelete: SavedResult) => {
    const updatedResults = savedResults.filter(result => 
      !(result.company === resultToDelete.company && 
        result.savedAt === resultToDelete.savedAt && 
        result.savedBy === resultToDelete.savedBy)
    );
    setSavedResults(updatedResults);
    if (user) {
      localStorage.setItem(`savedResults-${user.email}`, JSON.stringify(updatedResults));
    }
  };
  
  return (
    <Box>
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{ mb: 3 }}
          >
            <Tab label="Single Search" />
            <Tab label="Batch Upload" />
          </Tabs>

          {activeTab === 0 ? (
            <>
              <Typography variant="h6" gutterBottom>
                Enter Company Details
              </Typography>
              <form onSubmit={handleSubmit}>
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: { xs: 'stretch', sm: 'flex-end' }, mb: 2 }}>
                  <TextField
                    label="Company Name or VAT Number"
                    variant="outlined"
                    fullWidth
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Try: ACME, TECH, RISK, or NOVA"
                    disabled={isLoading}
                    InputProps={{
                      sx: { borderRadius: 2 }
                    }}
                    sx={{ flex: 1 }}
                  />
                  <FormControl sx={{ minWidth: { xs: '100%', sm: '200px' } }}>
                    <InputLabel>Data Source</InputLabel>
                    <Select
                      value={dataSource}
                      label="Data Source"
                      onChange={handleDataSourceChange}
                      disabled={isLoading}
                      sx={{ borderRadius: 2 }}
                    >
                      <MenuItem value="BOE">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Database size={16} />
                          BOE (Boletín Oficial del Estado)
                        </Box>
                      </MenuItem>
                      <MenuItem value="NewsAPI">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Newspaper size={16} />
                          NewsAPI
                        </Box>
                      </MenuItem>
                      <MenuItem value="both">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Globe size={16} />
                          Both Sources
                        </Box>
                      </MenuItem>
                    </Select>
                  </FormControl>
                </Box>

                {/* Date Range Section */}
                <Accordion sx={{ mb: 2, borderRadius: 2, '&:before': { display: 'none' } }}>
                  <AccordionSummary 
                    expandIcon={<ChevronDown />}
                    sx={{ 
                      borderRadius: 2,
                      '& .MuiAccordionSummary-content': { alignItems: 'center' }
                    }}
                  >
                    <Calendar size={18} style={{ marginRight: 8 }} />
                    <Typography variant="subtitle2">
                      Date Range
                    </Typography>
                    <Typography variant="caption" sx={{ ml: 2, color: 'text.secondary' }}>
                      {dateRangeType === 'preset' 
                        ? `Last ${daysBack} days`
                        : startDate && endDate 
                          ? `${startDate} to ${endDate}`
                          : 'Custom range'
                      }
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <ToggleButtonGroup
                        value={dateRangeType}
                        exclusive
                        onChange={handleDateRangeTypeChange}
                        size="small"
                        sx={{ mb: 2 }}
                      >
                        <ToggleButton value="preset">Quick Select</ToggleButton>
                        <ToggleButton value="custom">Custom Range</ToggleButton>
                      </ToggleButtonGroup>

                      {dateRangeType === 'preset' ? (
                        <FormControl sx={{ maxWidth: 300 }}>
                          <InputLabel>Period</InputLabel>
                          <Select
                            value={daysBack}
                            label="Period"
                            onChange={handleDaysBackChange}
                            disabled={isLoading}
                          >
                            <MenuItem value={7}>Last 7 days</MenuItem>
                            <MenuItem value={14}>Last 2 weeks</MenuItem>
                            <MenuItem value={30}>Last 30 days</MenuItem>
                            <MenuItem value={60}>Last 2 months</MenuItem>
                            <MenuItem value={90}>Last 3 months</MenuItem>
                            <MenuItem value={180}>Last 6 months</MenuItem>
                            <MenuItem value={365}>Last year</MenuItem>
                          </Select>
                        </FormControl>
                      ) : (
                        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
                          <TextField
                            label="Start Date"
                            type="date"
                            value={startDate}
                            onChange={handleStartDateChange}
                            disabled={isLoading}
                            placeholder="YYYY-MM-DD"
                            InputLabelProps={{
                              shrink: true,
                            }}
                            helperText="Format: YYYY-MM-DD (e.g., 2025-06-01)"
                            sx={{ flex: 1 }}
                          />
                          <TextField
                            label="End Date"
                            type="date"
                            value={endDate}
                            onChange={handleEndDateChange}
                            disabled={isLoading}
                            placeholder="YYYY-MM-DD"
                            InputLabelProps={{
                              shrink: true,
                            }}
                            helperText="Format: YYYY-MM-DD (e.g., 2025-06-13)"
                            sx={{ flex: 1 }}
                          />
                        </Box>
                      )}

                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                        💡 <strong>Tip:</strong> Date range primarily affects NewsAPI results. 
                        BOE data is typically current and less time-sensitive.
                      </Typography>
                    </Box>
                  </AccordionDetails>
                </Accordion>

                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={isLoading}
                    startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <Search />}
                    sx={{ 
                      minWidth: '200px',
                      height: '56px',
                      fontSize: '1.1rem',
                      fontWeight: 600
                    }}
                  >
                    {isLoading ? 'Searching...' : 'Get Score'}
                  </Button>
                </Box>
              </form>
              
              {error && (
                <Alert severity="error" sx={{ mt: 3 }}>
                  {error}
                </Alert>
              )}
            </>
          ) : (
            <BatchUpload
              onSaveResults={handleSaveBatchResults}
              getMockResponse={getMockResponse}
            />
          )}
        </CardContent>
      </Card>

      {/* Current Result Display */}
      {result && (
        <Card sx={{ mb: 4, position: 'relative' }}>
          <CardContent>
            <TrafficLightResult result={result} />
            <Zoom in={true}>
              <Fab
                color="primary"
                onClick={handleSave}
                sx={{
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  boxShadow: theme => `0 4px 14px ${theme.palette.primary.main}40`,
                  '&:hover': {
                    transform: 'scale(1.05)',
                  }
                }}
              >
                <Tooltip title="Save Result" placement="left">
                  <Save />
                </Tooltip>
              </Fab>
            </Zoom>
          </CardContent>
        </Card>
      )}



      {/* Success Snackbar */}
      <Snackbar
        open={showSaveSuccess}
        autoHideDuration={3000}
        onClose={() => setShowSaveSuccess(false)}
        message="Result saved successfully"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default TrafficLightQuery;