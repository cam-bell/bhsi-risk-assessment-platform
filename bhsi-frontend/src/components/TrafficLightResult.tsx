import { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Chip, 
  Grid, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Grow,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { type TrafficLightResponse } from './TrafficLightQuery';

interface TrafficLightResultProps {
  result: TrafficLightResponse;
}

// Map color strings to MUI color values
const colorMap = {
  green: 'success',
  orange: 'warning',
  red: 'error',
} as const;

// Map parameters to readable display names
const parameterMap = {
  turnover: 'Financial Turnover',
  shareholding: 'Shareholding Structure',
  bankruptcy: 'Bankruptcy History',
  legal: 'Legal Issues',
} as const;

const TrafficLightResult = ({ result }: TrafficLightResultProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [visible, setVisible] = useState(false);
  
  // Trigger animation after component mounts
  useEffect(() => {
    setVisible(true);
  }, []);

  return (
    <Grow in={visible} timeout={800}>
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
            <Typography variant="h5" component="h3" gutterBottom>
              Risk Assessment Result
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Company:</strong> {result.company}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>VAT:</strong> {result.vat}
              </Typography>
              <Chip
                label={result.overall.toUpperCase()}
                color={colorMap[result.overall]}
                sx={{
                  mt: 3,
                  fontSize: '1.2rem',
                  fontWeight: 'bold',
                  py: 3,
                  px: 2,
                  minWidth: '180px',
                  '& .MuiChip-label': {
                    px: 2,
                  },
                }}
              />
              <Typography variant="body2" sx={{ mt: 2, textAlign: 'center', maxWidth: 500 }}>
                {result.overall === 'green' && 'Low risk profile. Recommended for renewal.'}
                {result.overall === 'orange' && 'Medium risk profile. Recommended for review.'}
                {result.overall === 'red' && 'High risk profile. Recommended for pre-cancellation.'}
              </Typography>
            </Box>
          </Box>

          <Typography variant="h6" component="h4" gutterBottom sx={{ mb: 2 }}>
            Detailed Parameters
          </Typography>

          {isMobile ? (
            // Mobile view - cards
            <Grid container spacing={2}>
              {Object.entries(result.blocks).map(([key, value]) => (
                <Grid item xs={12} key={key}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      borderLeft: `6px solid ${theme.palette[colorMap[value]].main}`,
                      backgroundColor: `${theme.palette[colorMap[value]].light}15`,
                    }}
                  >
                    <Typography variant="subtitle1" component="div" fontWeight={600}>
                      {parameterMap[key as keyof typeof parameterMap]}
                    </Typography>
                    <Chip
                      label={value.toUpperCase()}
                      size="small"
                      color={colorMap[value]}
                      sx={{ mt: 1 }}
                    />
                  </Paper>
                </Grid>
              ))}
            </Grid>
          ) : (
            // Desktop view - table
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: theme.palette.grey[50] }}>
                    <TableCell><strong>Parameter</strong></TableCell>
                    <TableCell><strong>Risk Level</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(result.blocks).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell>{parameterMap[key as keyof typeof parameterMap]}</TableCell>
                      <TableCell>
                        <Chip
                          label={value.toUpperCase()}
                          color={colorMap[value]}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mt: 4, fontStyle: 'italic', textAlign: 'center' }}
          >
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
        </CardContent>
      </Card>
    </Grow>
  );
};

export default TrafficLightResult;