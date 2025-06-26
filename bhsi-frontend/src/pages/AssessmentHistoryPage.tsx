import React from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Stack,
  Divider,
} from "@mui/material";
import { useCompanies } from "../context/CompaniesContext";
import { Building2 } from "lucide-react";

const riskColor = {
  green: "success",
  orange: "warning",
  red: "error",
} as const;

const AssessmentHistoryPage = () => {
  const { assessedCompanies } = useCompanies();

  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh", py: 6 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Assessment History
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          View the history of all company risk assessments performed in this
          session.
        </Typography>
        <Card>
          <CardContent>
            {assessedCompanies.length === 0 ? (
              <Box sx={{ textAlign: "center", py: 8 }}>
                <Building2
                  size={64}
                  color="#ccc"
                  style={{ marginBottom: 16 }}
                />
                <Typography variant="h6" gutterBottom>
                  No Assessments Yet
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Start by searching and assessing companies on the Risk
                  Assessment page. Your assessments will appear here.
                </Typography>
              </Box>
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Company Name</TableCell>
                      <TableCell>VAT</TableCell>
                      <TableCell>Risk Level</TableCell>
                      <TableCell>Assessed At</TableCell>
                      <TableCell>Assessed By</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {assessedCompanies.map((company) => (
                      <TableRow key={company.id}>
                        <TableCell>{company.name}</TableCell>
                        <TableCell>{company.vat}</TableCell>
                        <TableCell>
                          <Chip
                            label={company.overallRisk.toUpperCase()}
                            color={riskColor[company.overallRisk]}
                            size="small"
                            sx={{ fontWeight: "bold" }}
                          />
                        </TableCell>
                        <TableCell>
                          {new Date(company.assessedAt).toLocaleString()}
                        </TableCell>
                        <TableCell>{company.assessedBy}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
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

export default AssessmentHistoryPage;
