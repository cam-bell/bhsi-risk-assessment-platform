import React from "react";
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Box,
} from "@mui/material";
import { CheckCircle } from "lucide-react";

const RecommendationsChecklist: React.FC<{ recommendations: string[] }> = ({
  recommendations,
}) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <CheckCircle size={20} color="#1976d2" style={{ marginRight: 8 }} />
        <Typography variant="h6">Recommendations</Typography>
      </Box>
      <List>
        {Array.isArray(recommendations) && recommendations.length > 0 ? (
          recommendations.map((rec, idx) => (
            <ListItem key={idx}>
              <ListItemIcon>
                <CheckCircle size={16} color="#43a047" />
              </ListItemIcon>
              <ListItemText primary={rec} />
            </ListItem>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No recommendations found.
          </Typography>
        )}
      </List>
    </CardContent>
  </Card>
);

export default RecommendationsChecklist;
