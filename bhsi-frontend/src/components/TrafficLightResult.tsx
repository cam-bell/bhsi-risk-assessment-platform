import { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grow,
  useMediaQuery,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Link,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import {
  ChevronDown,
  Database,
  Building,
  FileText,
  Scale,
  ExternalLink,
  Calendar,
  TrendingUp,
  Eye,
  Search,
  BarChart3,
} from "lucide-react";
import { type TrafficLightResponse } from "./TrafficLightQuery";
import RiskAnalysisDetails, {
  convertSearchResultsToRiskAnalysis,
} from "./RiskAnalysisDetails";

interface TrafficLightResultProps {
  result: TrafficLightResponse;
}

// Map color strings to MUI color values
const colorMap = {
  green: "success",
  orange: "warning",
  red: "error",
} as const;

// Map risk levels to colors
const riskLevelColorMap = {
  "Low-Other": "success",
  "Low-Regulatory": "success",
  "Low-Legal": "success",
  "Low-Financial": "success",
  "Medium-Economic": "warning",
  "Medium-Tax": "warning",
  "Medium-Legal": "warning",
  "Medium-Financial": "warning",
  "High-Legal": "error",
  "High-Financial": "error",
  Unknown: "default",
} as const;

// Map parameters to readable display names
const parameterMap = {
  turnover: "Financial Turnover",
  shareholding: "Shareholding Structure",
  bankruptcy: "Bankruptcy History",
  legal: "Legal Issues",
} as const;

// Map parameters to their data sources
const dataSourcesMap = {
  turnover: {
    primary: "SABI Bureau van Dijk Database",
    secondary: ["Companies House", "Annual Reports", "Financial Statements"],
    icon: <Database size={16} />,
    description:
      "Financial performance data sourced from official company filings and commercial databases",
    lastUpdated: "2024-01-15",
  },
  shareholding: {
    primary: "Companies House Registry",
    secondary: [
      "PSC Register",
      "Shareholding Disclosures",
      "Regulatory Filings",
    ],
    icon: <Building size={16} />,
    description:
      "Ownership structure verified through official company registrations and regulatory submissions",
    lastUpdated: "2024-01-12",
  },
  bankruptcy: {
    primary: "Insolvency Service Records",
    secondary: [
      "Court Records",
      "Gazette Notices",
      "Credit Reference Agencies",
    ],
    icon: <Scale size={16} />,
    description:
      "Insolvency history tracked through official court records and regulatory announcements",
    lastUpdated: "2024-01-10",
  },
  legal: {
    primary: "UK Court Service",
    secondary: ["Legal Databases", "Regulatory Actions", "Public Records"],
    icon: <FileText size={16} />,
    description:
      "Legal proceedings monitored through court systems and regulatory enforcement databases",
    lastUpdated: "2024-01-08",
  },
} as const;

const TrafficLightResult = ({ result }: TrafficLightResultProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [visible, setVisible] = useState(false);
  const [showDetailedResults, setShowDetailedResults] = useState(false);
  const [showRiskAnalysis, setShowRiskAnalysis] = useState(false);

  // Trigger animation after component mounts
  useEffect(() => {
    setVisible(true);
  }, []);

  // Get search results from the result
  const searchResults = result.searchResults?.results || [];
  const hasSearchResults = searchResults.length > 0;

  // Convert search results to risk analysis format
  const riskAnalysisData = result.searchResults
    ? convertSearchResultsToRiskAnalysis(result.searchResults)
    : null;

  return (
    <>
      <Grow in={visible} timeout={800}>
        <Card>
          <CardContent sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                mb: 4,
              }}
            >
              <Typography variant="h5" component="h3" gutterBottom>
                Risk Assessment Result
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  mt: 2,
                }}
              >
                <Typography variant="body1" gutterBottom>
                  <strong>Company:</strong> {result.company}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>VAT:</strong> {result.vat}
                </Typography>
                <Chip
                  label={result.overall.toUpperCase()}
                  color={colorMap[result.overall]}
                  sx={{
                    mt: 3,
                    fontSize: "1.2rem",
                    fontWeight: "bold",
                    py: 3,
                    px: 2,
                    minWidth: "180px",
                    "& .MuiChip-label": {
                      px: 2,
                    },
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{ mt: 2, textAlign: "center", maxWidth: 500 }}
                >
                  {result.overall === "green" &&
                    "Low risk profile. Recommended for renewal."}
                  {result.overall === "orange" &&
                    "Medium risk profile. Recommended for review."}
                  {result.overall === "red" &&
                    "High risk profile. Recommended for pre-cancellation."}
                </Typography>

                {/* Action Buttons */}
                {hasSearchResults && (
                  <Box
                    sx={{
                      mt: 3,
                      display: "flex",
                      gap: 2,
                      flexWrap: "wrap",
                      justifyContent: "center",
                    }}
                  >
                    <Button
                      variant="outlined"
                      startIcon={<Eye />}
                      onClick={() => setShowDetailedResults(true)}
                      size="small"
                    >
                      View Search Results
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<BarChart3 />}
                      onClick={() => setShowRiskAnalysis(true)}
                      size="small"
                    >
                      Detailed Risk Analysis
                    </Button>
                  </Box>
                )}
              </Box>
            </Box>

            <Typography variant="h6" component="h4" gutterBottom sx={{ mb: 2 }}>
              Detailed Parameters
            </Typography>

            {isMobile ? (
              // Mobile view - cards
              <Grid container spacing={2}>
                {Object.entries(result.blocks).map(([key, value]) => {
                  const sourceInfo =
                    dataSourcesMap[key as keyof typeof dataSourcesMap];
                  return (
                    <Grid item xs={12} key={key}>
                      <Paper
                        elevation={0}
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          borderLeft: `6px solid ${
                            theme.palette[colorMap[value]].main
                          }`,
                          backgroundColor: `${
                            theme.palette[colorMap[value]].light
                          }15`,
                        }}
                      >
                        <Box
                          sx={{ display: "flex", alignItems: "center", mb: 1 }}
                        >
                          {sourceInfo.icon}
                          <Typography
                            variant="subtitle2"
                            sx={{ ml: 1, fontWeight: "bold" }}
                          >
                            {parameterMap[key as keyof typeof parameterMap]}
                          </Typography>
                          <Chip
                            label={value.toUpperCase()}
                            color={colorMap[value]}
                            size="small"
                            sx={{ ml: "auto" }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {sourceInfo.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            ) : (
              // Desktop view - table
              <TableContainer
                component={Paper}
                elevation={0}
                sx={{ borderRadius: 2 }}
              >
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Parameter
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Risk Level
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Data Source
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Last Updated
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(result.blocks).map(([key, value]) => {
                      const sourceInfo =
                        dataSourcesMap[key as keyof typeof dataSourcesMap];
                      return (
                        <TableRow key={key}>
                          <TableCell>
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              {sourceInfo.icon}
                              <Typography variant="body2" sx={{ ml: 1 }}>
                                {parameterMap[key as keyof typeof parameterMap]}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={value.toUpperCase()}
                              color={colorMap[value]}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {sourceInfo.primary}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {sourceInfo.secondary.join(", ")}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {sourceInfo.lastUpdated}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}

            {/* Search Results Summary Section */}
            {hasSearchResults && (
              <Box sx={{ mt: 4 }}>
                <Typography
                  variant="h6"
                  component="h4"
                  gutterBottom
                  sx={{ mb: 2 }}
                >
                  Search Results Summary
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="primary">
                        {searchResults.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Documents
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="error">
                        {
                          searchResults.filter((r) =>
                            r.risk_level.startsWith("High")
                          ).length
                        }
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        High Risk
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="warning.main">
                        {
                          searchResults.filter((r) =>
                            r.risk_level.startsWith("Medium")
                          ).length
                        }
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Medium Risk
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="success.main">
                        {
                          searchResults.filter((r) =>
                            r.risk_level.startsWith("Low")
                          ).length
                        }
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Low Risk
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grow>

      {/* Detailed Results Dialog */}
      <Dialog
        open={showDetailedResults}
        onClose={() => setShowDetailedResults(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Search size={20} />
            Detailed Search Results for {result.company}
          </Box>
        </DialogTitle>
        <DialogContent>
          {hasSearchResults ? (
            <Box sx={{ mt: 2 }}>
              <TableContainer component={Paper} elevation={0}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: "bold" }}>Source</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Date</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Title</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Risk Level
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        Confidence
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {searchResults.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip
                            label={item.source}
                            color={
                              item.source === "BOE" ? "primary" : "secondary"
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(item.date).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 300 }}>
                            {item.title}
                          </Typography>
                          {item.summary && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              display="block"
                            >
                              {item.summary.substring(0, 100)}...
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={item.risk_level}
                            color={
                              riskLevelColorMap[
                                item.risk_level as keyof typeof riskLevelColorMap
                              ] || "default"
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <LinearProgress
                              variant="determinate"
                              value={item.confidence * 100}
                              sx={{ width: 60, height: 6, borderRadius: 3 }}
                            />
                            <Typography variant="caption">
                              {Math.round(item.confidence * 100)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button
                            component={Link}
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            startIcon={<ExternalLink size={16} />}
                            size="small"
                            variant="outlined"
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          ) : (
            <Typography variant="body1" sx={{ textAlign: "center", py: 4 }}>
              No search results available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDetailedResults(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Risk Analysis Dialog */}
      <Dialog
        open={showRiskAnalysis}
        onClose={() => setShowRiskAnalysis(false)}
        maxWidth="xl"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <BarChart3 size={20} />
            Detailed Risk Analysis for {result.company}
          </Box>
        </DialogTitle>
        <DialogContent>
          {riskAnalysisData ? (
            <RiskAnalysisDetails
              company={riskAnalysisData.company}
              overallRisk={riskAnalysisData.overallRisk}
              riskFactors={riskAnalysisData.riskFactors}
              confidence={riskAnalysisData.confidence}
              searchResults={result.searchResults}
            />
          ) : (
            <Typography variant="body1" sx={{ textAlign: "center", py: 4 }}>
              No risk analysis data available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRiskAnalysis(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default TrafficLightResult;
