import React from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Fade,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  AlertTriangle,
  Scale,
  DollarSign,
  Shield,
  Gavel,
  Info,
} from "lucide-react";

const categoryIconMap: Record<string, React.ReactNode> = {
  legal: <Gavel size={18} color="#673ab7" />,
  financial: <DollarSign size={18} color="#1976d2" />,
  regulatory: <Shield size={18} color="#0288d1" />,
  operational: <Scale size={18} color="#43a047" />,
};

const riskColorMap: Record<string, "success" | "warning" | "error"> = {
  green: "success",
  orange: "warning",
  red: "error",
};

const RiskBreakdownGrid: React.FC<{ riskBreakdown: Record<string, any> }> = ({
  riskBreakdown,
}) => (
  <Grid container spacing={2}>
    {Object.entries(riskBreakdown || {}).map(([category, breakdown], idx) => (
      <Grid item xs={12} sm={6} md={3} key={category}>
        <Fade in timeout={500 + idx * 150}>
          <Card
            variant="outlined"
            sx={{
              borderLeft:
                breakdown.level === "red"
                  ? "6px solid #f44336"
                  : breakdown.level === "orange"
                  ? "6px solid #ff9800"
                  : "6px solid #4caf50",
              boxShadow: breakdown.level === "red" ? 4 : 1,
              background:
                breakdown.level === "red"
                  ? "#fff5f5"
                  : breakdown.level === "orange"
                  ? "#fff8e1"
                  : "#f5fff5",
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {categoryIconMap[category] || <Info size={18} />}
                <Typography variant="subtitle1" fontWeight={700}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </Typography>
                <Chip
                  label={breakdown.level?.toUpperCase() || "-"}
                  color={riskColorMap[breakdown.level] || "default"}
                  size="small"
                  sx={{ fontWeight: 700, ml: 1 }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary" mb={1}>
                {breakdown.reasoning}
              </Typography>
              {Array.isArray(breakdown.evidence) &&
                breakdown.evidence.length > 0 && (
                  <Box mb={1}>
                    <Typography variant="caption" color="text.secondary">
                      Evidence:
                    </Typography>
                    <List dense>
                      {breakdown.evidence
                        .slice(0, 3)
                        .map((ev: string, i: number) => (
                          <ListItem key={i} sx={{ py: 0 }}>
                            <ListItemIcon sx={{ minWidth: 20 }}>
                              <Info size={14} color="#2196f3" />
                            </ListItemIcon>
                            <ListItemText
                              primary={ev}
                              primaryTypographyProps={{ variant: "caption" }}
                            />
                          </ListItem>
                        ))}
                    </List>
                  </Box>
                )}
              <Typography variant="caption" color="text.secondary">
                Confidence: {Math.round((breakdown.confidence || 0) * 100)}%
              </Typography>
            </CardContent>
          </Card>
        </Fade>
      </Grid>
    ))}
  </Grid>
);

export default RiskBreakdownGrid;
