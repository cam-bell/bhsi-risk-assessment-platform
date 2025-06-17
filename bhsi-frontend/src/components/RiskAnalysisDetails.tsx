import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Building,
  DollarSign,
  Users,
  Scale,
  Download,
  Share,
} from 'lucide-react';

interface RiskFactor {
  category: string;
  score: 'green' | 'orange' | 'red';
  weight: number;
  details: string[];
  recommendation?: string;
}

interface CompanyDetails {
  name: string;
  vat: string;
  industry: string;
  employees: string;
  revenue: string;
  founded: string;
  headquarters: string;
}

interface RiskAnalysisDetailsProps {
  company: CompanyDetails;
  overallRisk: 'green' | 'orange' | 'red';
  riskFactors: RiskFactor[];
  confidence: number;
}

const mockData: RiskAnalysisDetailsProps = {
  company: {
    name: 'TechVision Global S.A.',
    vat: 'ESX45678901',
    industry: 'Software Development',
    employees: '150-200',
    revenue: '€8.5M',
    founded: '2018',
    headquarters: 'Madrid, Spain',
  },
  overallRisk: 'green',
  confidence: 87,
  riskFactors: [
    {
      category: 'Financial Health',
      score: 'green',
      weight: 35,
      details: [
        'Steady revenue growth of 15% year-over-year',
        'Strong cash flow position',
        'Low debt-to-equity ratio (0.3)',
        'Profitable for 3 consecutive years',
      ],
      recommendation: 'Excellent financial position supports low-risk classification',
    },
    {
      category: 'Corporate Structure',
      score: 'green',
      weight: 25,
      details: [
        'Clear ownership structure',
        'No complex holding structures',
        'Transparent board composition',
        'Regular financial reporting',
      ],
    },
    {
      category: 'Legal & Compliance',
      score: 'orange',
      weight: 20,
      details: [
        'Minor regulatory fine in 2022 (€15K)',
        'No ongoing litigation',
        'Compliance framework in place',
        'Regular audits conducted',
      ],
      recommendation: 'Monitor regulatory compliance improvements',
    },
    {
      category: 'Market Position',
      score: 'green',
      weight: 20,
      details: [
        'Market leader in B2B software',
        'Diversified client base',
        'Strong competitive moat',
        'Innovation pipeline active',
      ],
    },
  ],
};

const getRiskColor = (risk: 'green' | 'orange' | 'red') => {
  switch (risk) {
    case 'green': return { color: '#2e7d32', bg: '#e8f5e8' };
    case 'orange': return { color: '#ed6c02', bg: '#fff3e0' };
    case 'red': return { color: '#d32f2f', bg: '#ffebee' };
  }
};

const getRiskIcon = (risk: 'green' | 'orange' | 'red') => {
  switch (risk) {
    case 'green': return <CheckCircle size={20} color="#2e7d32" />;
    case 'orange': return <AlertTriangle size={20} color="#ed6c02" />;
    case 'red': return <XCircle size={20} color="#d32f2f" />;
  }
};

const RiskAnalysisDetails = ({ 
  company, 
  overallRisk, 
  riskFactors, 
  confidence 
}: RiskAnalysisDetailsProps = mockData) => {
  const riskColors = getRiskColor(overallRisk);

  return (
    <Box sx={{ maxWidth: '100%', mx: 'auto', p: 3 }}>
      {/* Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box>
              <Typography variant="h4" gutterBottom>
                {company.name}
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                VAT: {company.vat} • {company.industry}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Download Report">
                <IconButton>
                  <Download size={20} />
                </IconButton>
              </Tooltip>
              <Tooltip title="Share Analysis">
                <IconButton>
                  <Share size={20} />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Overall Risk Assessment */}
          <Box 
            sx={{ 
              p: 3, 
              borderRadius: 2, 
              bgcolor: riskColors.bg,
              border: `2px solid ${riskColors.color}`,
              mb: 3 
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              {getRiskIcon(overallRisk)}
              <Typography variant="h5" sx={{ ml: 2, color: riskColors.color, fontWeight: 'bold' }}>
                {overallRisk.toUpperCase()} RISK
              </Typography>
              <Chip 
                label={`${confidence}% Confidence`} 
                sx={{ ml: 'auto' }}
                color={confidence > 80 ? 'success' : confidence > 60 ? 'warning' : 'error'}
              />
            </Box>
            
            <Typography variant="body1">
              Based on comprehensive analysis of financial health, corporate structure, legal compliance, and market position.
            </Typography>
          </Box>

          {/* Company Info Grid */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Building size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">Founded</Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">{company.founded}</Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Users size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">Employees</Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">{company.employees}</Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DollarSign size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">Revenue</Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">{company.revenue}</Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Scale size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">Headquarters</Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">{company.headquarters}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk Factors Analysis */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Detailed Risk Analysis
      </Typography>

      {riskFactors.map((factor, index) => {
        const factorColors = getRiskColor(factor.score);
        
        return (
          <Accordion key={index} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  {getRiskIcon(factor.score)}
                  <Typography variant="h6" sx={{ ml: 2 }}>
                    {factor.category}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
                    Weight: {factor.weight}%
                  </Typography>
                  <Chip 
                    label={factor.score.toUpperCase()} 
                    size="small"
                    sx={{ 
                      bgcolor: factorColors.bg, 
                      color: factorColors.color,
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
              </Box>
            </AccordionSummary>
            
            <AccordionDetails>
              <Box sx={{ p: 2 }}>
                <List dense>
                  {factor.details.map((detail, detailIndex) => (
                    <ListItem key={detailIndex} sx={{ pl: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Info size={16} color="#666" />
                      </ListItemIcon>
                      <ListItemText primary={detail} />
                    </ListItem>
                  ))}
                </List>
                
                {factor.recommendation && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Recommendation:</strong> {factor.recommendation}
                      </Typography>
                    </Alert>
                  </>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
};

export default RiskAnalysisDetails; 