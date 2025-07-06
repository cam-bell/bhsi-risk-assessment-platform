import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Collapse,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  CheckCircle,
  Error,
  Warning,
  Refresh,
  ExpandMore,
  ExpandLess,
  Storage,
  Timeline,
  Queue,
} from "@mui/icons-material";

interface BigQueryHealth {
  status: "healthy" | "degraded" | "unhealthy";
  failure_rate_percent: number;
  queue: {
    total_pending: number;
    high_priority: number;
    medium_priority: number;
    low_priority: number;
    tables: Record<string, number>;
  };
  failures: {
    total_failures: number;
    failure_stats: Record<string, number>;
    recent_failures: Array<{
      request_id: string;
      table_name: string;
      error: string;
      timestamp: string;
      retry_count: number;
      data_count: number;
      operation: string;
    }>;
    success_stats: Record<string, number>;
  };
  timestamp: string;
}

interface BigQueryStatusMonitorProps {
  showDetails?: boolean;
  onStatusChange?: (status: string) => void;
}

const BigQueryStatusMonitor: React.FC<BigQueryStatusMonitorProps> = ({
  showDetails = false,
  onStatusChange,
}) => {
  const [healthData, setHealthData] = useState<BigQueryHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(showDetails);

  const fetchHealthStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/v1/bigquery/health");
      const data = await response.json();

      if (data.status === "success" && data.bigquery_health) {
        setHealthData(data.bigquery_health);
        onStatusChange?.(data.bigquery_health.status);
      } else {
        setError(data.error || "Failed to fetch BigQuery health status");
      }
    } catch (err) {
      setError("Failed to connect to BigQuery health endpoint");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthStatus();
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealthStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle color="success" />;
      case "degraded":
        return <Warning color="warning" />;
      case "unhealthy":
        return <Error color="error" />;
      default:
        return <Error color="error" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "success";
      case "degraded":
        return "warning";
      case "unhealthy":
        return "error";
      default:
        return "error";
    }
  };

  const getStatusMessage = (status: string, failureRate: number) => {
    switch (status) {
      case "healthy":
        return `BigQuery is operating normally (${failureRate}% failure rate)`;
      case "degraded":
        return `BigQuery performance is degraded (${failureRate}% failure rate)`;
      case "unhealthy":
        return `BigQuery is experiencing issues (${failureRate}% failure rate)`;
      default:
        return "BigQuery status unknown";
    }
  };

  if (loading && !healthData) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} />
            <Typography>Checking BigQuery status...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error && !healthData) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={fetchHealthStatus}>
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  if (!healthData) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={2}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <Storage />
            <Typography variant="h6">BigQuery Status</Typography>
            {getStatusIcon(healthData.status)}
            <Chip
              label={healthData.status.toUpperCase()}
              color={getStatusColor(healthData.status) as any}
              size="small"
            />
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Refresh status">
              <IconButton
                size="small"
                onClick={fetchHealthStatus}
                disabled={loading}
              >
                {loading ? <CircularProgress size={16} /> : <Refresh />}
              </IconButton>
            </Tooltip>
            <Tooltip title={expanded ? "Hide details" : "Show details"}>
              <IconButton size="small" onClick={() => setExpanded(!expanded)}>
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" mb={2}>
          {getStatusMessage(healthData.status, healthData.failure_rate_percent)}
        </Typography>

        <Collapse in={expanded}>
          <Box mt={2}>
            {/* Queue Status */}
            <Box mb={3}>
              <Typography
                variant="subtitle2"
                gutterBottom
                display="flex"
                alignItems="center"
                gap={1}
              >
                <Queue fontSize="small" />
                Queue Status
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <Chip
                  label={`Pending: ${healthData.queue.total_pending}`}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={`High Priority: ${healthData.queue.high_priority}`}
                  color="error"
                  size="small"
                />
                <Chip
                  label={`Medium Priority: ${healthData.queue.medium_priority}`}
                  color="warning"
                  size="small"
                />
                <Chip
                  label={`Low Priority: ${healthData.queue.low_priority}`}
                  color="success"
                  size="small"
                />
              </Box>
            </Box>

            {/* Failure Statistics */}
            <Box mb={3}>
              <Typography
                variant="subtitle2"
                gutterBottom
                display="flex"
                alignItems="center"
                gap={1}
              >
                <Timeline fontSize="small" />
                Failure Statistics
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
                <Chip
                  label={`Total Failures: ${healthData.failures.total_failures}`}
                  color="error"
                  size="small"
                />
                <Chip
                  label={`Success Rate: ${Math.round(
                    (1 - healthData.failure_rate_percent / 100) * 100
                  )}%`}
                  color="success"
                  size="small"
                />
              </Box>

              {/* Table Failures */}
              {Object.keys(healthData.failures.failure_stats).length > 0 && (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Table</TableCell>
                        <TableCell align="right">Failures</TableCell>
                        <TableCell align="right">Success</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(healthData.failures.failure_stats).map(
                        ([table, failures]) => (
                          <TableRow key={table}>
                            <TableCell>{table}</TableCell>
                            <TableCell align="right">
                              <Chip
                                label={failures}
                                color="error"
                                size="small"
                              />
                            </TableCell>
                            <TableCell align="right">
                              {healthData.failures.success_stats[table] || 0}
                            </TableCell>
                          </TableRow>
                        )
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>

            {/* Recent Failures */}
            {healthData.failures.recent_failures.length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Recent Failures
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Table</TableCell>
                        <TableCell>Error</TableCell>
                        <TableCell>Retries</TableCell>
                        <TableCell>Data Count</TableCell>
                        <TableCell>Time</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {healthData.failures.recent_failures
                        .slice(0, 5)
                        .map((failure) => (
                          <TableRow key={failure.request_id}>
                            <TableCell>{failure.table_name}</TableCell>
                            <TableCell>
                              <Typography variant="caption" color="error">
                                {failure.error.length > 50
                                  ? `${failure.error.substring(0, 50)}...`
                                  : failure.error}
                              </Typography>
                            </TableCell>
                            <TableCell>{failure.retry_count}</TableCell>
                            <TableCell>{failure.data_count}</TableCell>
                            <TableCell>
                              {new Date(failure.timestamp).toLocaleTimeString()}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default BigQueryStatusMonitor;
