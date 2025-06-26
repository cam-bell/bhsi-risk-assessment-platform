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

interface SearchSuggestion {
  id: string;
  name: string;
  vat?: string;
  type: 'company' | 'recent';
}

interface SearchSuggestionsProps {
  value: string;
  onChange: (value: string) => void;
  recentSearches: string[];
  onSearch: () => void;
}

const mockSuggestions: SearchSuggestion[] = [
  { id: '1', name: 'ACME Solutions S.A.', vat: 'ESX78901234', type: 'company' },
  { id: '2', name: 'TechVision Global S.A.', vat: 'ESX45678901', type: 'company' },
  { id: '3', name: 'RiskCorp Industries S.A.', vat: 'ESX12345678', type: 'company' },
  { id: '4', name: 'Nova Enterprises S.A.', vat: 'ESX23456789', type: 'company' },
];

const SearchSuggestions = ({ value, onChange, recentSearches, onSearch }: SearchSuggestionsProps) => {
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);

  useEffect(() => {
    if (value.length < 2) {
      const recentSuggestions = recentSearches.slice(0, 3).map((search, index) => ({
        id: `recent-${index}`,
        name: search,
        type: 'recent' as const
      }));
      setSuggestions(recentSuggestions);
      return;
    }

    const filtered = mockSuggestions.filter(
      suggestion =>
        suggestion.name.toLowerCase().includes(value.toLowerCase()) ||
        suggestion.vat?.toLowerCase().includes(value.toLowerCase())
    );
    setSuggestions(filtered);
  }, [value, recentSearches]);

  return (
    <Autocomplete
      freeSolo
      value={value}
      onInputChange={(_: unknown, newValue: string) => onChange(newValue)}
      options={suggestions}
      getOptionLabel={(option: string | SearchSuggestion) => typeof option === 'string' ? option : option.name}
      renderInput={(params: AutocompleteRenderInputParams) => (
        <TextField
          {...params}
          label="Company name or VAT number"
          placeholder="e.g., ACME Solutions or ESX78901234"
          fullWidth
          onKeyPress={(e: React.KeyboardEvent) => {
            if (e.key === 'Enter') {
              onSearch();
            }
          }}
        />
      )}
      renderOption={(props: React.HTMLAttributes<HTMLLIElement>, option: SearchSuggestion) => (
        <Box component="li" {...props}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
            {option.type === 'company' ? (
              <Building2 size={16} style={{ marginRight: 8, color: '#666' }} />
            ) : (
              <FileText size={16} style={{ marginRight: 8, color: '#666' }} />
            )}
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2">{option.name}</Typography>
              {option.vat && (
                <Typography variant="caption" color="text.secondary">
                  {option.vat}
                </Typography>
              )}
            </Box>
            {option.type === 'recent' && (
              <Chip label="Recent" size="small" variant="outlined" />
            )}
          </Box>
        </Box>
      )}
      PaperComponent={(props: React.ComponentProps<typeof Paper>) => (
        <Paper {...props} sx={{ mt: 1, boxShadow: 3 }} />
      )}
      noOptionsText="No companies found"
    />
  );
};

export default SearchSuggestions; 