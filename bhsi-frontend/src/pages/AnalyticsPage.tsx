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
} from "lucide-react";
import CompanyAnalyticsDashboard from "../components/CompanyAnalyticsDashboard";
import ManagementSummary from "../components/ManagementSummary";
import RiskTrendsChart from "../components/RiskTrendsChart";
import CompanyComparison from "../components/CompanyComparison";

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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
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
      <Box mb={4}>
        <Typography variant="h3" fontWeight="bold" gutterBottom>
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive risk analytics and insights for informed decision making
        </Typography>
      </Box>

      {/* Feature Overview Cards */}
      <Grid container spacing={3} mb={4}>
        {analyticsFeatures.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: "100%",
                  cursor: "pointer",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: 3,
                  },
                }}
                onClick={() => setActiveTab(index)}
              >
                <CardContent sx={{ textAlign: "center", py: 3 }}>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: "50%",
                      backgroundColor: `${feature.color}20`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mx: "auto",
                      mb: 2,
                    }}
                  >
                    <Icon size={28} color={feature.color} />
                  </Box>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Company Selection for Company-specific Analytics */}
      {(activeTab === 0 || activeTab === 1) && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Select Company
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
              <input
                type="text"
                placeholder="Enter company name (e.g., 'Banco Santander')"
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                style={{
                  flex: 1,
                  padding: "12px 16px",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  fontSize: "14px",
                }}
              />
              <Button
                variant="contained"
                disabled={!selectedCompany.trim()}
                onClick={() => {}}
              >
                Load Analytics
              </Button>
            </Box>
            {!selectedCompany && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Enter a company name to view its analytics and management
                summary
              </Alert>
            )}
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
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <Building2 size={16} />
                Company Analytics
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <FileText size={16} />
                Management Summary
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <TrendingUp size={16} />
                Risk Trends
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <GitCompare size={16} />
                Company Comparison
              </Box>
            }
          />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          {selectedCompany ? (
            <CompanyAnalyticsDashboard companyName={selectedCompany} />
          ) : (
            <Box textAlign="center" py={4}>
              <Building2
                size={48}
                color="#9e9e9e"
                style={{ marginBottom: 16 }}
              />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Select a Company
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter a company name above to view its comprehensive analytics
              </Typography>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {selectedCompany ? (
            <ManagementSummary companyName={selectedCompany} />
          ) : (
            <Box textAlign="center" py={4}>
              <FileText
                size={48}
                color="#9e9e9e"
                style={{ marginBottom: 16 }}
              />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Select a Company
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter a company name above to view its management summary
              </Typography>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <RiskTrendsChart />
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <CompanyComparison />
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default AnalyticsPage;
