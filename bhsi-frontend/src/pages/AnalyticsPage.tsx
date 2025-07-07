import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Tabs,
  Tab,
  Paper,
  Alert,
  Tooltip,
  Avatar,
  CircularProgress,
  TextField,
  Container,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from "@mui/material";
import {
  BarChart3,
  FileText,
  TrendingUp,
  GitCompare,
  Building2,
  AlertTriangle,
  Users,
  Calendar,
  Globe,
  Activity,
  PieChart,
  Target,
  Shield,
  TrendingDown,
  TrendingUp as TrendingUpIcon,
  Bot,
} from "lucide-react";
import ManagementSummary from "../components/ManagementSummary";
import { useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import axios from "axios";
import RAGChatbot from "../components/RAGChatbot";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface CompanyAnalytics {
  company_name: string;
  vat_number?: string;
  sector?: string;
  total_events: number;
  risk_distribution: {
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  latest_events: Array<{
    event_id: string;
    title: string;
    risk_label: string;
    pub_date: string;
    url: string;
    source: string;
    rationale: string;
    alerted: boolean;
  }>;
  alert_summary: {
    total_alerts: number;
    high_risk_events: number;
    last_alert?: string;
  };
  assessment?: {
    turnover: string;
    shareholding: string;
    bankruptcy: string;
    legal: string;
    corruption: string;
    overall: string;
    summary: string;
    last_updated?: string;
  };
}

interface SystemAnalytics {
  trends: Array<{
    date: string;
    risk_label: string;
    count: number;
    alerts_triggered: number;
  }>;
  alerts: {
    total_alerts: number;
    high_risk_alerts: number;
    last_alert?: string;
  };
  sectors: Array<{
    sector: string;
    total_companies: number;
    total_events: number;
    high_risk_events: number;
    alerts_triggered: number;
  }>;
}

interface RiskComparison {
  companies: CompanyAnalytics[];
  comparison: {
    highest_risk: string;
    most_alerts: string;
    riskiest_sector: string;
  };
}

function TabPanel(props: {
  children?: React.ReactNode;
  index: number;
  value: number;
}) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const AnalyticsPage: React.FC = () => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [companyAnalytics, setCompanyAnalytics] =
    useState<CompanyAnalytics | null>(null);
  const [systemAnalytics, setSystemAnalytics] =
    useState<SystemAnalytics | null>(null);
  const [riskComparison, setRiskComparison] = useState<RiskComparison | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparisonCompanies, setComparisonCompanies] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<'date_desc' | 'date_asc'>('date_desc');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');

  // Extract unique risk labels for filter options
  const riskLabelOptions = React.useMemo(() => {
    const labels = new Set<string>();
    (companyAnalytics?.latest_events || []).forEach(e => {
      if (e.risk_label) labels.add(e.risk_label);
    });
    return Array.from(labels).sort();
  }, [companyAnalytics]);

  const riskFilterOptions = [
    { value: 'ALL', label: 'All' },
    { value: 'NO', label: 'No' },
    { value: 'LOW', label: 'Low' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'HIGH', label: 'High' },
  ];

  // Fetch system analytics on mount
  useEffect(() => {
    fetchSystemAnalytics();
  }, []);

  const fetchCompanyAnalytics = async (company: string) => {
    setLoading(true);
    setError(null);
    try {
      // Use the new merged search endpoint
      const response = await axios.get(
        `${API_BASE_URL}/streamlined/search/merged/${encodeURIComponent(company)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      // Map the merged response to the CompanyAnalytics interface for display
      const data = response.data;
      // Compute risk distribution from results
      const riskDistribution = { HIGH: 0, MEDIUM: 0, LOW: 0 };
      (data.results || []).forEach((event: any) => {
        if (event.risk_color === 'red') riskDistribution.HIGH += 1;
        else if (event.risk_color === 'orange') riskDistribution.MEDIUM += 1;
        else if (event.risk_color === 'green') riskDistribution.LOW += 1;
      });
      setCompanyAnalytics({
        company_name: data.company_name,
        vat_number: undefined, // Not available in merged response
        sector: undefined, // Not available in merged response
        total_events: data.total_results || (data.metadata?.total_results ?? 0),
        risk_distribution: riskDistribution,
        latest_events: (data.results || []).map((event: any, idx: number) => ({
          event_id: event.url || idx, // Use URL as unique ID fallback
          title: event.title || '',
          risk_label: event.risk_level || event.risk_color || 'Unknown',
          pub_date: event.date || '',
          url: event.url || '',
          source: event.source || '',
          rationale: event.url || '', // Store the link instead of the summary
          alerted: false, // Not available in merged response
        })),
        alert_summary: {
          total_alerts: data.metadata?.high_risk_results || 0,
          high_risk_events: data.metadata?.high_risk_results || 0,
          last_alert: undefined,
        },
        assessment: undefined, // Not available in merged response
      });
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to fetch company analytics"
      );
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemAnalytics = async () => {
    try {
      const [trendsResponse, alertsResponse, sectorsResponse] =
        await Promise.all([
          axios.get(`${API_BASE_URL}/companies/analytics/trends`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          axios.get(`${API_BASE_URL}/companies/analytics/alerts`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          axios.get(`${API_BASE_URL}/companies/analytics/sectors`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

      setSystemAnalytics({
        trends: trendsResponse.data.trends || [],
        alerts: alertsResponse.data,
        sectors: sectorsResponse.data.sectors || [],
      });
    } catch (err: any) {
      console.error("Failed to fetch system analytics:", err);
    }
  };

  const fetchRiskComparison = async (companies: string[]) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/companies/analytics/comparison?companies=${companies.join(
          ","
        )}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setRiskComparison(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch risk comparison");
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCompanyInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedCompany(e.target.value);
  };

  const handleAnalyze = () => {
    if (selectedCompany.trim()) {
      fetchCompanyAnalytics(selectedCompany.trim());
    }
  };

  const handleCompare = () => {
    const companies = comparisonCompanies
      .split(",")
      .map((c) => c.trim())
      .filter((c) => c);
    if (companies.length >= 2) {
      fetchRiskComparison(companies);
    } else {
      setError("Please enter at least 2 companies separated by commas");
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toUpperCase()) {
      case "HIGH":
      case "RED":
        return "error";
      case "MEDIUM":
      case "ORANGE":
        return "warning";
      case "LOW":
      case "GREEN":
        return "success";
      default:
        return "default";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  // Helper to sort events
  const sortEvents = (events: any[]) => {
    if (sortOrder === 'date_desc') {
      return [...events].sort((a, b) => new Date(b.pub_date).getTime() - new Date(a.pub_date).getTime());
    } else if (sortOrder === 'date_asc') {
      return [...events].sort((a, b) => new Date(a.pub_date).getTime() - new Date(b.pub_date).getTime());
    }
    return events;
  };

  // Helper to filter and sort events
  const filterAndSortEvents = (events: any[]) => {
    let filtered = events;
    if (riskFilter !== 'ALL') {
      filtered = events.filter(e =>
        (e.risk_label || '').toLowerCase().includes(riskFilter.toLowerCase())
      );
    }
    return sortEvents(filtered);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={2}>
        <Typography variant="h3" fontWeight="bold" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive risk analytics and insights for informed decision making
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs Layout */}
      <Paper sx={{ width: "100%", mt: 2 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="analytics tabs"
          sx={{ borderBottom: 1, borderColor: "divider" }}
        >
          <Tooltip
            title="Intelligent risk analysis engine for natural language queries and insights"
            arrow
          >
            <Tab
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <Bot size={16} />
                  Risk Intelligence Engine
                </Box>
              }
            />
          </Tooltip>
          <Tooltip
            title="Comprehensive risk analysis and insights for individual companies"
            arrow
          >
            <Tab
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <Building2 size={16} />
                  Company Analytics
                </Box>
              }
            />
          </Tooltip>
        </Tabs>

        {/* Risk Intelligence Engine Tab */}
        <TabPanel value={activeTab} index={0}>
          <RAGChatbot />
        </TabPanel>

        {/* Company Analytics Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box p={2} borderRadius={2} bgcolor="background.paper" boxShadow={1}>
            {/* Company Analytics Content */}
            <Box display="flex" gap={2} mb={3}>
              <TextField
                label="Company Name"
                value={selectedCompany}
                onChange={handleCompanyInput}
                fullWidth
                placeholder="Enter company name (e.g., Banco Santander, Repsol)"
              />
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={!selectedCompany.trim() || loading}
              >
                {companyAnalytics ? "Refresh Analysis" : "Analyze Company"}
              </Button>
            </Box>

            {loading && (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight={200}
              >
                <CircularProgress />
              </Box>
            )}

            {companyAnalytics && (
              <Grid container spacing={3}>
                {/* Company Overview */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Company Overview
                      </Typography>
                      <Box display="flex" alignItems="center" gap={2} mb={2}>
                        <Avatar sx={{ bgcolor: "primary.main" }}>
                          <Building2 size={20} />
                        </Avatar>
                        <Box>
                          <Typography variant="h6">
                            {companyAnalytics.company_name}
                          </Typography>
                          {companyAnalytics.vat_number && (
                            <Typography variant="body2" color="text.secondary">
                              VAT: {companyAnalytics.vat_number}
                            </Typography>
                          )}
                          {companyAnalytics.sector && (
                            <Typography variant="body2" color="text.secondary">
                              Sector: {companyAnalytics.sector}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                      <Box display="flex" gap={2}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="primary">
                            {companyAnalytics.total_events ?? 0}
                          </Typography>
                          <Typography variant="body2">Total Events</Typography>
                        </Box>
                        <Box textAlign="center">
                          <Typography variant="h4" color="error">
                            {companyAnalytics.alert_summary?.total_alerts ?? 0}
                          </Typography>
                          <Typography variant="body2">Alerts</Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Risk Distribution */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Risk Distribution
                      </Typography>
                      <Box display="flex" flexDirection="column" gap={1}>
                        {Object.entries(
                          companyAnalytics.risk_distribution || {}
                        ).map(([risk, count]) => (
                          <Box
                            key={risk}
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                          >
                            <Chip
                              label={risk}
                              color={getRiskColor(risk) as any}
                              size="small"
                            />
                            <Typography variant="h6">{count}</Typography>
                          </Box>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Assessment */}
                {companyAnalytics.assessment && (
                  <Grid item xs={12}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Risk Assessment
                        </Typography>
                        <Grid container spacing={2}>
                          {Object.entries(companyAnalytics.assessment || {}).map(
                            ([key, value]) => {
                              if (key === "summary" || key === "last_updated")
                                return null;
                              return (
                                <Grid item xs={6} md={3} key={key}>
                                  <Box textAlign="center">
                                    <Chip
                                      label={key.toUpperCase()}
                                      color={getRiskColor(value) as any}
                                      size="small"
                                      sx={{ mb: 1 }}
                                    />
                                    <Typography
                                      variant="h6"
                                      color={getRiskColor(value) as any}
                                    >
                                      {value}
                                    </Typography>
                                  </Box>
                                </Grid>
                              );
                            }
                          )}
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* Latest Events */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Typography variant="h6" gutterBottom>
                          Latest Events
                        </Typography>
                        <Box display="flex" gap={2}>
                          <FormControl size="small" sx={{ minWidth: 140 }}>
                            <InputLabel id="risk-filter-label">Risk Level</InputLabel>
                            <Select
                              labelId="risk-filter-label"
                              value={riskFilter}
                              label="Risk Level"
                              onChange={(e) => setRiskFilter(e.target.value)}
                            >
                              {riskFilterOptions.map(opt => (
                                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                          <FormControl size="small" sx={{ minWidth: 180 }}>
                            <InputLabel id="sort-order-label">Sort By</InputLabel>
                            <Select
                              labelId="sort-order-label"
                              value={sortOrder}
                              label="Sort By"
                              onChange={(e) => setSortOrder(e.target.value as 'date_desc' | 'date_asc')}
                            >
                              <MenuItem value="date_desc">Date (Newest First)</MenuItem>
                              <MenuItem value="date_asc">Date (Oldest First)</MenuItem>
                            </Select>
                          </FormControl>
                        </Box>
                      </Box>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Event</TableCell>
                              <TableCell>Risk Level</TableCell>
                              <TableCell>Source</TableCell>
                              <TableCell>Date</TableCell>
                              <TableCell>Alerted</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {filterAndSortEvents(companyAnalytics.latest_events || []).map(
                              (event) => (
                                <TableRow key={event.event_id}>
                                  <TableCell>
                                    <Typography variant="body2" fontWeight={500}>
                                      {event.title}
                                    </Typography>
                                    {event.rationale && (
                                      <Typography variant="caption" color="text.secondary">
                                        <a href={event.rationale} target="_blank" rel="noopener noreferrer">
                                          {event.rationale}
                                        </a>
                                      </Typography>
                                    )}
                                  </TableCell>
                                  <TableCell>
                                    <Chip
                                      label={event.risk_label}
                                      color={getRiskColor(event.risk_label) as any}
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell>{event.source}</TableCell>
                                  <TableCell>
                                    {formatDate(event.pub_date)}
                                  </TableCell>
                                  <TableCell>
                                    {event.alerted ? (
                                      <Chip
                                        label="Yes"
                                        color="error"
                                        size="small"
                                      />
                                    ) : (
                                      <Chip
                                        label="No"
                                        color="default"
                                        size="small"
                                      />
                                    )}
                                  </TableCell>
                                </TableRow>
                              )
                            )}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default AnalyticsPage;
