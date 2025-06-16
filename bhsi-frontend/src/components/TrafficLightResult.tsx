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
  useMediaQuery,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Link,
  LinearProgress
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { ChevronDown, Database, Building, FileText, Scale, ExternalLink, Calendar, TrendingUp } from 'lucide-react';
import { type TrafficLightResponse } from './TrafficLightQuery';

interface TrafficLightResultProps {
  result: TrafficLightResponse;
}

// Mock data sources results
const mockDataSourcesResults = [
  {
    source: "News",
    date: "2025-06-12T05:49:58Z",
    title: "Banco Santander prevé una mayor desaceleración económica en España",
    summary: "El banco español anticipa un crecimiento más lento debido a factores macroeconómicos globales y tensiones geopolíticas.",
    risk_level: "Medium-Economic",
    confidence: 0.8,
    url: "https://expansion.mx/empresas/2025/06/12/santander-desaceleracion-economica"
  },
  {
    source: "BOE",
    date: "2025-06-10T08:30:00Z",
    title: "Resolución de 8 de junio de 2025, sobre empresas en concurso de acreedores",
    summary: "Publicación de empresas que han iniciado procedimientos concursales en el segundo trimestre.",
    risk_level: "High-Legal",
    confidence: 0.95,
    url: "https://boe.es/diario_boe/txt.php?id=BOE-A-2025-9876"
  },
  {
    source: "News",
    date: "2025-06-11T14:22:30Z",
    title: "Nueva regulación afecta al sector tecnológico español",
    summary: null,
    risk_level: "Low-Regulatory",
    confidence: 0.6,
    url: "https://cincodias.elpais.com/mercados/2025-06-11/nueva-regulacion-tecnologia.html"
  },
  {
    source: "BOE",
    date: "2025-06-09T10:15:00Z",
    title: "Real Decreto sobre modificaciones en el régimen fiscal empresarial",
    summary: "Cambios en las deducciones fiscales para empresas del sector industrial y tecnológico.",
    risk_level: "Medium-Tax",
    confidence: 0.9,
    url: "https://boe.es/diario_boe/txt.php?id=BOE-A-2025-9845"
  }
];

// Map color strings to MUI color values
const colorMap = {
  green: 'success',
  orange: 'warning',
  red: 'error',
} as const;

// Map risk levels to colors
const riskLevelColorMap = {
  'Low-Other': 'success',
  'Low-Regulatory': 'success',
  'Medium-Economic': 'warning',
  'Medium-Tax': 'warning',
  'High-Legal': 'error',
  'High-Financial': 'error',
} as const;

// Map parameters to readable display names
const parameterMap = {
  turnover: 'Financial Turnover',
  shareholding: 'Shareholding Structure',
  bankruptcy: 'Bankruptcy History',
  legal: 'Legal Issues',
} as const;

