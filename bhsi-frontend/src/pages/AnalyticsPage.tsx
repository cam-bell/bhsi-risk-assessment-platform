import React, { useState } from "react";
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
  InputAdornment,
  Autocomplete,
  TextField,
} from "@mui/material";
import {
  BarChart3,
  FileText,
  TrendingUp,
  GitCompare,
  Building2,
  Shield,
  Activity,
  Users,
  Search,
} from "lucide-react";
import CompanyAnalyticsDashboard from "../components/CompanyAnalyticsDashboard";
import ManagementSummary from "../components/ManagementSummary";
import RiskTrendsChart from "../components/RiskTrendsChart";
import CompanyComparison from "../components/CompanyComparison";
import CompanySearchBar from "../components/CompanySearchBar";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
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
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleCompanyInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedCompany(e.target.value);
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    setAnalyticsData(null);
    try {
      const response = await fetch(
        `/api/v1/companies/${encodeURIComponent(
          selectedCompany
        )}/analytics?include_trends=true&include_sectors=false`
      );
      if (!response.ok) throw new Error("Failed to fetch analytics");
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const analyticsFeatures = [
    {
      title: "Company Analytics",
      description:
        "Comprehensive risk analysis and insights for individual companies",
      icon: Building2,
      color: "#2196f3",
    },
    {
      title: "Management Summary",
      description:
        "Executive summaries with key risks, financial health, and compliance status",
      icon: FileText,
      color: "#4caf50",
    },
    {
      title: "Risk Trends",
      description:
        "System-wide risk trends, sector insights, and risk factor analysis",
      icon: TrendingUp,
      color: "#ff9800",
    },
    {
      title: "Company Comparison",
      description:
        "Compare risk profiles across multiple companies side by side",
      icon: GitCompare,
      color: "#9c27b0",
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box mb={2}>
        <Typography variant="h3" fontWeight="bold" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive risk analytics and insights for informed decision making
        </Typography>
      </Box>
      {/* Summary Banner */}
      <Box mb={3}>
        <Card sx={{ background: "#f5f7fa", boxShadow: 0 }}>
          <CardContent>
            <Typography variant="subtitle1" color="primary" fontWeight="medium">
              Select a company and explore its analytics, management summary,
              risk trends, and comparisons using the tabs below.
            </Typography>
          </CardContent>
        </Card>
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
          onClick={fetchAnalytics}
          disabled={!selectedCompany.trim() || loading}
        >
          {loading ? "Loading..." : "Load Analytics"}
        </Button>
      </Box>
      {analyticsData && (
        <Card sx={{ mb: 3, background: "#e3f2fd" }}>
          <CardContent sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Avatar sx={{ bgcolor: "primary.main", width: 48, height: 48 }}>
              <Building2 size={28} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="bold">
                {analyticsData.company_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analytics loaded. Explore tabs for more insights.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
      {/* Analytics Tabs */}
      <Paper sx={{ width: "100%" }}>
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
          <Box sx={{ minHeight: 400, p: 2 }}>
            <CompanyAnalyticsDashboard
              analyticsData={analyticsData}
              loading={loading}
              error={error}
              companyName={selectedCompany}
            />
          </Box>
        </TabPanel>
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ minHeight: 400, p: 2 }}>
            <ManagementSummary />
          </Box>
        </TabPanel>
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ minHeight: 400, p: 2 }}>
            <RiskTrendsChart />
          </Box>
        </TabPanel>
        <TabPanel value={activeTab} index={3}>
          <Box sx={{ minHeight: 400, p: 2 }}>
            <CompanyComparison />
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default AnalyticsPage;
