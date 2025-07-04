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
  Tooltip,
  CircularProgress,
  Alert,
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
  DollarSign,
  Shield,
} from "lucide-react";
import DonutLargeIcon from "@mui/icons-material/DonutLarge";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import RiskAnalysisDetails, {
  convertSearchResultsToRiskAnalysis,
} from "./RiskAnalysisDetails";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { useGetManagementSummaryMutation } from "../store/api/analyticsApi";
import StarsIcon from "@mui/icons-material/Stars";

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
  const [showDetails, setShowDetails] = useState(false);
  const [
    getManagementSummary,
    { data: summary, isLoading: summaryLoading, error: summaryError },
  ] = useGetManagementSummaryMutation();
  const [showSummary, setShowSummary] = useState(false);

  // Trigger animation after component mounts
  useEffect(() => {
    setVisible(true);
  }, []);

  // Get search results from the result
  const searchResults = result.searchResults?.results || [];
  const hasSearchResults = searchResults.length > 0;
  const searchMeta =
    result.searchResults &&
    typeof result.searchResults === "object" &&
    "metadata" in result.searchResults
      ? (result.searchResults as any).metadata
      : {};
  const searchDate =
    result.searchResults?.search_date || new Date().toISOString();
  const sourcesUsed = Array.isArray(searchMeta.sources_searched)
    ? searchMeta.sources_searched.join(", ")
    : "N/A";

  // Convert search results to risk analysis format
  const riskAnalysisData = result.searchResults
    ? convertSearchResultsToRiskAnalysis(result.searchResults)
    : null;

  if (!hasSearchResults) {
    return (
      <Card sx={{ mt: 4, p: 4, textAlign: "center" }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No results found for this company.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Try another search or check your spelling.
        </Typography>
      </Card>
    );
  }

  return (
    <>
      <Grow in={visible} timeout={800}>
        <Card sx={{ mt: 2, p: isMobile ? 1 : 3 }}>
          {/* Summary Banner */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              background: theme.palette.grey[100],
              borderRadius: 2,
              px: isMobile ? 2 : 4,
              py: 2,
              mb: 3,
              flexDirection: isMobile ? "column" : "row",
              gap: isMobile ? 1 : 0,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CheckCircleIcon color="success" sx={{ fontSize: 32, mr: 1 }} />
              <Typography variant={isMobile ? "h6" : "h5"} fontWeight={700}>
                {result.company}
              </Typography>
            </Box>
            <Box sx={{ textAlign: isMobile ? "center" : "right" }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Date:</strong>{" "}
                {new Date(searchDate).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Sources:</strong> {sourcesUsed}
              </Typography>
            </Box>
          </Box>

          <CardContent sx={{ p: 0 }}>
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
                  color={colorMap[result.overall as keyof typeof colorMap]}
                  sx={{
                    mt: 3,
                    fontSize: isMobile ? "1.1rem" : "1.5rem",
                    fontWeight: "bold",
                    py: isMobile ? 2 : 3,
                    px: isMobile ? 1 : 4,
                    minWidth: isMobile ? "120px" : "200px",
                    minHeight: isMobile ? "48px" : "64px",
                    boxShadow: 3,
                    letterSpacing: 2,
                    "& .MuiChip-label": {
                      px: 2,
                    },
                  }}
                />
                <Typography
                  variant="body1"
                  sx={{
                    mt: 2,
                    textAlign: "center",
                    maxWidth: 500,
                    color: theme.palette.success.main,
                  }}
                >
                  {result.overall === "green" &&
                    "Low risk profile. Recommended for renewal."}
                  {result.overall === "orange" &&
                    "Medium risk profile. Review recommended."}
                  {result.overall === "red" &&
                    "High risk profile. Caution advised."}
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

            {/* Parameter Table */}
            <TableContainer component={Paper} sx={{ mt: 4, mb: 2 }}>
              <Table size={isMobile ? "small" : "medium"}>
                <TableHead>
                  <TableRow>
                    <TableCell>Parameter</TableCell>
                    <TableCell>Risk Level</TableCell>
                    <TableCell>Data Source</TableCell>
                    <TableCell>Last Updated</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.keys(result.blocks).map((param) => (
                    <TableRow key={param}>
                      <TableCell>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          {
                            dataSourcesMap[param as keyof typeof dataSourcesMap]
                              ?.icon
                          }
                          {parameterMap[param as keyof typeof parameterMap]}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.blocks[
                            param as keyof typeof result.blocks
                          ].toUpperCase()}
                          color={
                            colorMap[
                              result.blocks[param as keyof typeof result.blocks]
                            ]
                          }
                          sx={{ fontWeight: "bold", letterSpacing: 1 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <Typography variant="body2">
                            {
                              dataSourcesMap[
                                param as keyof typeof dataSourcesMap
                              ]?.primary
                            }
                          </Typography>
                          <InfoOutlinedIcon
                            fontSize="small"
                            color="action"
                            titleAccess={
                              dataSourcesMap[
                                param as keyof typeof dataSourcesMap
                              ]?.description
                            }
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip
                          title={`Last updated: ${
                            dataSourcesMap[param as keyof typeof dataSourcesMap]
                              ?.lastUpdated
                          }`}
                          placement="top"
                        >
                          <span>
                            {
                              dataSourcesMap[
                                param as keyof typeof dataSourcesMap
                              ]?.lastUpdated
                            }
                          </span>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

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

            {/* View Details Button */}
            <Box sx={{ textAlign: "center", mt: 2 }}>
              <Button
                variant="outlined"
                startIcon={<BarChart3 />}
                onClick={() => setShowDetails((prev) => !prev)}
                sx={{ fontWeight: 600 }}
              >
                {showDetails ? "Hide Raw Results" : "View Raw Results"}
              </Button>
            </Box>
            {showDetails && (
              <Accordion expanded sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ChevronDown />}>
                  <Typography variant="subtitle2">
                    Raw Search Results
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <pre
                    style={{
                      fontSize: isMobile ? 10 : 13,
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-all",
                      background: "#f9f9f9",
                      padding: 12,
                      borderRadius: 6,
                      maxHeight: 400,
                      overflow: "auto",
                    }}
                  >
                    {JSON.stringify(searchResults, null, 2)}
                  </pre>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Add Management Summary button below the main result display, only if there are search results */}
            {hasSearchResults && (
              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={async () => {
                    await getManagementSummary({
                      company_name: result.company,
                      classification_results: searchResults,
                    });
                    setShowSummary(true);
                  }}
                  disabled={summaryLoading || !searchResults.length}
                >
                  {summaryLoading ? "Loading..." : "Get Management Summary"}
                </Button>
                {summaryLoading && <CircularProgress sx={{ mt: 2 }} />}
                {summaryError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    Error loading management summary. Please try again.
                  </Alert>
                )}
                {/* Management Summary display */}
                {showSummary && summary ? (
                  <Box sx={{ mt: 3, textAlign: "left" }}>
                    {/* 1. Overall Risk Distribution */}
                    <Card sx={{ mb: 3 }}>
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={2} mb={2}>
                          <DonutLargeIcon color="primary" />
                          <Typography variant="h6">Overall Risk</Typography>
                          <Chip
                            label={summary.overall_risk?.toUpperCase() || "-"}
                            color={
                              summary.overall_risk === "red"
                                ? "error"
                                : summary.overall_risk === "orange"
                                ? "warning"
                                : "success"
                            }
                            sx={{ fontWeight: "bold", ml: 2 }}
                          />
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            ml={2}
                          >
                            Method: {summary.method}
                          </Typography>
                        </Box>
                        {/* Show risk distribution if available */}
                        {summary.risk_breakdown && (
                          <Grid container spacing={2}>
                            {Object.entries(summary.risk_breakdown).map(
                              ([category, breakdown]: [string, any]) => (
                                <Grid item xs={12} sm={6} md={3} key={category}>
                                  <Paper
                                    variant="outlined"
                                    sx={{ p: 2, textAlign: "center" }}
                                  >
                                    <Typography
                                      variant="subtitle2"
                                      gutterBottom
                                    >
                                      {category.charAt(0).toUpperCase() +
                                        category.slice(1)}
                                    </Typography>
                                    <Chip
                                      label={breakdown.level?.toUpperCase()}
                                      color={
                                        breakdown.level === "red"
                                          ? "error"
                                          : breakdown.level === "orange"
                                          ? "warning"
                                          : "success"
                                      }
                                      sx={{ fontWeight: "bold", mb: 1 }}
                                    />
                                    <Typography
                                      variant="body2"
                                      color="text.secondary"
                                      mb={1}
                                    >
                                      {breakdown.reasoning}
                                    </Typography>
                                    {Array.isArray(breakdown.evidence) &&
                                      breakdown.evidence.length > 0 && (
                                        <>
                                          <Typography
                                            variant="caption"
                                            color="text.secondary"
                                          >
                                            Evidence:
                                          </Typography>
                                          <ul
                                            style={{
                                              margin: 0,
                                              paddingLeft: 16,
                                            }}
                                          >
                                            {breakdown.evidence
                                              .slice(0, 2)
                                              .map(
                                                (ev: string, idx: number) => (
                                                  <li key={idx}>
                                                    <Typography variant="caption">
                                                      {ev}
                                                    </Typography>
                                                  </li>
                                                )
                                              )}
                                          </ul>
                                        </>
                                      )}
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      Confidence:{" "}
                                      {Math.round(
                                        (breakdown.confidence || 0) * 100
                                      )}
                                      %
                                    </Typography>
                                  </Paper>
                                </Grid>
                              )
                            )}
                          </Grid>
                        )}
                      </CardContent>
                    </Card>

                    {/* 2. Executive Summary */}
                    <Card sx={{ mb: 3 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Executive Summary
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                          {summary.executive_summary}
                        </Typography>
                      </CardContent>
                    </Card>

                    {/* 3. Key Risk Items */}
                    {Array.isArray(summary.key_risks) &&
                      summary.key_risks.length > 0 && (
                        <Card sx={{ mb: 3 }}>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Key Risk Items
                            </Typography>
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography variant="subtitle2">
                                  Show/Hide Key Risks
                                </Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <TableContainer
                                  component={Paper}
                                  variant="outlined"
                                >
                                  <Table size="small">
                                    <TableHead>
                                      <TableRow>
                                        <TableCell>Risk Type</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell>Severity</TableCell>
                                        <TableCell>Recommendations</TableCell>
                                      </TableRow>
                                    </TableHead>
                                    <TableBody>
                                      {summary.key_risks.map(
                                        (risk: any, idx: number) => (
                                          <TableRow key={idx}>
                                            <TableCell>
                                              {risk.risk_type}
                                            </TableCell>
                                            <TableCell>
                                              {risk.description}
                                            </TableCell>
                                            <TableCell>
                                              <Chip
                                                label={risk.severity?.toUpperCase()}
                                                color={
                                                  risk.severity === "high"
                                                    ? "error"
                                                    : risk.severity === "medium"
                                                    ? "warning"
                                                    : "success"
                                                }
                                                size="small"
                                              />
                                            </TableCell>
                                            <TableCell>
                                              {Array.isArray(
                                                risk.recommendations
                                              )
                                                ? risk.recommendations.join(
                                                    ", "
                                                  )
                                                : "-"}
                                            </TableCell>
                                          </TableRow>
                                        )
                                      )}
                                    </TableBody>
                                  </Table>
                                </TableContainer>
                              </AccordionDetails>
                            </Accordion>
                          </CardContent>
                        </Card>
                      )}

                    {/* 4. Financial Health */}
                    {summary.financial_health && (
                      <Card sx={{ mb: 3 }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" mb={2}>
                            <DollarSign size={20} style={{ marginRight: 8 }} />
                            <Typography variant="h6">
                              Financial Health
                            </Typography>
                            <Chip
                              label={summary.financial_health.status?.toUpperCase()}
                              color={
                                summary.financial_health.status === "critical"
                                  ? "error"
                                  : summary.financial_health.status ===
                                    "concerning"
                                  ? "warning"
                                  : "success"
                              }
                              sx={{ ml: 2 }}
                            />
                          </Box>
                          <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Indicator</TableCell>
                                  <TableCell>Value</TableCell>
                                  <TableCell>Status</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {Array.isArray(
                                  summary.financial_health.indicators
                                ) &&
                                summary.financial_health.indicators.length >
                                  0 ? (
                                  summary.financial_health.indicators.map(
                                    (indicator: any, idx: number) => (
                                      <TableRow key={idx}>
                                        <TableCell>
                                          {indicator.indicator}
                                        </TableCell>
                                        <TableCell>{indicator.value}</TableCell>
                                        <TableCell>
                                          <Chip
                                            label={indicator.status?.toUpperCase()}
                                            color={
                                              indicator.status === "negative"
                                                ? "error"
                                                : indicator.status === "neutral"
                                                ? "warning"
                                                : "success"
                                            }
                                            size="small"
                                          />
                                        </TableCell>
                                      </TableRow>
                                    )
                                  )
                                ) : (
                                  <TableRow>
                                    <TableCell colSpan={3} align="center">
                                      No indicators found.
                                    </TableCell>
                                  </TableRow>
                                )}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </CardContent>
                      </Card>
                    )}

                    {/* 5. Compliance Status */}
                    {summary.compliance_status && (
                      <Card sx={{ mb: 3 }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" mb={2}>
                            <Shield size={20} style={{ marginRight: 8 }} />
                            <Typography variant="h6">
                              Compliance Status
                            </Typography>
                            <Chip
                              label={summary.compliance_status.overall?.toUpperCase()}
                              color={
                                summary.compliance_status.overall ===
                                "compliant"
                                  ? "default"
                                  : summary.compliance_status.overall ===
                                    "partial"
                                  ? "warning"
                                  : "error"
                              }
                              sx={{ ml: 2 }}
                            />
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              ml={2}
                            >
                              {summary.compliance_status.overall === "compliant"
                                ? "Compliant (coming soon)"
                                : summary.compliance_status.overall?.replace(
                                    "_",
                                    " "
                                  )}
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    )}

                    {/* Gemini Key Findings and Recommendations */}
                    {Array.isArray(summary.key_findings) &&
                      summary.key_findings.length > 0 && (
                        <Card
                          sx={{
                            mb: 3,
                            borderLeft: "6px solid #673ab7",
                            background: "#f8f6ff",
                          }}
                        >
                          <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                              <StarsIcon sx={{ color: "#673ab7", mr: 1 }} />
                              <Typography
                                variant="h6"
                                color="primary"
                                fontWeight={700}
                              >
                                Gemini Key Findings
                              </Typography>
                            </Box>
                            <List>
                              {summary.key_findings.map(
                                (finding: string, idx: number) => (
                                  <ListItem key={idx}>
                                    <ListItemIcon>
                                      <StarsIcon sx={{ color: "#9575cd" }} />
                                    </ListItemIcon>
                                    <ListItemText primary={finding} />
                                  </ListItem>
                                )
                              )}
                            </List>
                          </CardContent>
                        </Card>
                      )}
                    {Array.isArray(summary.recommendations) &&
                      summary.recommendations.length > 0 && (
                        <Card
                          sx={{
                            mb: 3,
                            borderLeft: "6px solid #1976d2",
                            background: "#f3f8ff",
                          }}
                        >
                          <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                              <StarsIcon sx={{ color: "#1976d2", mr: 1 }} />
                              <Typography
                                variant="h6"
                                color="primary"
                                fontWeight={700}
                              >
                                Gemini Recommendations
                              </Typography>
                            </Box>
                            <List>
                              {summary.recommendations.map(
                                (rec: string, idx: number) => (
                                  <ListItem key={idx}>
                                    <ListItemIcon>
                                      <StarsIcon sx={{ color: "#64b5f6" }} />
                                    </ListItemIcon>
                                    <ListItemText primary={rec} />
                                  </ListItem>
                                )
                              )}
                            </List>
                          </CardContent>
                        </Card>
                      )}
                  </Box>
                ) : null}
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
                    {searchResults.map((item: any, index: number) => (
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
