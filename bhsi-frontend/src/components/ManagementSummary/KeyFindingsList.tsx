import React from "react";
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
} from "@mui/material";
import { Stars } from "@mui/icons-material";

const KeyFindingsList: React.FC<{ keyFindings: string[] }> = ({
  keyFindings,
}) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Stars sx={{ color: "#673ab7", mr: 1 }} />
        <Typography variant="h6">Key Findings</Typography>
      </Box>
      <List>
        {Array.isArray(keyFindings) && keyFindings.length > 0 ? (
          keyFindings.map((finding, idx) => (
            <ListItem key={idx}>
              <ListItemIcon>
                <Stars sx={{ color: "#9575cd" }} />
              </ListItemIcon>
              <ListItemText primary={finding} />
            </ListItem>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No key findings found.
          </Typography>
        )}
      </List>
    </CardContent>
  </Card>
);

export default KeyFindingsList;
