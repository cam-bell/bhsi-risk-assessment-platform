import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Divider,
  Stack,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Info,
} from "lucide-react";
import { useGetCompanyAnalyticsQuery } from "../store/api/analyticsApi";

interface CompanyAnalyticsDashboardProps {
  companyName: string;
  onRefresh?: () => void;
}

const RiskIndicator: React.FC<{ level: "green" | "orange" | "red" }> = ({
  level,
}) => {
  const colors = {
    green: "#4caf50",
    orange: "#ff9800",
    red: "#f44336",
  };

  return (
    <Box
      sx={{
        width: 12,
        height: 12,
        borderRadius: "50%",
        backgroundColor: colors[level],
        display: "inline-block",
        mr: 1,
      }}
    />
  );
};

const TrendIcon: React.FC<{
  trend: "increasing" | "decreasing" | "stable";
}> = ({ trend }) => {
  switch (trend) {
    case "increasing":
      return <TrendingUp size={16} color="#f44336" />;
    case "decreasing":
      return <TrendingDown size={16} color="#4caf50" />;
    case "stable":
      return <Minus size={16} color="#9e9e9e" />;
    default:
      return null;
  }
};

const CompanyAnalyticsDashboard: React.FC<CompanyAnalyticsDashboardProps> = ({
  companyName,
  onRefresh,
}) => {
  const [includeSectors, setIncludeSectors] = useState(false);

  const {
    data: analytics,
    isLoading,
    error,
    refetch,
  } = useGetCompanyAnalyticsQuery({
    company_name: companyName,
    include_trends: true,
    include_sectors: includeSectors,
  });

  const handleRefresh = () => {
    refetch();
    onRefresh?.();
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight={400}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading analytics for {companyName}. Please try again.
      </Alert>
    );
  }

  if (!analytics || !analytics.risk_profile) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        No analytics data available for {companyName}.
      </Alert>
    );
  }

  const historical =
    analytics.trends && analytics.trends.historical_comparison
      ? analytics.trends.historical_comparison
      : {
          current_period: 0,
          previous_period: 0,
          change_percentage: 0,
        };

  const recentEvents = analytics.recent_events || [];

  return (
    <Box>
      {/* Header */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            {analytics.company_name} Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Comprehensive risk analysis and insights
          </Typography>
        </Box>
        <Tooltip title="Refresh analytics">
          <IconButton onClick={handleRefresh} color="primary">
            <RefreshCw />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Risk Profile Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Profile Overview
              </Typography>
              <Stack spacing={2}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Overall Risk</Typography>
                  <Box display="flex" alignItems="center">
                    <RiskIndicator level={analytics.risk_profile.overall} />
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.risk_profile.overall.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Legal Risk</Typography>
                  <Box display="flex" alignItems="center">
                    <RiskIndicator level={analytics.risk_profile.legal} />
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.risk_profile.legal.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Bankruptcy Risk</Typography>
                  <Box display="flex" alignItems="center">
                    <RiskIndicator level={analytics.risk_profile.bankruptcy} />
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.risk_profile.bankruptcy.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Corruption Risk</Typography>
                  <Box display="flex" alignItems="center">
                    <RiskIndicator level={analytics.risk_profile.corruption} />
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.risk_profile.corruption.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Trends
              </Typography>
              <Stack spacing={2}>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Current Trend</Typography>
                  <Box display="flex" alignItems="center">
                    <TrendIcon trend={analytics.trends.risk_trend} />
                    <Typography variant="body2" fontWeight="medium" ml={1}>
                      {analytics.trends.risk_trend.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
                <Box
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Typography variant="body2">Recent Events</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {analytics.trends.recent_events}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Historical Comparison
                  </Typography>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography variant="caption" color="text.secondary">
                      Current: {historical.current_period}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Previous: {historical.previous_period}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.abs(historical.change_percentage)}
                    sx={{
                      mt: 1,
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: "grey.200",
                      "& .MuiLinearProgress-bar": {
                        backgroundColor:
                          historical.change_percentage > 0
                            ? "#f44336"
                            : "#4caf50",
                      },
                    }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    mt={0.5}
                    display="block"
                  >
                    {historical.change_percentage > 0 ? "+" : ""}
                    {historical.change_percentage.toFixed(1)}% change
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Sector Analysis */}
        {analytics.sector_analysis && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sector Analysis
                </Typography>
                <Stack spacing={2}>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography variant="body2">Sector</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.sector_analysis.sector}
                    </Typography>
                  </Box>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography variant="body2">Sector Risk</Typography>
                    <Box display="flex" alignItems="center">
                      <RiskIndicator
                        level={analytics.sector_analysis.sector_risk}
                      />
                      <Typography variant="body2" fontWeight="medium">
                        {analytics.sector_analysis.sector_risk.toUpperCase()}
                      </Typography>
                    </Box>
                  </Box>
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography variant="body2">Company Rank</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {analytics.sector_analysis.company_rank} of{" "}
                      {analytics.sector_analysis.total_companies}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Recent Events */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Events
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Risk Level</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentEvents.map((event, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(event.date).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={event.type}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap>
                            {event.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <RiskIndicator level={event.risk_level} />
                            <Typography variant="body2" fontWeight="medium">
                              {event.risk_level.toUpperCase()}
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              {recentEvents.length === 0 && (
                <Box textAlign="center" py={3}>
                  <Typography variant="body2" color="text.secondary">
                    No recent events found
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CompanyAnalyticsDashboard;
