import React from "react";
import { Card, CardContent, Typography, Box, Fade } from "@mui/material";
import { FileText } from "lucide-react";

const ExecutiveSummaryCard: React.FC<{ summary: string }> = ({ summary }) => (
  <Fade in timeout={700}>
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <FileText size={20} style={{ marginRight: 8 }} />
          <Typography variant="h6">Executive Summary</Typography>
        </Box>
        <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
          {summary || "-"}
        </Typography>
      </CardContent>
    </Card>
  </Fade>
);

export default ExecutiveSummaryCard;
