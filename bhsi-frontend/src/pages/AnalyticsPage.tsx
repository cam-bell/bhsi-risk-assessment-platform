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
} from "@mui/material";
import {
  BarChart3,
  FileText,
  TrendingUp,
  GitCompare,
  Building2,
} from "lucide-react";
import ManagementSummary from "../components/ManagementSummary";
import { useLocation } from "react-router-dom";
import CompanyAnalyticsDashboard from "../components/CompanyAnalyticsDashboard";
import RiskTrendsPlaceholder from "../components/RiskTrendsChart";
import BigQueryStatusMonitor from "../components/BigQueryStatusMonitor";

// Placeholder components for tabs
const RiskTrendsChart = () => (
  <Box p={2}>
    <Typography>Risk Trends (Coming soon)</Typography>
  </Box>
);
const CompanyComparison = () => (
  <Box p={2}>
    <Typography>Company Comparison (Coming soon)</Typography>
  </Box>
);

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

const LANGUAGES = [
  { code: "es", label: "Español" },
  { code: "en", label: "English" },
];

const AnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState("es");
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const companyFromUrl = params.get("company") || "";

  // Fetch analytics data on mount if company param exists
  useEffect(() => {
    if (companyFromUrl) {
      setSelectedCompany(companyFromUrl);
      fetchAnalytics(companyFromUrl);
    }
    // eslint-disable-next-line
  }, [companyFromUrl]);

  // Fetch analytics data (simulate /analysis?company=...)
  const fetchAnalytics = async (company: string) => {
    setLoading(true);
    setError(null);
    setAnalyticsData(null);
    try {
      // Replace with your real API endpoint
      const response = await fetch(`/api/v1/analysis/management-summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_name: company, language }),
      });
      if (!response.ok) throw new Error("Failed to fetch analytics");
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
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
      fetchAnalytics(selectedCompany.trim());
    }
  };

  // Sticky language toggle + print/export for ManagementSummary
  const [printAnchor, setPrintAnchor] = useState<HTMLDivElement | null>(null);

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

      {/* BigQuery Status Monitor */}
      <Box mb={3}>
        <BigQueryStatusMonitor showDetails={false} />
      </Box>
      <Box display="flex" gap={2} mb={2}>
        <TextField
          label="Company Name"
          value={selectedCompany}
          onChange={handleCompanyInput}
          fullWidth
        />
        <Button
          variant="contained"
          onClick={handleAnalyze}
          disabled={!selectedCompany.trim() || loading}
        >
          {analyticsData ? "Refresh Analysis" : "Analyze Company"}
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
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
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
          <Tooltip
            title="Executive summaries with key risks, financial health, and compliance status"
            arrow
          >
            <Tab
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <FileText size={16} />
                  Management Summary
                </Box>
              }
            />
          </Tooltip>
          <Tooltip
            title="System-wide risk trends, sector insights, and risk factor analysis"
            arrow
          >
            <Tab
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <TrendingUp size={16} />
                  Risk Trends
                </Box>
              }
            />
          </Tooltip>
          <Tooltip
            title="Compare risk profiles across multiple companies side by side"
            arrow
          >
            <Tab
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <GitCompare size={16} />
                  Company Comparison
                </Box>
              }
            />
          </Tooltip>
        </Tabs>
        <TabPanel value={activeTab} index={0}>
          <CompanyAnalyticsDashboard companyName={selectedCompany} />
        </TabPanel>
        <TabPanel value={activeTab} index={1}>
          {/* Sticky language toggle + print/export */}
          <Box
            sx={{
              position: "sticky",
              top: 0,
              zIndex: 10,
              bgcolor: "background.paper",
              py: 2,
              mb: 2,
              borderBottom: 1,
              borderColor: "divider",
            }}
            ref={setPrintAnchor}
          >
            <Box display="flex" alignItems="center" gap={2}>
              <Tabs
                value={language}
                onChange={(_, val) => setLanguage(val)}
                aria-label="language toggle"
                sx={{ minHeight: 36 }}
              >
                {LANGUAGES.map((lang) => (
                  <Tab
                    key={lang.code}
                    value={lang.code}
                    label={lang.label}
                    sx={{ minWidth: 100 }}
                  />
                ))}
              </Tabs>
              <Button
                variant="outlined"
                onClick={() => window.print()}
                sx={{ ml: 2 }}
              >
                Print / Export
              </Button>
            </Box>
          </Box>
          <ManagementSummary
            companyName={selectedCompany}
            language={language}
            onLanguageChange={setLanguage}
            languages={LANGUAGES}
          />
        </TabPanel>
        <TabPanel value={activeTab} index={2}>
          <RiskTrendsPlaceholder />
        </TabPanel>
        <TabPanel value={activeTab} index={3}>
          <CompanyComparison />
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default AnalyticsPage;
