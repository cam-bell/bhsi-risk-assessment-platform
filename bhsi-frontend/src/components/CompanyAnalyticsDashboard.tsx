import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  Avatar,
  Alert,
  Divider,
} from "@mui/material";
// @ts-ignore: If recharts types are missing, ignore for now
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from "recharts";
import { AlertTriangle, CheckCircle, XCircle, Info } from "lucide-react";
import type { ReactElement } from "react";

const RISK_COLORS: Record<string, string> = {
  HIGH: "#f44336",
  MEDIUM: "#ff9800",
  LOW: "#4caf50",
};
const RISK_LABELS: Record<string, string> = {
  HIGH: "High Risk",
  MEDIUM: "Medium Risk",
  LOW: "Low Risk",
};
const RISK_ICONS: Record<string, React.ReactNode> = {
  HIGH: <AlertTriangle size={18} color="#f44336" />, // red
  MEDIUM: <AlertTriangle size={18} color="#ff9800" />, // orange
  LOW: <CheckCircle size={18} color="#4caf50" />, // green
};

interface CompanyAnalyticsDashboardProps {
  companyName: string;
}

function getValidIcon(icon: React.ReactNode): ReactElement | undefined {
  // Only allow a valid ReactElement, not string/number/array/boolean
  return React.isValidElement(icon) ? icon : undefined;
}

const CompanyAnalyticsDashboard: React.FC<CompanyAnalyticsDashboardProps> = ({
  companyName,
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!companyName) return;
    setLoading(true);
    setError(null);
    setData(null);
    fetch(`/api/v1/companies/${encodeURIComponent(companyName)}/analytics`)
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      })
      .then((json) => setData(json))
      .catch((e) => setError(e.message || "Failed to load analytics"))
      .finally(() => setLoading(false));
  }, [companyName]);

  // Prepare risk distribution for chart
  const riskDistribution = data?.risk_distribution || {};
  const riskChartData = Object.entries(riskDistribution).map(
    ([key, value]) => ({
      name: RISK_LABELS[key] || key,
      value,
      code: key,
    })
  );

  // Alert summary
  const alertSummary = data?.alert_summary || {};

  // Latest events
  const latestEvents = data?.latest_events || [];

  // Last alert date
  const lastAlertDate = alertSummary?.last_alert;

  // Loading/Error/Empty states
  if (!companyName) {
    return <Typography>Select a company to view analytics.</Typography>;
  }
  if (loading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minHeight={200}
      >
        <CircularProgress />
      </Box>
    );
  }
  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }
  if (!data) {
    return null;
  }

  // Pie label function
  const pieLabel = (props: any) => {
    const { name, percent } = props;
    return `${name} (${((percent || 0) * 100).toFixed(0)}%)`;
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto", p: 2 }}>
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                {data.company_name || companyName}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Total Events: <b>{data.total_events}</b>
                {lastAlertDate && (
                  <>
                    {" "}
                    | Last Alert:{" "}
                    <b>{new Date(lastAlertDate).toLocaleDateString()}</b>
                  </>
                )}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box
                display="flex"
                justifyContent={{ xs: "flex-start", md: "flex-end" }}
              >
                <Stack direction="row" spacing={2}>
                  <Chip
                    icon={<AlertTriangle color="#f44336" />}
                    label={`Total Alerts: ${alertSummary?.total_alerts ?? 0}`}
                    color="error"
                  />
                  <Chip
                    icon={<XCircle color="#f44336" />}
                    label={`High-Risk: ${alertSummary?.high_risk_alerts ?? 0}`}
                    color="error"
                  />
                </Stack>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk Distribution Chart & Alert Summary */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              {riskChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={riskChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={pieLabel}
                    >
                      {riskChartData.map((entry, idx) => (
                        <Cell
                          key={entry.code}
                          fill={RISK_COLORS[entry.code] || "#8884d8"}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography>No risk data available.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alert Summary
              </Typography>
              <Stack spacing={1}>
                <Box display="flex" alignItems="center">
                  <AlertTriangle color="#f44336" style={{ marginRight: 8 }} />
                  <Typography>
                    <b>Total Alerts:</b> {alertSummary?.total_alerts ?? 0}
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <XCircle color="#f44336" style={{ marginRight: 8 }} />
                  <Typography>
                    <b>High-Risk Alerts:</b>{" "}
                    {alertSummary?.high_risk_alerts ?? 0}
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center">
                  <Info color="#1976d2" style={{ marginRight: 8 }} />
                  <Typography>
                    <b>Last Alert:</b>{" "}
                    {lastAlertDate
                      ? new Date(lastAlertDate).toLocaleString()
                      : "N/A"}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Latest Events Table */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Latest Events
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Risk Label</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {latestEvents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      No recent events found.
                    </TableCell>
                  </TableRow>
                ) : (
                  latestEvents.map((event: any, idx: number) => {
                    const risk = event.risk_label?.toUpperCase();
                    return (
                      <TableRow key={event.event_id || idx}>
                        <TableCell>
                          <Typography
                            fontWeight={event.alerted ? "bold" : undefined}
                            color={event.alerted ? "error" : undefined}
                          >
                            {event.title}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getValidIcon(RISK_ICONS[risk]) || undefined}
                            label={
                              RISK_LABELS[risk] || event.risk_label || "Unknown"
                            }
                            style={{
                              background: RISK_COLORS[risk] || undefined,
                              color: "#fff",
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          {event.confidence !== undefined
                            ? `${Math.round(event.confidence * 100)}%`
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {event.pub_date
                            ? new Date(event.pub_date).toLocaleDateString()
                            : "-"}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CompanyAnalyticsDashboard;
