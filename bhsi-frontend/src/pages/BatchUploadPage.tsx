import React from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Divider,
} from "@mui/material";
import BatchUpload from "../components/BatchUpload";

// Define allowed risk levels
const riskLevels = ["green", "orange", "red"] as const;
type RiskLevel = (typeof riskLevels)[number];

// Mock getMockResponse for demo
const getMockResponse = (company: string) => {
  const randomRisk = () =>
    riskLevels[Math.floor(Math.random() * riskLevels.length)];
  return {
    company,
    vat: "ESX" + Math.floor(Math.random() * 100000000),
    overall: randomRisk() as RiskLevel,
    blocks: {
      turnover: randomRisk() as RiskLevel,
      shareholding: randomRisk() as RiskLevel,
      bankruptcy: randomRisk() as RiskLevel,
      legal: randomRisk() as RiskLevel,
    },
    status: "complete",
  };
};

const handleSaveResults = (results: any[]) => {
  // For demo, just log the results
  // In a real app, you might save to backend or localStorage
  // eslint-disable-next-line no-console
  console.log("Saved batch results:", results);
};

const BatchUploadPage = () => {
  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh", py: 6 }}>
      <Container maxWidth="md">
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Batch Upload
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Upload a CSV or Excel file with company names to assess risk for
          multiple companies at once. Download a sample file to get started.
        </Typography>
        <Card>
          <CardContent>
            <BatchUpload
              onSaveResults={handleSaveResults}
              getMockResponse={getMockResponse}
            />
          </CardContent>
        </Card>
        <Divider sx={{ my: 4 }} />
        <Typography variant="body2" color="text.secondary" align="center">
          &copy; {new Date().getFullYear()} Berkshire Hathaway Specialty
          Insurance. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default BatchUploadPage;