// Map parameters to their data sources
const dataSourcesMap = {
  turnover: {
    primary: 'SABI Bureau van Dijk Database',
    secondary: ['Companies House', 'Annual Reports', 'Financial Statements'],
    icon: <Database size={16} />,
    description: 'Financial performance data sourced from official company filings and commercial databases',
    lastUpdated: '2024-01-15'
  },
  shareholding: {
    primary: 'Companies House Registry',
    secondary: ['PSC Register', 'Shareholding Disclosures', 'Regulatory Filings'],
    icon: <Building size={16} />,
    description: 'Ownership structure verified through official company registrations and regulatory submissions',
    lastUpdated: '2024-01-12'
  },
  bankruptcy: {
    primary: 'Insolvency Service Records',
    secondary: ['Court Records', 'Gazette Notices', 'Credit Reference Agencies'],
    icon: <Scale size={16} />,
    description: 'Insolvency history tracked through official court records and regulatory announcements',
    lastUpdated: '2024-01-10'
  },
  legal: {
    primary: 'UK Court Service',
    secondary: ['Legal Databases', 'Regulatory Actions', 'Public Records'],
    icon: <FileText size={16} />,
    description: 'Legal proceedings monitored through court systems and regulatory enforcement databases',
    lastUpdated: '2024-01-08'
  },
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
              {Object.entries(result.blocks).map(([key, value]) => {
                const sourceInfo = dataSourcesMap[key as keyof typeof dataSourcesMap];
                return (
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
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {sourceInfo.icon}
                        <Typography variant="subtitle1" component="div" fontWeight={600} sx={{ ml: 1 }}>
                          {parameterMap[key as keyof typeof parameterMap]}
                        </Typography>
                      </Box>
                      <Chip
                        label={value.toUpperCase()}
                        size="small"
                        color={colorMap[value]}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary" display="block">
                        <strong>Source:</strong> {sourceInfo.primary}
                      </Typography>
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
          ) : (
            // Desktop view - table
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: theme.palette.grey[50] }}>
                    <TableCell><strong>Parameter</strong></TableCell>
                    <TableCell><strong>Risk Level</strong></TableCell>
                    <TableCell><strong>Primary Data Source</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(result.blocks).map(([key, value]) => {
                    const sourceInfo = dataSourcesMap[key as keyof typeof dataSourcesMap];
                    return (
                      <TableRow key={key}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {sourceInfo.icon}
                            <Typography sx={{ ml: 1 }}>
                              {parameterMap[key as keyof typeof parameterMap]}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={value.toUpperCase()}
                            color={colorMap[value]}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {sourceInfo.primary}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Data Sources Section */}
          <Box sx={{ mt: 4 }}>
            <Accordion>
              <AccordionSummary expandIcon={<ChevronDown />}>
                <Typography variant="h6" component="h4">
                  📊 Data Sources & Methodology
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Recent data sources analyzed for this risk assessment, sorted by date (most recent first).
                </Typography>
                
                <Grid container spacing={2}>
                  {mockDataSourcesResults
                    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                    .map((item, index) => (
                    <Grid item xs={12} key={index}>
                      <Paper 
                        elevation={1} 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          borderLeft: `4px solid ${theme.palette[item.source === 'News' ? 'info' : 'primary'].main}`,
                          '&:hover': {
                            elevation: 2,
                            backgroundColor: theme.palette.grey[50]
                          }
                        }}
                      >
                        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
                          {/* Left Column - Main Info */}
                          <Box sx={{ flex: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <Chip 
                                label={item.source}
                                size="small"
                                color={item.source === 'News' ? 'info' : 'primary'}
                                icon={item.source === 'News' ? <TrendingUp size={14} /> : <FileText size={14} />}
                              />
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Calendar size={14} />
                                <Typography variant="caption" color="text.secondary">
                                  {new Date(item.date).toLocaleDateString()} {new Date(item.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                </Typography>
                              </Box>
                            </Box>
                            
                            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                              {item.title}
                            </Typography>
                            
                            {item.summary && (
                              <Typography variant="body2" color="text.secondary" paragraph>
                                {item.summary}
                              </Typography>
                            )}
                            
                            <Link 
                              href={item.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              sx={{ 
                                display: 'inline-flex', 
                                alignItems: 'center', 
                                gap: 0.5,
                                fontSize: '0.875rem',
                                textDecoration: 'none',
                                '&:hover': { textDecoration: 'underline' }
                              }}
                            >
                              View Source <ExternalLink size={12} />
                            </Link>
                          </Box>
                          
                          {/* Right Column - Risk Metrics */}
                          <Box sx={{ 
                            minWidth: { xs: '100%', md: '200px' },
                            display: 'flex', 
                            flexDirection: 'column',
                            gap: 1.5
                          }}>
                            <Box>
                              <Typography variant="caption" fontWeight={600} gutterBottom display="block">
                                Risk Level
                              </Typography>
                              <Chip
                                label={item.risk_level}
                                size="small"
                                color={riskLevelColorMap[item.risk_level as keyof typeof riskLevelColorMap] || 'default'}
                                sx={{ fontSize: '0.75rem' }}
                              />
                            </Box>
                            
                            <Box>
                              <Typography variant="caption" fontWeight={600} gutterBottom display="block">
                                Confidence Score
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={item.confidence * 100} 
                                  sx={{ 
                                    flex: 1, 
                                    height: 6,
                                    borderRadius: 3,
                                    backgroundColor: theme.palette.grey[200],
                                    '& .MuiLinearProgress-bar': {
                                      borderRadius: 3,
                                      backgroundColor: item.confidence >= 0.7 ? theme.palette.success.main : 
                                                     item.confidence >= 0.5 ? theme.palette.warning.main : 
                                                     theme.palette.error.main
                                    }
                                  }}
                                />
                                <Typography variant="caption" fontWeight={600}>
                                  {(item.confidence * 100).toFixed(0)}%
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
                
                <Divider sx={{ my: 3 }} />
                
                <Box sx={{ bgcolor: theme.palette.info.light + '20', p: 2, borderRadius: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    🔒 Data Quality & Compliance
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    All data sources are GDPR compliant and processed in real-time. News articles are analyzed using 
                    advanced NLP algorithms, while BOE documents undergo structured data extraction. Confidence scores 
                    reflect the reliability and relevance of each source to the company's risk profile.
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>
          </Box>

          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mt: 4, fontStyle: 'italic', textAlign: 'center' }}
          >
            Last updated: {new Date().toLocaleDateString()} • Data refreshed hourly
          </Typography>
        </CardContent>
      </Card>
    </Grow>
  );
};

export default TrafficLightResult;