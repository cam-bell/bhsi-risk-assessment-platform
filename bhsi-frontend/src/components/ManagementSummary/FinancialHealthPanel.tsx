import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
} from "@mui/material";
import {
  DollarSign,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
} from "lucide-react";

const statusColorMap: Record<string, "success" | "warning" | "error"> = {
  healthy: "success",
  concerning: "warning",
  critical: "error",
};

const indicatorStatusIcon = (status: string) => {
  if (status === "positive") return <CheckCircle size={14} color="#4caf50" />;
  if (status === "neutral") return <AlertTriangle size={14} color="#ff9800" />;
  if (status === "negative") return <XCircle size={14} color="#f44336" />;
  return <Info size={14} color="#9e9e9e" />;
};

const FinancialHealthPanel: React.FC<{ financialHealth?: any }> = ({
  financialHealth,
}) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <DollarSign size={20} style={{ marginRight: 8 }} />
        <Typography variant="h6">Financial Health</Typography>
        {financialHealth?.status && (
          <Chip
            label={financialHealth.status.toUpperCase()}
            color={statusColorMap[financialHealth.status] || "default"}
            sx={{ ml: 2, fontWeight: 700 }}
          />
        )}
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
            {Array.isArray(financialHealth?.indicators) &&
            financialHealth.indicators.length > 0 ? (
              financialHealth.indicators.map((indicator: any, idx: number) => (
                <TableRow key={idx}>
                  <TableCell>
                    <Tooltip title={indicator.indicator} placement="top">
                      <Typography variant="body2">
                        {indicator.indicator}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {indicator.value}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {indicatorStatusIcon(indicator.status)}
                      <Typography variant="caption">
                        {indicator.status?.toUpperCase()}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No indicators found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </CardContent>
  </Card>
);

export default FinancialHealthPanel;
