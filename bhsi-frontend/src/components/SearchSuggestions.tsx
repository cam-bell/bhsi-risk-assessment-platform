import React, { useState, useEffect } from 'react';
import {
  Box,
  Autocomplete,
  TextField,
  Paper,
  Typography,
  Chip,
  AutocompleteRenderInputParams,
} from '@mui/material';
import { Building2, FileText } from 'lucide-react';

interface Suggestion {
  id: string;
  name: string;
  type: 'company' | 'sector' | 'location';
}

const defaultSuggestions: Suggestion[] = [
  { id: '1', name: 'ACME Solutions S.A.', type: 'company' },
  { id: '2', name: 'TechVision Global S.A.', type: 'company' },
  { id: '3', name: 'RiskCorp Industries S.A.', type: 'company' },
  { id: '4', name: 'Nova Enterprises S.A.', type: 'company' },
  { id: '5', name: 'Banking Sector', type: 'sector' },
  { id: '6', name: 'Technology Sector', type: 'sector' },
  { id: '7', name: 'Energy Sector', type: 'sector' },
  { id: '8', name: 'Madrid Region', type: 'location' },
  { id: '9', name: 'Catalonia Region', type: 'location' },
  { id: '10', name: 'Basque Country', type: 'location' },
];

interface SearchSuggestionsProps {
  onSuggestionSelect?: (suggestion: string) => void;
}

const SearchSuggestions: React.FC<SearchSuggestionsProps> = ({ onSuggestionSelect }) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>(defaultSuggestions);

  const getSuggestions = (value: string) => {
    const inputValue = value.trim().toLowerCase();
    const inputLength = inputValue.length;
    
    return inputLength === 0 
      ? defaultSuggestions
      : suggestions.filter(suggestion => 
          suggestion.name.toLowerCase().includes(value.toLowerCase())
        );
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 400 }}>
      <Autocomplete
        options={getSuggestions('')}
        getOptionLabel={(option) => option.name}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Company name"
            variant="outlined"
            size="small"
          />
        )}
        renderOption={(props, option) => (
          <Box component="li" {...props}>
            <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
              <Typography variant="body2">
                {option.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {option.type.charAt(0).toUpperCase() + option.type.slice(1)}
              </Typography>
            </Box>
          </Box>
        )}
        onChange={(_, newValue) => {
          if (newValue && onSuggestionSelect) {
            onSuggestionSelect(newValue.name);
          }
        }}
        filterOptions={(options, { inputValue }) => getSuggestions(inputValue)}
      />
    </Box>
  );
};

export default SearchSuggestions; 