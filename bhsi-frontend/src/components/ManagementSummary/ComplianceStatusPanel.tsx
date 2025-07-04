import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  Paper,
} from "@mui/material";
import { Shield, CheckCircle, AlertTriangle, XCircle } from "lucide-react";

const statusColorMap: Record<string, "success" | "warning" | "error"> = {
  compliant: "success",
  partial: "warning",
  non_compliant: "error",
};

const statusIconMap: Record<string, React.ReactElement | undefined> = {
  compliant: <CheckCircle size={16} color="#4caf50" />,
  partial: <AlertTriangle size={16} color="#ff9800" />,
  non_compliant: <XCircle size={16} color="#f44336" />,
};

function getStatusIcon(status: string) {
  return statusIconMap[status] || undefined;
}

const ComplianceStatusPanel: React.FC<{ complianceStatus?: any }> = ({
  complianceStatus,
}) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Shield size={20} style={{ marginRight: 8 }} />
        <Typography variant="h6">Compliance Status</Typography>
        {complianceStatus?.overall && (
          <Chip
            label={complianceStatus.overall.replace("_", " ").toUpperCase()}
            color={statusColorMap[complianceStatus.overall] || "default"}
            icon={statusIconMap[complianceStatus.overall]}
            sx={{ ml: 2, fontWeight: 700 }}
          />
        )}
      </Box>
      <Grid container spacing={2}>
        {Array.isArray(complianceStatus?.areas) &&
        complianceStatus.areas.length > 0 ? (
          complianceStatus.areas.map((area: any, idx: number) => (
            <Grid item xs={12} md={6} key={idx}>
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
                  <Chip
                    label={area.status.replace("_", " ").toUpperCase()}
                    color={statusColorMap[area.status] || "default"}
                    icon={statusIconMap[area.status]}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {area.details}
                </Typography>
              </Paper>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">
              No compliance areas found.
            </Typography>
          </Grid>
        )}
      </Grid>
    </CardContent>
  </Card>
);

export default ComplianceStatusPanel;
