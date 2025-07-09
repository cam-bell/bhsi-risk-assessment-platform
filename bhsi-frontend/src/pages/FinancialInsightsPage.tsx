import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Tabs,
  Tab,
  Paper,
  Alert,
  Tooltip,
  Avatar,
  CircularProgress,
  TextField,
  Container,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
} from "@mui/material";
import {
  BarChart3,
  FileText,
  TrendingUp,
  GitCompare,
  Building2,
  AlertTriangle,
  Users,
  Calendar,
  Globe,
  Activity,
  PieChart,
  Target,
  Shield,
  TrendingDown,
  TrendingUp as TrendingUpIcon,
  Bot,
} from "lucide-react";
import ManagementSummary from "../components/ManagementSummary";
import { useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import axios from "axios";
import RAGChatbot from "../components/RAGChatbot";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://bhsi-backend-iee4puj5na-ew.a.run.app/api/v1";

const riskLevelColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case "red":
    case "high":
      return "error";
    case "orange":
    case "medium":
      return "warning";
    case "green":
    case "low":
      return "success";
    default:
      return "info";
  }
};

const formatNumber = (num: any) => {
  if (num === null || num === undefined || isNaN(num)) return "N/A";
  if (typeof num === "string" && num.match(/^\d+$/)) num = Number(num);
  if (typeof num === "number") {
    if (Math.abs(num) >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (Math.abs(num) >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (Math.abs(num) >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toLocaleString()}`;
  }
  return num;
};

const formatDate = (date: string) => {
  if (!date) return "N/A";
  const d = new Date(date);
  if (isNaN(d.getTime())) return date;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

const RenderValue: React.FC<{ value: any }> = ({ value }) => {
  if (value === null || value === undefined) return <>N/A</>;
  if (typeof value === "number") return <>{formatNumber(value)}</>;
  if (typeof value === "string") return <>{value}</>;
  if (Array.isArray(value)) {
    if (value.length === 0) return <>[]</>;
    // If array of primitives
    if (value.every((v) => typeof v !== "object")) {
      return <>{value.join(", ")}</>;
    }
    // Array of objects: render as subtable
    return (
      <Table size="small" sx={{ mt: 1, mb: 1 }}>
        <TableBody>
          {value.map((item, idx) => (
            <TableRow key={idx}>
              <TableCell colSpan={2}>
                <RenderValue value={item} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }
  if (typeof value === "object") {
    return (
      <Table size="small" sx={{ mt: 1, mb: 1 }}>
        <TableBody>
          {Object.entries(value).map(([k, v]) => (
            <TableRow key={k}>
              <TableCell>{k}</TableCell>
              <TableCell>
                <RenderValue value={v} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }
  return <>{String(value)}</>;
};

const ExpandablePanel: React.FC<{ title: string; data: any }> = ({
  title,
  data,
}) => {
  const [open, setOpen] = useState(false);
  if (!data || typeof data !== "object" || Object.keys(data).length === 0)
    return null;
  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box
        sx={{ display: "flex", alignItems: "center", cursor: "pointer" }}
        onClick={() => setOpen((o) => !o)}
      >
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="primary">
          {open ? "Hide" : "Show"}
        </Typography>
      </Box>
      {open && <RenderValue value={data} />}
    </Paper>
  );
};

const SummaryTab: React.FC<{ summary: any; loading: boolean }> = ({
  summary,
  loading,
}) => (
  <Box>
    {loading ? (
      <CircularProgress />
    ) : summary && typeof summary === "object" ? (
      <>
        {/* Handle error cases */}
        {summary.error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {summary.error}
            </Typography>
          </Alert>
        )}

        {/* Show suggestions if available */}
        {summary.suggestions && Array.isArray(summary.suggestions) && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Suggestions:
            </Typography>
            <ul>
              {summary.suggestions.map((suggestion: string, index: number) => (
                <li key={index}>
                  <Typography variant="body2">{suggestion}</Typography>
                </li>
              ))}
            </ul>
          </Paper>
        )}

        <Typography variant="h5" gutterBottom>
          Executive Summary
        </Typography>

        {/* Data availability indicator */}
        {summary.data_availability && (
          <Alert
            severity={
              summary.data_availability.data_completeness > 70
                ? "success"
                : summary.data_availability.data_completeness > 30
                ? "warning"
                : "info"
            }
            sx={{ mb: 2 }}
          >
            <Typography variant="body2">
              Summary based on {summary.data_availability.data_completeness}%
              data completeness
              {summary.data_note && ` - ${summary.data_note}`}
            </Typography>
          </Alert>
        )}

        <Paper sx={{ p: 3, mb: 2, background: "#f9f9f9" }}>
          <Typography variant="body1" sx={{ whiteSpace: "pre-line" }}>
            {summary.summary || summary.ai_summary || summary}
          </Typography>
        </Paper>

        <Typography variant="subtitle2" color="text.secondary">
          Company: {summary.company} ({summary.ticker})
        </Typography>
      </>
    ) : (
      <Typography color="text.secondary">No summary available.</Typography>
    )}
  </Box>
);

const RiskTab: React.FC<{ risk: any; loading: boolean }> = ({
  risk,
  loading,
}) => {
  // Add defensive check for risk data
  if (!risk || typeof risk !== "object") {
    return (
      <Box>
        <Typography color="text.secondary">
          No risk report available.
        </Typography>
      </Box>
    );
  }

  // Fixed list of key score factors for underwriters
  const scoreFactorFields: { key: string; label: string }[] = [
    { key: "debtToEquity", label: "Debt to Equity" },
    { key: "totalRevenue", label: "Total Revenue" },
    { key: "netIncome", label: "Net Income" },
    { key: "currentRatio", label: "Current Ratio" },
    { key: "returnOnEquity", label: "Return on Equity" },
    { key: "red_news_count", label: "Red News Count" },
    { key: "freeCashFlow", label: "Free Cash Flow" },
  ];

  // Try to extract these from risk.scoreFactors or risk.financials
  const getScoreFactor = (key: string) => {
    if (!risk) return undefined;
    if (risk.scoreFactors && risk.scoreFactors[key] !== undefined)
      return risk.scoreFactors[key];
    if (risk.financials && risk.financials[key] !== undefined)
      return risk.financials[key];
    // Special case for freeCashFlow in cashflow object
    if (
      key === "freeCashFlow" &&
      risk.scoreFactors &&
      risk.scoreFactors.cashflow &&
      typeof risk.scoreFactors.cashflow === "object"
    ) {
      const cflow = risk.scoreFactors.cashflow;
      const latest = Object.keys(cflow).sort().reverse()[0];
      if (
        latest &&
        cflow[latest] &&
        cflow[latest]["Free Cash Flow"] !== undefined
      ) {
        return cflow[latest]["Free Cash Flow"];
      }
    }
    return undefined;
  };

  return (
    <Box>
      {loading ? (
        <CircularProgress />
      ) : (
        <>
          {/* Handle error cases */}
          {risk.error && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                {risk.error}
              </Typography>
              {risk.data_note && (
                <Typography variant="body2">{risk.data_note}</Typography>
              )}
            </Alert>
          )}

          {/* Show suggestions if available */}
          {risk.suggestions && Array.isArray(risk.suggestions) && (
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggestions:
              </Typography>
              <ul>
                {risk.suggestions.map((suggestion: string, index: number) => (
                  <li key={index}>
                    <Typography variant="body2">{suggestion}</Typography>
                  </li>
                ))}
              </ul>
            </Paper>
          )}

          <Stack direction="row" spacing={2} alignItems="center" mb={2}>
            <Typography variant="h5">Risk Report</Typography>
            <Chip
              label={risk.riskLevel || risk.risk_level || "Unknown"}
              color={riskLevelColor(risk.riskLevel || risk.risk_level)}
              sx={{
                fontWeight: 600,
                fontSize: "1rem",
                textTransform: "capitalize",
              }}
              aria-label={`Risk level: ${risk.riskLevel}`}
            />
          </Stack>

          {/* Data availability indicator */}
          {risk.data_availability && (
            <Alert
              severity={
                risk.data_availability.data_completeness > 70
                  ? "success"
                  : risk.data_availability.data_completeness > 30
                  ? "warning"
                  : "info"
              }
              sx={{ mb: 2 }}
            >
              <Typography variant="body2">
                Risk assessment based on{" "}
                {risk.data_availability.data_completeness}% data completeness
                {risk.data_note && ` - ${risk.data_note}`}
              </Typography>
            </Alert>
          )}

          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Score Factors
            </Typography>
            <Table size="small">
              <TableBody>
                {scoreFactorFields.map(({ key, label }) => (
                  <TableRow key={key}>
                    <TableCell>{label}</TableCell>
                    <TableCell>
                      {getScoreFactor(key) !== undefined &&
                      getScoreFactor(key) !== null
                        ? formatNumber(getScoreFactor(key))
                        : "N/A"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>

          {risk.ai_risk_summary && (
            <Paper
              sx={{
                p: 2,
                mb: 3,
                background: "#f9f9f9",
                borderLeft: "5px solid #1976d2",
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                AI Risk Assessment
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
                {risk.ai_risk_summary}
              </Typography>
            </Paper>
          )}

          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent News
            </Typography>
            {risk.news && Array.isArray(risk.news) && risk.news.length > 0 ? (
              <Stack spacing={1}>
                {risk.news.map((item: any, idx: number) => (
                  <Alert
                    key={idx}
                    severity={riskLevelColor(item.sentiment)}
                    icon={false}
                    sx={{ fontWeight: 500 }}
                  >
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        fontWeight: 600,
                        color: "inherit",
                        textDecoration: "underline",
                      }}
                    >
                      {item.headline}
                    </a>
                    {item.date && (
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        {formatDate(item.date)}
                      </Typography>
                    )}
                  </Alert>
                ))}
              </Stack>
            ) : (
              <Typography color="text.secondary">
                No recent news available.
              </Typography>
            )}
          </Paper>
        </>
      )}
    </Box>
  );
};

const FinancialsTab: React.FC<{ financials: any; loading: boolean }> = ({
  financials,
  loading,
}) => {
  // Show only high-level metrics in summary, and expandable panels for details
  if (loading) return <CircularProgress />;

  if (!financials || typeof financials !== "object") {
    return (
      <Typography color="text.secondary">
        No financial data available.
      </Typography>
    );
  }

  // Handle error cases with helpful information
  if (financials.error) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            {financials.error}
          </Typography>
          {financials.data_note && (
            <Typography variant="body2">{financials.data_note}</Typography>
          )}
        </Alert>

        {financials.suggestions && Array.isArray(financials.suggestions) && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Suggestions:
            </Typography>
            <ul>
              {financials.suggestions.map(
                (suggestion: string, index: number) => (
                  <li key={index}>
                    <Typography variant="body2">{suggestion}</Typography>
                  </li>
                )
              )}
            </ul>
          </Paper>
        )}

        <Typography variant="h5" gutterBottom>
          Financial Data - Limited Information
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Company</TableCell>
                <TableCell>
                  {financials.longName || financials.ticker || "Unknown"}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Ticker</TableCell>
                <TableCell>{financials.ticker || "N/A"}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Data Status</TableCell>
                <TableCell>Limited or unavailable</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </Paper>
      </Box>
    );
  }

  // Extract high-level fields
  const summaryFields = [
    "longName",
    "ticker",
    "sector",
    "industry",
    "country",
    "marketCap",
    "totalRevenue",
    "netIncome",
    "debtToEquity",
    "currentRatio",
    "returnOnEquity",
    "grossProfits",
    "operatingCashflow",
    "freeCashFlow",
    "currentPrice",
    "currency",
  ];

  const summaryData = summaryFields
    .map((k) => [k, financials[k]])
    .filter(([_, v]) => v !== undefined && v !== null);

  // Find nested objects for details
  const details = [
    ["Financials", financials.financials],
    ["Balance Sheet", financials.balanceSheet],
    ["Cash Flow", financials.cashflow],
    ["Recommendations", financials.recommendations],
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Financial Data
      </Typography>

      {/* Data availability indicator */}
      {financials.data_availability && (
        <Alert
          severity={
            financials.data_availability.data_completeness > 70
              ? "success"
              : financials.data_availability.data_completeness > 30
              ? "warning"
              : "info"
          }
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            Data completeness: {financials.data_availability.data_completeness}%
            {financials.data_note && ` - ${financials.data_note}`}
          </Typography>
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Table size="small">
          <TableBody>
            {summaryData.length > 0 ? (
              summaryData.map(([k, v]) => (
                <TableRow key={k}>
                  <TableCell sx={{ fontWeight: 600 }}>
                    {k
                      .replace(/([A-Z])/g, " $1")
                      .replace(/^./, (str: string) => str.toUpperCase())}
                  </TableCell>
                  <TableCell>
                    {typeof v === "number" ? formatNumber(v) : v ?? "N/A"}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={2}>
                  <Typography color="text.secondary">
                    Basic financial metrics not available for this ticker.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      {details.map(([title, data]) => (
        <ExpandablePanel
          key={title as string}
          title={title as string}
          data={data}
        />
      ))}

      {financials.ai_insights && (
        <Paper sx={{ p: 2, background: "#f9f9f9" }}>
          <Typography variant="subtitle1">AI Financial Insights</Typography>
          <Typography variant="body2" sx={{ whiteSpace: "pre-line" }}>
            {financials.ai_insights}
          </Typography>
        </Paper>
      )}

      {financials.business_summary && (
        <Paper sx={{ p: 2, mt: 2, background: "#f9f9f9" }}>
          <Typography variant="subtitle1">Business Summary</Typography>
          <Typography variant="body2">{financials.business_summary}</Typography>
        </Paper>
      )}
    </Box>
  );
};

const FinancialInsightsPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [financials, setFinancials] = useState<any>(null);
  const [risk, setRisk] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);

  const handleSearch = async () => {
    setError(null);
    setLoading(true);
    setFinancials(null);
    setRisk(null);
    setSummary(null);
    try {
      const [finRes, riskRes, sumRes] = await Promise.all([
        fetch(
          `${API_BASE_URL}/finance/financials?query=${encodeURIComponent(
            query
          )}`
        ).then((r) => r.json()),
        fetch(
          `${API_BASE_URL}/finance/risk?query=${encodeURIComponent(query)}`
        ).then((r) => r.json()),
        fetch(
          `${API_BASE_URL}/finance/summary?query=${encodeURIComponent(query)}`
        ).then((r) => r.json()),
      ]);
      setFinancials(finRes);
      setRisk(riskRes);
      setSummary(sumRes);
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1000, mx: "auto" }}>
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Financial Insights
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Search for a company by name or ticker to view financial risk data,
          AI-generated executive summaries, and key indicators for D&O
          underwriting.
        </Typography>
        <Divider sx={{ my: 3 }} />
        <Box
          component="form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          sx={{ display: "flex", gap: 2, mb: 3, alignItems: "center" }}
        >
          <TextField
            label="Company Name or Ticker"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant="outlined"
            size="small"
            sx={{ flex: 1 }}
            autoFocus
            inputProps={{ "aria-label": "Company Name or Ticker" }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !query.trim()}
            aria-label="Search"
          >
            Search
          </Button>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        <Tabs value={tab} onChange={(_, v) => setTab(v ?? 0)} sx={{ mb: 3 }}>
          <Tab label="Summary" />
          <Tab label="Risk Report" />
          <Tab label="Financials" />
        </Tabs>
        <Box>
          {tab === 0 && <SummaryTab summary={summary} loading={loading} />}
          {tab === 1 && <RiskTab risk={risk} loading={loading} />}
          {tab === 2 && (
            <FinancialsTab financials={financials} loading={loading} />
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default FinancialInsightsPage;
