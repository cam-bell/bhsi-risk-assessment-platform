import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Stack,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  AlertTriangle,
} from "lucide-react";
import { useGetRiskTrendsQuery } from "../store/api/analyticsApi";

// Simple chart components (in a real app, you'd use a charting library like recharts or chart.js)
const RiskDistributionChart: React.FC<{
  distribution: { green: number; orange: number; red: number };
}> = ({ distribution }) => {
  const total = distribution.green + distribution.orange + distribution.red;
  const greenPercent = total > 0 ? (distribution.green / total) * 100 : 0;
  const orangePercent = total > 0 ? (distribution.orange / total) * 100 : 0;
  const redPercent = total > 0 ? (distribution.red / total) * 100 : 0;

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={2}>
        <Box
          sx={{
            width: "100%",
            height: 20,
            borderRadius: 10,
            overflow: "hidden",
            display: "flex",
          }}
        >
          <Box
            sx={{
              width: `${greenPercent}%`,
              backgroundColor: "#4caf50",
              height: "100%",
            }}
          />
          <Box
            sx={{
              width: `${orangePercent}%`,
              backgroundColor: "#ff9800",
              height: "100%",
            }}
          />
          <Box
            sx={{
              width: `${redPercent}%`,
              backgroundColor: "#f44336",
              height: "100%",
            }}
          />
        </Box>
      </Box>
      <Box display="flex" justifyContent="space-between" fontSize="0.75rem">
        <Box display="flex" alignItems="center">
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#4caf50",
              mr: 0.5,
            }}
          />
          <span>Green: {distribution.green}</span>
        </Box>
        <Box display="flex" alignItems="center">
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#ff9800",
              mr: 0.5,
            }}
          />
          <span>Orange: {distribution.orange}</span>
        </Box>
        <Box display="flex" alignItems="center">
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#f44336",
              mr: 0.5,
            }}
          />
          <span>Red: {distribution.red}</span>
        </Box>
      </Box>
    </Box>
  );
};

const TrendLineChart: React.FC<{
  data: Array<{
    date: string;
    green_count: number;
    orange_count: number;
    red_count: number;
  }>;
}> = ({ data }) => {
  const maxValue = Math.max(
    ...data.flatMap((d) => [d.green_count, d.orange_count, d.red_count])
  );

  return (
    <Box>
      <Box sx={{ height: 200, position: "relative", mb: 2 }}>
        {data.map((point, index) => (
          <Box
            key={index}
            sx={{
              position: "absolute",
              left: `${(index / (data.length - 1)) * 100}%`,
              bottom: 0,
              width: "2px",
              height: `${(point.red_count / maxValue) * 100}%`,
              backgroundColor: "#f44336",
              transform: "translateX(-50%)",
            }}
          />
        ))}
        {data.map((point, index) => (
          <Box
            key={`orange-${index}`}
            sx={{
              position: "absolute",
              left: `${(index / (data.length - 1)) * 100}%`,
              bottom: 0,
              width: "2px",
              height: `${(point.orange_count / maxValue) * 100}%`,
              backgroundColor: "#ff9800",
              transform: "translateX(-50%)",
            }}
          />
        ))}
        {data.map((point, index) => (
          <Box
            key={`green-${index}`}
            sx={{
              position: "absolute",
              left: `${(index / (data.length - 1)) * 100}%`,
              bottom: 0,
              width: "2px",
              height: `${(point.green_count / maxValue) * 100}%`,
              backgroundColor: "#4caf50",
              transform: "translateX(-50%)",
            }}
          />
        ))}
      </Box>
      <Box display="flex" justifyContent="space-between" fontSize="0.75rem">
        <span>{data[0]?.date}</span>
        <span>{data[data.length - 1]?.date}</span>
      </Box>
    </Box>
  );
};

const RiskTrendsPlaceholder = () => (
  <Paper sx={{ p: 4, textAlign: "center", mt: 4 }}>
    <BarChart3 size={48} color="#90caf9" />
    <Typography variant="h5" fontWeight="bold" mt={2}>
      Risk Trends Coming Soon
    </Typography>
    <Typography variant="body1" color="text.secondary" mt={1}>
      Visualize how risk levels change over time and across sectors.
      <br />
      This feature will help you spot trends, outliers, and emerging risks.
    </Typography>
    <Button
      variant="outlined"
      color="primary"
      sx={{ mt: 3 }}
      href="/help/risk-trends"
    >
      Learn More About Risk Trends
    </Button>
    {/* Optionally, show a sample chart */}
    <Box mt={5} width="100%" maxWidth={600} mx="auto">
      <Typography variant="subtitle1" color="text.secondary" align="center">
        Example Risk Trends (Sample Data)
      </Typography>
      {/* Insert a simple static chart or image here */}
      {/* ... */}
    </Box>
  </Paper>
);

const RiskTrendsChart: React.FC = () => {
  const { data, error, isLoading } = useGetRiskTrendsQuery();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading risk trends.</div>;
  if (!data || !data.system_wide_trends) {
    return <RiskTrendsPlaceholder />;
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Risk Trends Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary">
          System-wide risk trends and sector insights
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Overall Risk Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <PieChart size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Overall Risk Distribution</Typography>
              </Box>
              <RiskDistributionChart
                distribution={data.system_wide_trends.overall_risk_distribution}
              />
              <Typography variant="body2" color="text.secondary" mt={2}>
                Total companies analyzed:{" "}
                {data.system_wide_trends.overall_risk_distribution.green +
                  data.system_wide_trends.overall_risk_distribution.orange +
                  data.system_wide_trends.overall_risk_distribution.red}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Trends Over Time */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Activity size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Risk Trends Over Time</Typography>
              </Box>
              <TrendLineChart
                data={data.system_wide_trends.risk_trends_over_time}
              />
              <Box
                display="flex"
                justifyContent="space-between"
                fontSize="0.75rem"
                mt={1}
              >
                <Box display="flex" alignItems="center">
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: "#4caf50",
                      mr: 0.5,
                    }}
                  />
                  <span>Green</span>
                </Box>
                <Box display="flex" alignItems="center">
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: "#ff9800",
                      mr: 0.5,
                    }}
                  />
                  <span>Orange</span>
                </Box>
                <Box display="flex" alignItems="center">
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor: "#f44336",
                      mr: 0.5,
                    }}
                  />
                  <span>Red</span>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Risk Factors */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AlertTriangle size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Top Risk Factors</Typography>
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Risk Factor</TableCell>
                      <TableCell>Frequency</TableCell>
                      <TableCell>Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.system_wide_trends.top_risk_factors.map(
                      (factor, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2">
                              {factor.factor}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {factor.frequency}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`${factor.percentage.toFixed(1)}%`}
                              size="small"
                              variant="outlined"
                              color={
                                factor.percentage > 50
                                  ? "error"
                                  : factor.percentage > 25
                                  ? "warning"
                                  : "default"
                              }
                            />
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

        {/* Sector Insights */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <BarChart3 size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Sector Insights</Typography>
              </Box>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {data.sector_insights.map((sector, index) => (
                  <Box key={index}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={1}
                    >
                      <Typography variant="subtitle2" fontWeight="medium">
                        {sector.sector}
                      </Typography>
                      <Chip
                        label={sector.average_risk.toUpperCase()}
                        size="small"
                        color={
                          sector.average_risk === "red"
                            ? "error"
                            : sector.average_risk === "orange"
                            ? "warning"
                            : "success"
                        }
                        variant="outlined"
                      />
                    </Box>
                    <RiskDistributionChart
                      distribution={sector.risk_distribution}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskTrendsChart;
