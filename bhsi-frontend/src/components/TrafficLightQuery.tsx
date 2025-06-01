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
  Tabs
} from '@mui/material';
import { Search, Save } from 'lucide-react';
import TrafficLightResult from './TrafficLightResult';
import SavedResults from './SavedResults';
import BatchUpload from './BatchUpload';
import { useAuth } from '../auth/useAuth';

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
    overall: 'orange',
    blocks: {
      turnover: 'green',
      shareholding: 'orange',
      bankruptcy: 'green',
      legal: 'red'
    }
  },
  'TECH': {
    company: 'TechVision Global S.A.',
    vat: 'ESX45678901',
    overall: 'green',
    blocks: {
      turnover: 'green',
      shareholding: 'green',
      bankruptcy: 'green',
      legal: 'green'
    }
  },
  'RISK': {
    company: 'RiskCorp Industries S.A.',
    vat: 'ESX12345678',
    overall: 'red',
    blocks: {
      turnover: 'red',
      shareholding: 'red',
      bankruptcy: 'orange',
      legal: 'red'
    }
  },
  'NOVA': {
    company: 'Nova Enterprises S.A.',
    vat: 'ESX23456789',
    overall: 'orange',
    blocks: {
      turnover: 'orange',
      shareholding: 'green',
      bankruptcy: 'orange',
      legal: 'green'
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
    overall: 'orange',
    blocks: {
      turnover: 'orange',
      shareholding: 'orange',
      bankruptcy: 'green',
      legal: 'orange'
    }
  };
};

const TrafficLightQuery = () => {
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TrafficLightResponse | null>(null);
  const [savedResults, setSavedResults] = useState<SavedResult[]>([]);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Load saved results from localStorage on component mount
  useEffect(() => {
    if (user) {
      const storedResults = localStorage.getItem(`savedResults-${user.email}`);
      if (storedResults) {
        setSavedResults(JSON.parse(storedResults));
      }
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a company name or VAT number');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      const data = getMockResponse(query);
      setResult(data);
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
    localStorage.setItem(`savedResults-${user.email}`, JSON.stringify(updatedResults));
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
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
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
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={isLoading}
                    startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <Search />}
                    sx={{ 
                      minWidth: { xs: '100%', sm: '180px' },
                      height: { xs: '48px', sm: 'auto' }
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

      {/* Saved Results */}
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Saved Results
          </Typography>
          <SavedResults 
            results={savedResults}
            onDelete={handleDeleteResult}
          />
        </CardContent>
      </Card>

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