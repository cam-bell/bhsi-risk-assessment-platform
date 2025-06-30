import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
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
  TextField,
  Button,
  Autocomplete,
  Divider,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart3,
  X,
  Plus,
  GitCompare,
} from "lucide-react";
import { useCompareCompaniesQuery } from "../store/api/analyticsApi";

interface CompanyComparisonProps {
  initialCompanies?: string[];
}

const RiskIndicator: React.FC<{ level: "green" | "orange" | "red" }> = ({
  level,
}) => {
  const colors = {
    green: "#4caf50",
    orange: "#ff9800",
    red: "#f44336",
  };

  return (
    <Box
      sx={{
        width: 12,
        height: 12,
        borderRadius: "50%",
        backgroundColor: colors[level],
        display: "inline-block",
        mr: 1,
      }}
    />
  );
};

const TrendIcon: React.FC<{
  trend: "increasing" | "decreasing" | "stable";
}> = ({ trend }) => {
  switch (trend) {
    case "increasing":
      return <TrendingUp size={16} color="#f44336" />;
    case "decreasing":
      return <TrendingDown size={16} color="#4caf50" />;
    case "stable":
      return <Minus size={16} color="#9e9e9e" />;
    default:
      return null;
  }
};

const CompanyComparison: React.FC<CompanyComparisonProps> = ({
  initialCompanies = [],
}) => {
  const [companies, setCompanies] = useState<string[]>(initialCompanies);
  const [inputValue, setInputValue] = useState("");

  const {
    data: comparison,
    isLoading,
    error,
    refetch,
  } = useCompareCompaniesQuery({ companies }, { skip: companies.length < 2 });

  const handleAddCompany = () => {
    if (inputValue.trim() && !companies.includes(inputValue.trim())) {
      setCompanies([...companies, inputValue.trim()]);
      setInputValue("");
    }
  };

  const handleRemoveCompany = (companyToRemove: string) => {
    setCompanies(companies.filter((c) => c !== companyToRemove));
  };

  const handleCompare = () => {
    if (companies.length >= 2) {
      refetch();
    }
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 7) return "error";
    if (score >= 4) return "warning";
    return "success";
  };

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Company Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Compare risk profiles across multiple companies
        </Typography>
      </Box>

      {/* Company Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Companies to Compare
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Enter company name"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleAddCompany()}
                />
                <Button
                  variant="outlined"
                  onClick={handleAddCompany}
                  disabled={!inputValue.trim()}
                  startIcon={<Plus />}
                >
                  Add
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                variant="contained"
                onClick={handleCompare}
                disabled={companies.length < 2}
                startIcon={<GitCompare />}
                fullWidth
              >
                Compare {companies.length} Companies
              </Button>
            </Grid>
          </Grid>

          {/* Selected Companies */}
          {companies.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Selected Companies:
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {companies.map((company) => (
                  <Chip
                    key={company}
                    label={company}
                    onDelete={() => handleRemoveCompany(company)}
                    deleteIcon={<X />}
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {companies.length >= 2 && (
        <>
          {isLoading && (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              minHeight={200}
            >
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error loading comparison data. Please try again.
            </Alert>
          )}

          {comparison && !isLoading && (
            <Grid container spacing={3}>
              {/* Comparative Analysis */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <BarChart3 size={20} style={{ marginRight: 8 }} />
                      <Typography variant="h6">Comparative Analysis</Typography>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={3}>
                        <Paper
                          variant="outlined"
                          sx={{ p: 2, textAlign: "center" }}
                        >
                          <Typography
                            variant="subtitle2"
                            color="text.secondary"
                          >
                            Highest Risk
                          </Typography>
                          <Typography
                            variant="h6"
                            fontWeight="bold"
                            color="error"
                          >
                            {comparison.comparative_analysis.highest_risk}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Paper
                          variant="outlined"
                          sx={{ p: 2, textAlign: "center" }}
                        >
                          <Typography
                            variant="subtitle2"
                            color="text.secondary"
                          >
                            Lowest Risk
                          </Typography>
                          <Typography
                            variant="h6"
                            fontWeight="bold"
                            color="success.main"
                          >
                            {comparison.comparative_analysis.lowest_risk}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Paper
                          variant="outlined"
                          sx={{ p: 2, textAlign: "center" }}
                        >
                          <Typography
                            variant="subtitle2"
                            color="text.secondary"
                          >
                            Most Volatile
                          </Typography>
                          <Typography
                            variant="h6"
                            fontWeight="bold"
                            color="warning.main"
                          >
                            {comparison.comparative_analysis.most_volatile}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Paper
                          variant="outlined"
                          sx={{ p: 2, textAlign: "center" }}
                        >
                          <Typography
                            variant="subtitle2"
                            color="text.secondary"
                          >
                            Risk Correlation
                          </Typography>
                          <Typography variant="h6" fontWeight="bold">
                            {(
                              comparison.comparative_analysis.risk_correlation *
                              100
                            ).toFixed(1)}
                            %
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Detailed Comparison Table */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Detailed Comparison
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Company</TableCell>
                            <TableCell>Overall Risk</TableCell>
                            <TableCell>Legal Risk</TableCell>
                            <TableCell>Bankruptcy Risk</TableCell>
                            <TableCell>Corruption Risk</TableCell>
                            <TableCell>Risk Score</TableCell>
                            <TableCell>Recent Events</TableCell>
                            <TableCell>Trend</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {comparison.comparison_data.map((company, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                <Typography variant="body2" fontWeight="medium">
                                  {company.company_name}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <RiskIndicator
                                    level={company.risk_profile.overall}
                                  />
                                  <Typography
                                    variant="body2"
                                    fontWeight="medium"
                                  >
                                    {company.risk_profile.overall.toUpperCase()}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <RiskIndicator
                                    level={company.risk_profile.legal}
                                  />
                                  <Typography
                                    variant="body2"
                                    fontWeight="medium"
                                  >
                                    {company.risk_profile.legal.toUpperCase()}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <RiskIndicator
                                    level={company.risk_profile.bankruptcy}
                                  />
                                  <Typography
                                    variant="body2"
                                    fontWeight="medium"
                                  >
                                    {company.risk_profile.bankruptcy.toUpperCase()}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <RiskIndicator
                                    level={company.risk_profile.corruption}
                                  />
                                  <Typography
                                    variant="body2"
                                    fontWeight="medium"
                                  >
                                    {company.risk_profile.corruption.toUpperCase()}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={company.risk_score.toFixed(1)}
                                  size="small"
                                  color={
                                    getRiskScoreColor(company.risk_score) as any
                                  }
                                  variant="outlined"
                                />
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" fontWeight="medium">
                                  {company.recent_events}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <TrendIcon trend={company.trend} />
                                  <Typography
                                    variant="body2"
                                    fontWeight="medium"
                                    ml={0.5}
                                  >
                                    {company.trend.toUpperCase()}
                                  </Typography>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </>
      )}

      {/* Empty State */}
      {companies.length < 2 && !isLoading && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <GitCompare
                size={48}
                color="#9e9e9e"
                style={{ marginBottom: 16 }}
              />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Select Companies to Compare
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add at least 2 companies above to start comparing their risk
                profiles
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CompanyComparison;
