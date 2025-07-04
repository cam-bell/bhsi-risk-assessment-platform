import React from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import { AlertTriangle, Info } from "lucide-react";

const severityColorMap: Record<string, "success" | "warning" | "error"> = {
  low: "success",
  medium: "warning",
  high: "error",
};

const KeyRisksPanel: React.FC<{ keyRisks?: any[] }> = ({ keyRisks }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <AlertTriangle size={20} color="#f44336" style={{ marginRight: 8 }} />
        <Typography variant="h6">Key Risks</Typography>
      </Box>
      {Array.isArray(keyRisks) && keyRisks.length > 0 ? (
        keyRisks.map((risk, idx) => (
          <Box key={idx} mb={2}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              mb={1}
            >
              <Typography variant="subtitle2" fontWeight="medium">
                {risk.risk_type}
              </Typography>
              <Chip
                label={risk.severity?.toUpperCase()}
                color={severityColorMap[risk.severity] || "default"}
                size="small"
                sx={{ fontWeight: 700 }}
                icon={
                  risk.severity === "high" ? (
                    <AlertTriangle size={14} color="#f44336" />
                  ) : undefined
                }
              />
            </Box>
            <Typography variant="body2" color="text.secondary" mb={1}>
              {risk.description}
            </Typography>
            <List dense>
              {risk.recommendations?.map((rec: string, recIdx: number) => (
                <ListItem key={recIdx} sx={{ py: 0.5 }}>
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
            {idx < keyRisks.length - 1 && <Divider sx={{ mt: 2 }} />}
          </Box>
        ))
      ) : (
        <Typography variant="body2" color="text.secondary">
          No key risks found.
        </Typography>
      )}
    </CardContent>
  </Card>
);

export default KeyRisksPanel;
