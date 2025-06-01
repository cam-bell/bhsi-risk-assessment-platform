import { 
  Box, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  IconButton,
  useTheme,
  useMediaQuery,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  Slide
} from '@mui/material';
import { Search, Eye, X, Trash2 } from 'lucide-react';
import { useState } from 'react';
import type { SavedResult } from './TrafficLightQuery';
import TrafficLightResult from './TrafficLightResult';
import { useAuth } from '../auth/useAuth';

interface SavedResultsProps {
  results: SavedResult[];
  onDelete?: (result: SavedResult) => void;
}

const colorMap = {
  green: 'success',
  orange: 'warning',
  red: 'error',
} as const;

const SavedResults = ({ results, onDelete }: SavedResultsProps) => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedResult, setSelectedResult] = useState<SavedResult | null>(null);
  const [deleteConfirmResult, setDeleteConfirmResult] = useState<SavedResult | null>(null);
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  // Filter results by search term and current user
  const filteredResults = results.filter(result => 
    result.savedBy === user?.email && // Only show results for current user
    (result.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.vat.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleViewResult = (result: SavedResult) => {
    setSelectedResult(result);
  };

  const handleCloseDialog = () => {
    setSelectedResult(null);
  };

  const handleDeleteClick = (result: SavedResult) => {
    setDeleteConfirmResult(result);
  };

  const handleConfirmDelete = () => {
    if (deleteConfirmResult && onDelete) {
      onDelete(deleteConfirmResult);
      setDeleteConfirmResult(null);
      // Show success message
      const alert = document.createElement('div');
      alert.style.position = 'fixed';
      alert.style.bottom = '1rem';
      alert.style.left = '50%';
      alert.style.transform = 'translateX(-50%)';
      alert.style.zIndex = '9999';
      document.body.appendChild(alert);
    }
  };

  return (
    <Box>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search saved results..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search size={20} />
            </InputAdornment>
          ),
        }}
      />

      {filteredResults.length === 0 ? (
        <Typography variant="body1" color="text.secondary" textAlign="center" py={4}>
          No saved results found
        </Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Company</strong></TableCell>
                <TableCell><strong>VAT</strong></TableCell>
                <TableCell><strong>Risk Level</strong></TableCell>
                <TableCell><strong>Saved Date</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredResults.map((result, index) => (
                <TableRow 
                  key={index}
                  sx={{ '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' } }}
                >
                  <TableCell>{result.company}</TableCell>
                  <TableCell>{result.vat}</TableCell>
                  <TableCell>
                    <Chip
                      label={result.overall.toUpperCase()}
                      color={colorMap[result.overall]}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(result.savedAt).toLocaleDateString()} {new Date(result.savedAt).toLocaleTimeString()}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        onClick={() => handleViewResult(result)}
                        size="small"
                        color="primary"
                        title="View Details"
                      >
                        <Eye size={20} />
                      </IconButton>
                      <IconButton
                        onClick={() => handleDeleteClick(result)}
                        size="small"
                        color="error"
                        title="Delete Result"
                      >
                        <Trash2 size={20} />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* View Details Dialog */}
      <Dialog
        fullScreen={fullScreen}
        maxWidth="md"
        fullWidth
        open={Boolean(selectedResult)}
        onClose={handleCloseDialog}
        TransitionComponent={Slide}
      >
        {selectedResult && (
          <>
            <DialogTitle sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              pb: 1
            }}>
              Risk Assessment Details
              <IconButton
                edge="end"
                color="inherit"
                onClick={handleCloseDialog}
                aria-label="close"
                size="small"
              >
                <X size={20} />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Saved on: {new Date(selectedResult.savedAt).toLocaleString()}
              </Typography>
              <TrafficLightResult result={selectedResult} />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog} variant="contained">
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={Boolean(deleteConfirmResult)}
        onClose={() => setDeleteConfirmResult(null)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Are you sure you want to delete the result for {deleteConfirmResult?.company}? This action cannot be undone.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmResult(null)}>
            Cancel
          </Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SavedResults;