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
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ErrorIcon from "@mui/icons-material/Error";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { useGetManagementSummaryMutation } from "../store/api/analyticsApi";
import StarsIcon from "@mui/icons-material/Stars";
import { TrafficLightResponse } from "./TrafficLightQuery";
import DOMPurify from "dompurify";

interface TrafficLightResultProps {
  result: TrafficLightResponse;
}

// Map color strings to MUI color values
const colorMap: Record<string, "success" | "warning" | "error"> = {
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
  "Low-Operational": "success",
  "Medium-Economic": "warning",
  "Medium-Tax": "warning",
  "Medium-Legal": "warning",
  "Medium-Financial": "warning",
  "Medium-Regulatory": "warning",
  "Medium-Operational": "warning",
  "High-Legal": "error",
  "High-Financial": "error",
  "High-Regulatory": "error",
  "High-Operational": "error",
  Unknown: "default",
} as const;

// Map parameters to readable display names
const parameterMap = {
  turnover: "Financial Turnover",
  shareholding: "Shareholding Structure",
  bankruptcy: "Bankruptcy History",
  legal: "Legal Issues",
  regulatory: "Regulatory Compliance",
  dismissals: "Employee Dismissals",
  environmental: "Environmental Issues",
  operational: "Operational Changes",
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

// Add animation for risk badge
const riskBadgeAnimation = {
  animation: "scaleIn 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
  "@keyframes scaleIn": {
    from: { transform: "scale(0.8)", opacity: 0 },
    to: { transform: "scale(1)", opacity: 1 },
  },
};

// Define type for search result items
interface SearchResultItem {
  risk_level: string;
  date: string;
  title: string;
  summary?: string | null;
  source: string;
  confidence: number;
  url: string;
  [key: string]: any;
}

// Map parameter keys to risk_level substrings or other logic
const parameterToRiskLevelMap: Record<string, string[]> = {
  turnover: ["Financial"],
  shareholding: ["Shareholding"],
  bankruptcy: ["Bankruptcy"],
  legal: ["Legal"],
  regulatory: ["Regulatory"],
  dismissals: ["Dismissal", "Employee"],
  environmental: ["Environmental"],
  operational: ["Operational"],
};

// Helper to extract article title and heading from HTML or fields
const extractTitleAndHeading = (risk: any) => {
  // Prefer explicit fields if present
  let title = risk.title || "";
  let heading = risk.heading || "";

  // Try to extract <title> or first non-empty line
  if (!title) {
    const match = risk.description?.match(/<title>(.*?)<\/title>/i);
    if (match) {
      title = match[1];
    }
  }

  // Try to extract first <h1>, <h2>, or <h3>
  if (!heading) {
    const match = risk.description?.match(/<(h1|h2|h3)[^>]*>(.*?)<\/\1>/i);
    if (match) {
      heading = match[2];
    }
  }

  // Fallback: use first and second non-empty lines of text
  if (!title || !heading) {
    const tmp = document.createElement("div");
    tmp.innerHTML = risk.description || "";
    const lines = (tmp.textContent || tmp.innerText || "")
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!title && lines.length > 0) {
      title = lines[0];
    }
    if (!heading && lines.length > 1) {
      heading = lines[1];
    }
  }

  // Truncate for compactness
  const truncate = (str: string, n = 120) =>
    str && str.length > n ? str.slice(0, n) + "..." : str;

  return { title: truncate(title), heading: truncate(heading) };
};

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
  const [openRiskIdx, setOpenRiskIdx] = useState<number | null>(null);

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

  // --- Move getSourcesForParameter here so it can access searchResults ---
  function getSourcesForParameter(param: string): string {
    if (!searchResults.length) return "—";
    const relevantResults = searchResults.filter((result: any) =>
      parameterToRiskLevelMap[param]?.some((substr) =>
        (result.risk_level || "").toLowerCase().includes(substr.toLowerCase())
      )
    );
    const sources = [...new Set(relevantResults.map((r: any) => r.source))];
    if (sources.length === 0) return "—";
    if (sources.length <= 3) return sources.join(", ");
    return sources.slice(0, 3).join(", ") + `, +${sources.length - 3} more`;
  }

  // Add these just before the return statement in TrafficLightResult
  const highRiskCount = searchResults.filter(
    (r: SearchResultItem) => r.risk_level && r.risk_level.startsWith("High")
  ).length;
  const mediumRiskCount = searchResults.filter(
    (r: SearchResultItem) => r.risk_level && r.risk_level.startsWith("Medium")
  ).length;
  const lowRiskCount = searchResults.length - highRiskCount - mediumRiskCount;

  // Helper to get a plain text preview from HTML, stripping <img> tags
  const getTextPreview = (html: string, maxLength = 200) => {
    const tmp = document.createElement("div");
    tmp.innerHTML = html.replace(/<img[^>]*>/g, "");
    const text = tmp.textContent || tmp.innerText || "";
    return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
  };

  if (!hasSearchResults) {
    return (
      <Card
        sx={{ mt: 4, p: 4, textAlign: "center", boxShadow: 6, borderRadius: 3 }}
      >
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
        <Card
          sx={{ mt: 2, p: isMobile ? 1 : 3, boxShadow: 6, borderRadius: 3 }}
        >
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
                gap: 2,
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
                                      <strong>Company:</strong> {result.company}
                </Typography>
                <Chip
                  label={result.overall.toUpperCase()}
                  color={colorMap[result.overall as keyof typeof colorMap]}
                  icon={
                    result.overall === "green" ? (
                      <CheckCircleIcon />
                    ) : result.overall === "orange" ? (
                      <WarningAmberIcon />
                    ) : (
                      <ErrorIcon />
                    )
                  }
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
                    ...riskBadgeAnimation,
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

            <Typography
              variant="h6"
              component="h4"
              gutterBottom
              sx={{ mb: 2, mt: 4 }}
            >
              Detailed Parameters
            </Typography>

            {/* Parameter Table */}
            <TableContainer
              component={Paper}
              sx={{ mt: 4, mb: 2, boxShadow: 2, borderRadius: 2 }}
            >
              <Table size={isMobile ? "small" : "medium"}>
                <TableHead>
                  <TableRow>
                    <TableCell>Parameter</TableCell>
                    <TableCell>Risk Level</TableCell>
                    <TableCell>Data Source</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.keys(result.blocks).map((param) => {
                    const risk =
                      result.blocks[param as keyof typeof result.blocks];
                    const isGreen = risk === "green";
                    const riskIcon =
                      risk === "green" ? (
                        <CheckCircleIcon fontSize="small" color="success" />
                      ) : risk === "orange" ? (
                        <WarningAmberIcon fontSize="small" color="warning" />
                      ) : (
                        <ErrorIcon fontSize="small" color="error" />
                      );
                    return (
                      <TableRow
                        key={param}
                        sx={{
                          borderLeft: `6px solid ${
                            isGreen
                              ? theme.palette.success.main
                              : risk === "orange"
                              ? theme.palette.warning.main
                              : theme.palette.error.main
                          }`,
                          backgroundColor: isGreen
                            ? "#f9fff9"
                            : risk === "orange"
                            ? "#fffbe6"
                            : "#fff5f5",
                          transition: "background 0.2s",
                          cursor: "pointer",
                          "&:hover": { backgroundColor: "#f0f4ff" },
                        }}
                        // Optionally: onClick={() => setShowParamDetails(param)}
                      >
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {
                              dataSourcesMap[
                                param as keyof typeof dataSourcesMap
                              ]?.icon
                            }
                            <b>
                              {parameterMap[param as keyof typeof parameterMap]}
                            </b>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={risk.toUpperCase()}
                            color={colorMap[risk]}
                            icon={riskIcon}
                            sx={{ fontWeight: "bold" }}
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title={getSourcesForParameter(param)}>
                            <span>{getSourcesForParameter(param)}</span>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Add a summary bar above the table */}
            {hasSearchResults && (
              <Box
                sx={{
                  mt: 4,
                  mb: 2,
                  display: "flex",
                  gap: 3,
                  justifyContent: "center",
                }}
              >
                <Chip
                  label={`Total: ${searchResults.length}`}
                  color="primary"
                />
                <Chip
                  label={`High: ${highRiskCount}`}
                  color="error"
                  icon={<ErrorIcon fontSize="small" />}
                />
                <Chip
                  label={`Medium: ${mediumRiskCount}`}
                  color="warning"
                  icon={<WarningAmberIcon fontSize="small" />}
                />
                <Chip
                  label={`Low: ${lowRiskCount}`}
                  color="success"
                  icon={<CheckCircleIcon fontSize="small" />}
                />
              </Box>
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
                        {highRiskCount}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        High Risk
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="warning.main">
                        {mediumRiskCount}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Medium Risk
                      </Typography>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h4" color="success.main">
                        {lowRiskCount}
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
                      classification_results:
                        searchResults as SearchResultItem[],
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
                    {String(summaryError)}
                  </Alert>
                )}
                {/* Management Summary display */}
                {showSummary && summary ? (
                  <Box sx={{ mt: 4, textAlign: "left" }}>
                    {/* 1. Overall Risk Distribution - Enhanced */}
                    <Card
                      sx={{
                        mb: 4,
                        boxShadow: 4,
                        borderRadius: 3,
                        background:
                          "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                        border: "1px solid #dee2e6",
                      }}
                    >
                      <CardContent sx={{ p: 4 }}>
                        <Box display="flex" alignItems="center" gap={2} mb={3}>
                          <Box
                            sx={{
                              p: 2,
                              borderRadius: 2,
                              background:
                                "linear-gradient(135deg, #1976d2 0%, #1565c0 100%)",
                              color: "white",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              minWidth: 48,
                              height: 48,
                            }}
                          >
                            <DonutLargeIcon sx={{ fontSize: 28 }} />
                          </Box>
                          <Box sx={{ flex: 1 }}>
                            <Typography
                              variant="h5"
                              fontWeight={700}
                              gutterBottom
                            >
                              Overall Risk Assessment
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Comprehensive analysis based on{" "}
                              {searchResults.length} data points
                            </Typography>
                          </Box>
                          <Chip
                            label={
                              summary.overall_risk?.toUpperCase() || "UNKNOWN"
                            }
                            color={
                              summary.overall_risk === "red"
                                ? "error"
                                : summary.overall_risk === "orange"
                                ? "warning"
                                : "success"
                            }
                            sx={{
                              fontWeight: "bold",
                              fontSize: "1rem",
                              py: 1,
                              px: 2,
                              minHeight: 40,
                            }}
                          />
                        </Box>

                        {/* Risk Distribution Grid - Enhanced */}
                        {summary.risk_breakdown && (
                          <Box sx={{ mt: 3 }}>
                            <Typography
                              variant="h6"
                              gutterBottom
                              sx={{ mb: 2, fontWeight: 600 }}
                            >
                              Risk Breakdown by Category
                            </Typography>
                            <Grid container spacing={3}>
                              {Object.entries(summary.risk_breakdown).map(
                                ([category, breakdown]: [string, any]) => (
                                  <Grid
                                    item
                                    xs={12}
                                    sm={6}
                                    md={4}
                                    key={category}
                                  >
                                    <Card
                                      variant="outlined"
                                      sx={{
                                        p: 3,
                                        textAlign: "center",
                                        height: "100%",
                                        transition: "all 0.3s ease",
                                        cursor: "pointer",
                                        "&:hover": {
                                          transform: "translateY(-2px)",
                                          boxShadow: 3,
                                          borderColor: "primary.main",
                                        },
                                      }}
                                    >
                                      <Box sx={{ mb: 2 }}>
                                        <Typography
                                          variant="subtitle1"
                                          gutterBottom
                                          sx={{
                                            fontWeight: 600,
                                            color: "primary.main",
                                          }}
                                        >
                                          {category.charAt(0).toUpperCase() +
                                            category.slice(1)}
                                        </Typography>
                                        <Chip
                                          label={
                                            breakdown.level?.toUpperCase() ||
                                            "UNKNOWN"
                                          }
                                          color={
                                            breakdown.level === "red"
                                              ? "error"
                                              : breakdown.level === "orange"
                                              ? "warning"
                                              : "success"
                                          }
                                          sx={{
                                            fontWeight: "bold",
                                            mb: 2,
                                            minWidth: 80,
                                          }}
                                        />
                                      </Box>

                                      <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        sx={{ mb: 2, minHeight: 40 }}
                                      >
                                        {breakdown.reasoning}
                                      </Typography>

                                      {/* Confidence Indicator */}
                                      <Box sx={{ mb: 2 }}>
                                        <Typography
                                          variant="caption"
                                          color="text.secondary"
                                          display="block"
                                        >
                                          Confidence Level
                                        </Typography>
                                        <LinearProgress
                                          variant="determinate"
                                          value={
                                            (breakdown.confidence || 0) * 100
                                          }
                                          sx={{
                                            height: 8,
                                            borderRadius: 4,
                                            backgroundColor: "grey.200",
                                            "& .MuiLinearProgress-bar": {
                                              borderRadius: 4,
                                            },
                                          }}
                                        />
                                        <Typography
                                          variant="caption"
                                          color="text.secondary"
                                        >
                                          {Math.round(
                                            (breakdown.confidence || 0) * 100
                                          )}
                                          %
                                        </Typography>
                                      </Box>

                                      {/* Evidence Preview */}
                                      {Array.isArray(breakdown.evidence) &&
                                        breakdown.evidence.length > 0 && (
                                          <Accordion
                                            sx={{ boxShadow: "none", mt: 1 }}
                                          >
                                            <AccordionSummary
                                              expandIcon={
                                                <ChevronDown size={16} />
                                              }
                                              sx={{
                                                minHeight: 32,
                                                "& .MuiAccordionSummary-content":
                                                  {
                                                    margin: 0,
                                                  },
                                              }}
                                            >
                                              <Typography
                                                variant="caption"
                                                color="primary"
                                              >
                                                View Evidence (
                                                {breakdown.evidence.length})
                                              </Typography>
                                            </AccordionSummary>
                                            <AccordionDetails sx={{ pt: 0 }}>
                                              <Box
                                                sx={{
                                                  maxHeight: 120,
                                                  overflow: "auto",
                                                }}
                                              >
                                                {breakdown.evidence
                                                  .slice(0, 3)
                                                  .map(
                                                    (
                                                      ev: string,
                                                      idx: number
                                                    ) => (
                                                      <Typography
                                                        key={idx}
                                                        variant="caption"
                                                        display="block"
                                                        sx={{
                                                          mb: 1,
                                                          p: 1,
                                                          bgcolor: "grey.50",
                                                          borderRadius: 1,
                                                          fontSize: "0.75rem",
                                                        }}
                                                      >
                                                        • {ev}
                                                      </Typography>
                                                    )
                                                  )}
                                              </Box>
                                            </AccordionDetails>
                                          </Accordion>
                                        )}
                                    </Card>
                                  </Grid>
                                )
                              )}
                            </Grid>
                          </Box>
                        )}
                      </CardContent>
                    </Card>

                    {/* 2. Executive Summary - Enhanced */}
                    <Card
                      sx={{
                        mb: 4,
                        boxShadow: 4,
                        borderRadius: 3,
                        background:
                          "linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)",
                        border: "1px solid #ffcc02",
                      }}
                    >
                      <CardContent sx={{ p: 4 }}>
                        <Box display="flex" alignItems="center" gap={2} mb={3}>
                          <Box
                            sx={{
                              p: 2,
                              borderRadius: 2,
                              background:
                                "linear-gradient(135deg, #ff9800 0%, #f57c00 100%)",
                              color: "white",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              minWidth: 48,
                              height: 48,
                            }}
                          >
                            <StarsIcon sx={{ fontSize: 28 }} />
                          </Box>
                          <Typography variant="h5" fontWeight={700}>
                            Executive Summary
                          </Typography>
                        </Box>

                        <Typography
                          variant="body1"
                          sx={{
                            mb: 2,
                            lineHeight: 1.7,
                            fontSize: "1.1rem",
                            color: "text.primary",
                          }}
                        >
                          {summary.executive_summary}
                        </Typography>
                      </CardContent>
                    </Card>

                    {/* 3. Key Risk Items - Enhanced */}
                    {Array.isArray(summary.key_risks) &&
                      summary.key_risks.length > 0 && (
                        <Card
                          sx={{
                            mb: 4,
                            boxShadow: 4,
                            borderRadius: 3,
                            background:
                              "linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)",
                            border: "1px solid #ef5350",
                          }}
                        >
                          <CardContent sx={{ p: 4 }}>
                            <Box
                              display="flex"
                              alignItems="center"
                              gap={2}
                              mb={3}
                            >
                              <Box
                                sx={{
                                  p: 2,
                                  borderRadius: 2,
                                  background:
                                    "linear-gradient(135deg, #f44336 0%, #d32f2f 100%)",
                                  color: "white",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  minWidth: 48,
                                  height: 48,
                                }}
                              >
                                <ErrorIcon sx={{ fontSize: 28 }} />
                              </Box>
                              <Typography variant="h5" fontWeight={700}>
                                Key Risk Items
                              </Typography>
                            </Box>

                            <Accordion sx={{ boxShadow: "none" }}>
                              <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                sx={{
                                  bgcolor: "rgba(255,255,255,0.7)",
                                  borderRadius: 2,
                                  mb: 2,
                                }}
                              >
                                <Typography
                                  variant="subtitle1"
                                  fontWeight={600}
                                >
                                  View {summary.key_risks.length} Risk Items
                                </Typography>
                              </AccordionSummary>
                              <AccordionDetails sx={{ p: 0 }}>
                                <TableContainer
                                  component={Paper}
                                  variant="outlined"
                                  sx={{ borderRadius: 2 }}
                                >
                                  <Table size="small">
                                    <TableHead>
                                      <TableRow sx={{ bgcolor: "grey.50" }}>
                                        <TableCell sx={{ fontWeight: 600 }}>
                                          Risk Type
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>
                                          Description
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>
                                          Severity
                                        </TableCell>
                                        <TableCell sx={{ fontWeight: 600 }}>
                                          Recommendations
                                        </TableCell>
                                      </TableRow>
                                    </TableHead>
                                    <TableBody>
                                      {summary.key_risks.map(
                                        (risk: any, idx: number) => (
                                          <TableRow
                                            key={idx}
                                            sx={{
                                              "&:nth-of-type(odd)": {
                                                bgcolor:
                                                  "rgba(255,255,255,0.5)",
                                              },
                                            }}
                                          >
                                            <TableCell>
                                              <Typography
                                                variant="body2"
                                                fontWeight={500}
                                              >
                                                {risk.risk_type}
                                              </Typography>
                                            </TableCell>
                                            <TableCell>
                                              {(() => {
                                                const { title, heading } =
                                                  extractTitleAndHeading(risk);
                                                return (
                                                  <>
                                                    <strong>Article:</strong>{" "}
                                                    {title || "-"}
                                                    <br />
                                                    <strong>
                                                      Heading:
                                                    </strong>{" "}
                                                    {heading || "-"}
                                                  </>
                                                );
                                              })()}
                                            </TableCell>
                                            <TableCell>
                                              <Chip
                                                label={
                                                  risk.severity?.toUpperCase() ||
                                                  "UNKNOWN"
                                                }
                                                color={
                                                  risk.severity === "high"
                                                    ? "error"
                                                    : risk.severity === "medium"
                                                    ? "warning"
                                                    : "success"
                                                }
                                                size="small"
                                                sx={{ fontWeight: 600 }}
                                              />
                                            </TableCell>
                                            <TableCell>
                                              <Typography
                                                variant="body2"
                                                color="text.secondary"
                                              >
                                                {Array.isArray(
                                                  risk.recommendations
                                                )
                                                  ? risk.recommendations.join(
                                                      ", "
                                                    )
                                                  : "-"}
                                              </Typography>
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

                    {/* 4. Financial Health - Enhanced */}
                    {summary.financial_health && (
                      <Card
                        sx={{
                          mb: 4,
                          boxShadow: 4,
                          borderRadius: 3,
                          background:
                            "linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)",
                          border: "1px solid #4caf50",
                        }}
                      >
                        <CardContent sx={{ p: 4 }}>
                          <Box
                            display="flex"
                            alignItems="center"
                            gap={2}
                            mb={3}
                          >
                            <Box
                              sx={{
                                p: 2,
                                borderRadius: 2,
                                background:
                                  "linear-gradient(135deg, #4caf50 0%, #388e3c 100%)",
                                color: "white",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                minWidth: 48,
                                height: 48,
                              }}
                            >
                              <DollarSign size={24} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="h5" fontWeight={700}>
                                Financial Health
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Key financial indicators and performance metrics
                              </Typography>
                            </Box>
                            <Chip
                              label={
                                summary.financial_health.status?.toUpperCase() ||
                                "UNKNOWN"
                              }
                              color={
                                summary.financial_health.status === "critical"
                                  ? "error"
                                  : summary.financial_health.status ===
                                    "concerning"
                                  ? "warning"
                                  : "success"
                              }
                              sx={{ fontWeight: "bold" }}
                            />
                          </Box>

                          <TableContainer
                            component={Paper}
                            variant="outlined"
                            sx={{ borderRadius: 2 }}
                          >
                            <Table size="small">
                              <TableHead>
                                <TableRow sx={{ bgcolor: "grey.50" }}>
                                  <TableCell sx={{ fontWeight: 600 }}>
                                    Indicator
                                  </TableCell>
                                  <TableCell sx={{ fontWeight: 600 }}>
                                    Value
                                  </TableCell>
                                  <TableCell sx={{ fontWeight: 600 }}>
                                    Status
                                  </TableCell>
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
                                      <TableRow
                                        key={idx}
                                        sx={{
                                          "&:nth-of-type(odd)": {
                                            bgcolor: "rgba(255,255,255,0.5)",
                                          },
                                        }}
                                      >
                                        <TableCell>
                                          <Typography
                                            variant="body2"
                                            fontWeight={500}
                                          >
                                            {indicator.indicator}
                                          </Typography>
                                        </TableCell>
                                        <TableCell>
                                          <Typography variant="body2">
                                            {indicator.value}
                                          </Typography>
                                        </TableCell>
                                        <TableCell>
                                          <Chip
                                            label={
                                              indicator.status?.toUpperCase() ||
                                              "UNKNOWN"
                                            }
                                            color={
                                              indicator.status === "negative"
                                                ? "error"
                                                : indicator.status === "neutral"
                                                ? "warning"
                                                : "success"
                                            }
                                            size="small"
                                            sx={{ fontWeight: 600 }}
                                          />
                                        </TableCell>
                                      </TableRow>
                                    )
                                  )
                                ) : (
                                  <TableRow>
                                    <TableCell colSpan={3} align="center">
                                      <Typography
                                        variant="body2"
                                        color="text.secondary"
                                      >
                                        No financial indicators available
                                      </Typography>
                                    </TableCell>
                                  </TableRow>
                                )}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </CardContent>
                      </Card>
                    )}

                    {/* 5. Gemini Key Findings - Enhanced */}
                    {Array.isArray(summary.key_findings) &&
                      summary.key_findings.length > 0 && (
                        <Card
                          sx={{
                            mb: 4,
                            boxShadow: 4,
                            borderRadius: 3,
                            background:
                              "linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)",
                            border: "1px solid #9c27b0",
                          }}
                        >
                          <CardContent sx={{ p: 4 }}>
                            <Box
                              display="flex"
                              alignItems="center"
                              gap={2}
                              mb={3}
                            >
                              <Box
                                sx={{
                                  p: 2,
                                  borderRadius: 2,
                                  background:
                                    "linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)",
                                  color: "white",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  minWidth: 48,
                                  height: 48,
                                }}
                              >
                                <StarsIcon sx={{ fontSize: 28 }} />
                              </Box>
                              <Typography
                                variant="h5"
                                fontWeight={700}
                                color="primary"
                              >
                                Key Findings
                              </Typography>
                            </Box>

                            <List sx={{ p: 0 }}>
                              {summary.key_findings.map(
                                (finding: string, idx: number) => (
                                  <ListItem
                                    key={idx}
                                    sx={{
                                      p: 2,
                                      mb: 1,
                                      bgcolor: "rgba(255,255,255,0.7)",
                                      borderRadius: 2,
                                      border:
                                        "1px solid rgba(156, 39, 176, 0.2)",
                                    }}
                                  >
                                    <ListItemIcon>
                                      <StarsIcon sx={{ color: "#9c27b0" }} />
                                    </ListItemIcon>
                                    <ListItemText
                                      primary={finding}
                                      primaryTypographyProps={{
                                        variant: "body1",
                                        fontWeight: 500,
                                      }}
                                    />
                                  </ListItem>
                                )
                              )}
                            </List>
                          </CardContent>
                        </Card>
                      )}

                    {/* 6. Gemini Recommendations - Enhanced */}
                    {Array.isArray(summary.recommendations) &&
                      summary.recommendations.length > 0 && (
                        <Card
                          sx={{
                            mb: 4,
                            boxShadow: 4,
                            borderRadius: 3,
                            background:
                              "linear-gradient(135deg, #e8f4fd 0%, #bbdefb 100%)",
                            border: "1px solid #1976d2",
                          }}
                        >
                          <CardContent sx={{ p: 4 }}>
                            <Box
                              display="flex"
                              alignItems="center"
                              gap={2}
                              mb={3}
                            >
                              <Box
                                sx={{
                                  p: 2,
                                  borderRadius: 2,
                                  background:
                                    "linear-gradient(135deg, #1976d2 0%, #1565c0 100%)",
                                  color: "white",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  minWidth: 48,
                                  height: 48,
                                }}
                              >
                                <StarsIcon sx={{ fontSize: 28 }} />
                              </Box>
                              <Typography
                                variant="h5"
                                fontWeight={700}
                                color="primary"
                              >
                                Recommendations
                              </Typography>
                            </Box>

                            <List sx={{ p: 0 }}>
                              {summary.recommendations.map(
                                (rec: string, idx: number) => (
                                  <ListItem
                                    key={idx}
                                    sx={{
                                      p: 2,
                                      mb: 1,
                                      bgcolor: "rgba(255,255,255,0.7)",
                                      borderRadius: 2,
                                      border:
                                        "1px solid rgba(25, 118, 210, 0.2)",
                                    }}
                                  >
                                    <ListItemIcon>
                                      <StarsIcon sx={{ color: "#1976d2" }} />
                                    </ListItemIcon>
                                    <ListItemText
                                      primary={rec}
                                      primaryTypographyProps={{
                                        variant: "body1",
                                        fontWeight: 500,
                                      }}
                                    />
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
                    {searchResults.map(
                      (item: SearchResultItem, index: number) => (
                        <TableRow key={index} hover>
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
                              <Accordion sx={{ boxShadow: "none", mt: 1 }}>
                                <AccordionSummary expandIcon={<ChevronDown />}>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    Show snippet
                                  </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography
                                    variant="caption"
                                    color="text.secondary"
                                  >
                                    {item.summary}
                                  </Typography>
                                </AccordionDetails>
                              </Accordion>
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
                              icon={
                                item.risk_level.startsWith("High") ? (
                                  <ErrorIcon fontSize="small" />
                                ) : item.risk_level.startsWith("Medium") ? (
                                  <WarningAmberIcon fontSize="small" />
                                ) : item.risk_level.startsWith("Low") ? (
                                  <CheckCircleIcon fontSize="small" />
                                ) : (
                                  <InfoOutlinedIcon fontSize="small" />
                                )
                              }
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
                      )
                    )}
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
