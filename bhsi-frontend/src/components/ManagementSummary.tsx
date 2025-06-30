import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
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
} from "@mui/material";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  TrendingUp,
  TrendingDown,
  Minus,
  FileText,
  Shield,
  DollarSign,
} from "lucide-react";
import { useGetManagementSummaryMutation } from "../store/api/analyticsApi";

interface ManagementSummaryProps {
  companyName: string;
}

const StatusIcon: React.FC<{
  status:
    | "healthy"
    | "concerning"
    | "critical"
    | "compliant"
    | "partial"
    | "non_compliant"
    | "positive"
    | "neutral"
    | "negative";
}> = ({ status }) => {
  switch (status) {
    case "healthy":
    case "compliant":
    case "positive":
      return <CheckCircle size={16} color="#4caf50" />;
    case "concerning":
    case "partial":
    case "neutral":
      return <AlertTriangle size={16} color="#ff9800" />;
    case "critical":
    case "non_compliant":
    case "negative":
      return <XCircle size={16} color="#f44336" />;
    default:
      return <Info size={16} color="#9e9e9e" />;
  }
};

const SeverityChip: React.FC<{ severity: "low" | "medium" | "high" }> = ({
  severity,
}) => {
  const colors = {
    low: "success",
    medium: "warning",
    high: "error",
  } as const;

  return (
    <Chip
      label={severity.toUpperCase()}
      color={colors[severity]}
      size="small"
      variant="outlined"
    />
  );
};

const ManagementSummary: React.FC<ManagementSummaryProps> = ({
  companyName,
}) => {
  const {
    data: summary,
    isLoading,
    error,
  } = useGetManagementSummaryMutation({ company_name: companyName });

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
        Error loading management summary for {companyName}. Please try again.
      </Alert>
    );
  }

  if (!summary) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        No management summary available for {companyName}.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Management Summary
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {summary.company_name} • Generated{" "}
          {new Date(summary.generated_at).toLocaleString()}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Executive Summary */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <FileText size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Executive Summary</Typography>
              </Box>
              <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                {summary.summary.executive_summary}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Key Risks */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AlertTriangle size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Key Risks</Typography>
              </Box>
              <Stack spacing={2}>
                {summary.summary.key_risks.map((risk, index) => (
                  <Box key={index}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={1}
                    >
                      <Typography variant="subtitle2" fontWeight="medium">
                        {risk.risk_type}
                      </Typography>
                      <SeverityChip severity={risk.severity} />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      {risk.description}
                    </Typography>
                    <List dense>
                      {risk.recommendations.map((rec, recIndex) => (
                        <ListItem key={recIndex} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 20 }}>
                            <Info size={12} color="#2196f3" />
                          </ListItemIcon>
                          <ListItemText
                            primary={rec}
                            primaryTypographyProps={{ variant: "caption" }}
                          />
                        </ListItem>
                      ))}
                    </List>
                    {index < summary.summary.key_risks.length - 1 && (
                      <Divider sx={{ mt: 2 }} />
                    )}
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <DollarSign size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Financial Health</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={2}>
                <StatusIcon status={summary.summary.financial_health.status} />
                <Typography variant="subtitle1" fontWeight="medium" ml={1}>
                  {summary.summary.financial_health.status.toUpperCase()}
                </Typography>
              </Box>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Indicator</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {summary.summary.financial_health.indicators.map(
                      (indicator, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2">
                              {indicator.indicator}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {indicator.value}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <StatusIcon status={indicator.status} />
                              <Typography variant="body2" ml={0.5}>
                                {indicator.status.toUpperCase()}
                              </Typography>
                            </Box>
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

        {/* Compliance Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Shield size={20} style={{ marginRight: 8 }} />
                <Typography variant="h6">Compliance Status</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={2}>
                <StatusIcon
                  status={summary.summary.compliance_status.overall}
                />
                <Typography variant="subtitle1" fontWeight="medium" ml={1}>
                  Overall:{" "}
                  {summary.summary.compliance_status.overall
                    .replace("_", " ")
                    .toUpperCase()}
                </Typography>
              </Box>
              <Grid container spacing={2}>
                {summary.summary.compliance_status.areas.map((area, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                        mb={1}
                      >
                        <Typography variant="subtitle2" fontWeight="medium">
                          {area.area}
                        </Typography>
                        <Box display="flex" alignItems="center">
                          <StatusIcon status={area.status} />
                          <Typography variant="caption" ml={0.5}>
                            {area.status.replace("_", " ").toUpperCase()}
                          </Typography>
                        </Box>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {area.details}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ManagementSummary;
