import { useState, useEffect } from "react";
import {
  Box,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Typography,
  Tooltip,
  Zoom,
  Fab,
  Snackbar,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  ToggleButton,
  ToggleButtonGroup,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  ListItemText,
  FormControlLabel,
  Chip,
} from "@mui/material";
import {
  Search,
  Save,
  Database,
  Newspaper,
  Globe,
  Calendar,
  ChevronDown,
} from "lucide-react";
import TrafficLightResult from "./TrafficLightResult";
import SavedResults from "./SavedResults";
import BatchUpload from "./BatchUpload";
import { useAuth } from "../auth/useAuth";
import { useCompanies } from "../context/CompaniesContext";
import {
  useSearchCompanyMutation,
  SearchResponse,
} from "../store/api/riskAssessmentApi";
import { useGetManagementSummaryMutation } from "../store/api/analyticsApi";

// Type for API response
export interface TrafficLightResponse {
  company: string;
  vat: string;
  overall: "green" | "orange" | "red";
  blocks: {
    turnover: "green" | "orange" | "red";
    shareholding: "green" | "orange" | "red";
    bankruptcy: "green" | "orange" | "red";
    legal: "green" | "orange" | "red";
  };
  dataSource?: "BOE" | "NewsAPI" | "both";
  dateRange?: {
    type: "preset" | "custom";
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
  // Add backend search results
  searchResults?: SearchResponse;
}

export interface SavedResult extends TrafficLightResponse {
  savedAt: string;
  savedBy: string;
}

// Function to convert backend search results to traffic light format
const convertSearchResultsToTrafficLight = (
  searchResponse: SearchResponse
): TrafficLightResponse => {
  const results = searchResponse.results;

  // Analyze risk levels from search results
  const highRiskCount = results.filter(
    (r) => r.risk_level === "High-Legal" || r.risk_level === "High-Financial"
  ).length;
  const mediumRiskCount = results.filter(
    (r) =>
      r.risk_level === "Medium-Legal" || r.risk_level === "Medium-Financial"
  ).length;
  const lowRiskCount = results.filter(
    (r) => r.risk_level === "Low-Legal" || r.risk_level === "Low-Financial"
  ).length;

  // Determine overall risk based on results
  let overall: "green" | "orange" | "red" = "green";
  if (highRiskCount > 0) {
    overall = "red";
  } else if (mediumRiskCount > 0) {
    overall = "orange";
  }

  // Analyze by category (simplified mapping)
  const legalResults = results.filter((r) => r.risk_level.includes("Legal"));
  const financialResults = results.filter((r) =>
    r.risk_level.includes("Financial")
  );

  const getCategoryRisk = (
    categoryResults: any[]
  ): "green" | "orange" | "red" => {
    const highRisk = categoryResults.filter((r) =>
      r.risk_level.startsWith("High")
    ).length;
    const mediumRisk = categoryResults.filter((r) =>
      r.risk_level.startsWith("Medium")
    ).length;

    if (highRisk > 0) return "red";
    if (mediumRisk > 0) return "orange";
    return "green";
  };

  return {
    company: searchResponse.company_name,
    vat: "N/A", // Backend doesn't provide VAT
    overall,
    blocks: {
      turnover: getCategoryRisk(financialResults),
      shareholding: "green", // Not directly available from search
      bankruptcy: getCategoryRisk(financialResults),
      legal: getCategoryRisk(legalResults),
    },
    searchResults: searchResponse,
  };
};

const RSS_FEEDS = [
  { value: "elpais", label: "El País" },
  { value: "expansion", label: "Expansión" },
  { value: "elmundo", label: "El Mundo" },
  { value: "abc", label: "ABC" },
  { value: "lavanguardia", label: "La Vanguardia" },
  { value: "elconfidencial", label: "El Confidencial" },
  { value: "eldiario", label: "El Diario" },
  { value: "europapress", label: "Europa Press" },
];

interface TrafficLightQueryProps {
  onRiskResult?: (company: string, executiveSummary: string) => void;
}

const TrafficLightQuery: React.FC<TrafficLightQueryProps> = ({
  onRiskResult,
}) => {
  const { user } = useAuth();
  const { addAssessedCompany } = useCompanies();
  const [query, setQuery] = useState("");
  const [boeEnabled, setBoeEnabled] = useState(true);
  const [newsEnabled, setNewsEnabled] = useState(true);
  const [rssEnabled, setRssEnabled] = useState(false);
  const [dateRangeType, setDateRangeType] = useState<"preset" | "custom">(
    "preset"
  );
  const [daysBack, setDaysBack] = useState<number>(30);
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TrafficLightResponse | null>(null);
  const [savedResults, setSavedResults] = useState<SavedResult[]>([]);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedRssFeeds, setSelectedRssFeeds] = useState<string[]>(
    RSS_FEEDS.map((f) => f.value)
  );

  // RTK Query hook for API calls
  const [searchCompany, { isLoading }] = useSearchCompanyMutation();
  const [getManagementSummary] = useGetManagementSummaryMutation();

  // Helper function to format date to YYYY-MM-DD
  const formatDateToYYYYMMDD = (date: Date): string => {
    return date.toISOString().split("T")[0];
  };

  // Helper function to validate date format
  const isValidDateFormat = (dateString: string): boolean => {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    return dateRegex.test(dateString) && !isNaN(Date.parse(dateString));
  };

  // Load saved results from localStorage on component mount
  useEffect(() => {
    if (user) {
      const storedResults = localStorage.getItem(`savedResults-${user.email}`);
      if (storedResults) {
        setSavedResults(JSON.parse(storedResults));
      }
    }
  }, [user]);

  const handleDateRangeTypeChange = (
    event: React.MouseEvent<HTMLElement>,
    newType: "preset" | "custom"
  ) => {
    if (newType !== null) {
      setDateRangeType(newType);
    }
  };

  const handleDaysBackChange = (event: SelectChangeEvent<number>) => {
    setDaysBack(event.target.value as number);
  };

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Ensure YYYY-MM-DD format
    if (value === "" || isValidDateFormat(value)) {
      setStartDate(value);
    }
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Ensure YYYY-MM-DD format
    if (value === "" || isValidDateFormat(value)) {
      setEndDate(value);
    }
  };

  const handleRssFeedsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[];
    setSelectedRssFeeds(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      setError("Please enter a company name or VAT number");
      return;
    }

    // Validate custom date range
    if (dateRangeType === "custom") {
      if (!startDate || !endDate) {
        setError(
          "Please select both start and end dates for custom range (format: YYYY-MM-DD)"
        );
        return;
      }
      if (!isValidDateFormat(startDate) || !isValidDateFormat(endDate)) {
        setError("Please enter dates in YYYY-MM-DD format");
        return;
      }
      if (new Date(startDate) > new Date(endDate)) {
        setError("Start date must be before end date");
        return;
      }
    }

    setError(null);

    try {
      // Prepare search request
      const searchRequest = {
        company_name: query.trim(),
        include_boe: boeEnabled,
        include_news: newsEnabled,
        include_rss: false, // RSS is disabled for performance
        ...(dateRangeType === "preset"
          ? { days_back: daysBack }
          : { start_date: startDate, end_date: endDate }),
      };

      console.log("🔍 Sending search request:", searchRequest);

      // Call the backend API
      const searchResponse = await searchCompany(searchRequest).unwrap();

      console.log("✅ Search response received:", searchResponse);

      // Convert to traffic light format
      const trafficLightResult =
        convertSearchResultsToTrafficLight(searchResponse);

      console.log("🎯 Traffic light result:", trafficLightResult);

      // Add metadata
      const resultWithMetadata: TrafficLightResponse = {
        ...trafficLightResult,
        dataSource: boeEnabled ? "BOE" : newsEnabled ? "NewsAPI" : "both",
        dateRange:
          dateRangeType === "preset"
            ? { type: "preset" as const, daysBack }
            : { type: "custom" as const, startDate, endDate },
      };

      setResult(resultWithMetadata);

      // Automatically add to dashboard
      if (user) {
        addAssessedCompany({
          name: trafficLightResult.company,
          vat: trafficLightResult.vat,
          overallRisk: trafficLightResult.overall,
          assessedBy: user.email,
          riskFactors: {
            turnover: trafficLightResult.blocks.turnover,
            shareholding: trafficLightResult.blocks.shareholding,
            bankruptcy: trafficLightResult.blocks.bankruptcy,
            legal: trafficLightResult.blocks.legal,
          },
        });
      }

      // Fetch executive summary (only executive_summary field)
      if (onRiskResult) {
        try {
          console.log(
            "📊 Fetching management summary for:",
            trafficLightResult.company
          );
          const summary = await getManagementSummary({
            company_name: trafficLightResult.company,
            classification_results: searchResponse.results,
            language: "es",
          }).unwrap();
          console.log("✅ Management summary received:", summary);
          onRiskResult(trafficLightResult.company, summary.executive_summary);
        } catch (summaryErr) {
          console.error("❌ Management summary error:", summaryErr);
          onRiskResult(trafficLightResult.company, "");
        }
      }
    } catch (err: any) {
      console.error("❌ Search error:", err);
      console.error("❌ Error details:", {
        status: err?.status,
        data: err?.data,
        message: err?.message,
      });
      setError(
        err?.data?.detail || err?.message || "An unexpected error occurred"
      );
      setResult(null);
    }
  };

  const handleSave = () => {
    if (result && user) {
      const savedResult: SavedResult = {
        ...result,
        savedAt: new Date().toISOString(),
        savedBy: user.email,
      };
      const newSavedResults = [savedResult, ...savedResults];
      setSavedResults(newSavedResults);
      localStorage.setItem(
        `savedResults-${user.email}`,
        JSON.stringify(newSavedResults)
      );
      setResult(null);
      setShowSaveSuccess(true);
    }
  };

  const handleSaveBatchResults = (newResults: SavedResult[]) => {
    const updatedResults = [...newResults, ...savedResults];
    setSavedResults(updatedResults);
    if (user) {
      localStorage.setItem(
        `savedResults-${user.email}`,
        JSON.stringify(updatedResults)
      );
    }
    setShowSaveSuccess(true);
  };

  const handleDeleteResult = (resultToDelete: SavedResult) => {
    const updatedResults = savedResults.filter(
      (result) =>
        !(
          result.company === resultToDelete.company &&
          result.savedAt === resultToDelete.savedAt &&
          result.savedBy === resultToDelete.savedBy
        )
    );
    setSavedResults(updatedResults);
    if (user) {
      localStorage.setItem(
        `savedResults-${user.email}`,
        JSON.stringify(updatedResults)
      );
    }
  };

  return (
    <Box>
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{ mb: 3 }}
          >
            <Tab label="Single Search" />
            <Tab label="Batch Upload" />
          </Tabs>

          {activeTab === 0 ? (
            <>
              <Typography variant="h6" gutterBottom>
                Risk Assessment Search
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Search for company risk information across multiple data sources
              </Typography>

              <form onSubmit={handleSubmit}>
                {/* Company Search Section */}
                <Card variant="outlined" sx={{ mb: 3, p: 2 }}>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{ fontWeight: 600 }}
                  >
                    Company Information
                  </Typography>
                  <TextField
                    label="Company Name or VAT Number"
                    variant="outlined"
                    fullWidth
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter company name (e.g., Real Madrid, Banco Santander) or VAT number"
                    disabled={isLoading}
                    InputProps={{
                      sx: { borderRadius: 2 },
                      startAdornment: (
                        <Search
                          style={{ marginRight: 8, color: "text.secondary" }}
                        />
                      ),
                    }}
                  />
                </Card>

                {/* Data Sources Section */}
                <Card variant="outlined" sx={{ mb: 3, p: 2 }}>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{ fontWeight: 600 }}
                  >
                    Data Sources
                  </Typography>
                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    {/* BOE Source */}
                    <Card
                      variant="outlined"
                      sx={{
                        p: 2,
                        cursor: "pointer",
                        border: boeEnabled
                          ? "2px solid #1976d2"
                          : "1px solid #e0e0e0",
                        backgroundColor: boeEnabled ? "#f3f8ff" : "transparent",
                        transition: "all 0.2s",
                      }}
                      onClick={() => setBoeEnabled((prev) => !prev)}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mb: 1,
                        }}
                      >
                        <Database size={20} color="#1976d2" />
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: 600 }}
                        >
                          BOE (Official Gazette)
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Spanish government publications, legal notices, and
                        official announcements
                      </Typography>
                    </Card>
                    {/* NewsAPI Source */}
                    <Card
                      variant="outlined"
                      sx={{
                        p: 2,
                        cursor: "pointer",
                        border: newsEnabled
                          ? "2px solid #1976d2"
                          : "1px solid #e0e0e0",
                        backgroundColor: newsEnabled
                          ? "#f3f8ff"
                          : "transparent",
                        transition: "all 0.2s",
                      }}
                      onClick={() => setNewsEnabled((prev) => !prev)}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mb: 1,
                        }}
                      >
                        <Newspaper size={20} color="#1976d2" />
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: 600 }}
                        >
                          NewsAPI
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        International news sources and business publications
                      </Typography>
                    </Card>
                    {/* RSS Feeds - Disabled for Demo */}
                    <Card
                      variant="outlined"
                      sx={{
                        p: 2,
                        cursor: "not-allowed",
                        border: "1px solid #e0e0e0",
                        backgroundColor: "#f5f5f5",
                        opacity: 0.6,
                        transition: "all 0.2s",
                      }}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mb: 1,
                        }}
                      >
                        <Globe size={20} color="#9e9e9e" />
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: 600, color: "#9e9e9e" }}
                        >
                          RSS Feeds (Demo Disabled)
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Spanish news sources - disabled for demo performance
                      </Typography>
                    </Card>
                  </Box>

                  {/* RSS Feed Selection */}
                  {rssEnabled && (
                    <Accordion sx={{ mt: 2, "&:before": { display: "none" } }}>
                      <AccordionSummary expandIcon={<ChevronDown />}>
                        <Typography variant="subtitle2">
                          Select RSS Feeds ({selectedRssFeeds.length} selected)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box
                          sx={{
                            display: "grid",
                            gridTemplateColumns: {
                              xs: "1fr",
                              sm: "repeat(2, 1fr)",
                              md: "repeat(4, 1fr)",
                            },
                            gap: 1,
                          }}
                        >
                          {RSS_FEEDS.map((feed) => (
                            <FormControlLabel
                              key={feed.value}
                              control={
                                <Checkbox
                                  checked={selectedRssFeeds.includes(
                                    feed.value
                                  )}
                                  onChange={(e) => {
                                    if (e.target.checked) {
                                      setSelectedRssFeeds([
                                        ...selectedRssFeeds,
                                        feed.value,
                                      ]);
                                    } else {
                                      setSelectedRssFeeds(
                                        selectedRssFeeds.filter(
                                          (f) => f !== feed.value
                                        )
                                      );
                                    }
                                  }}
                                  size="small"
                                />
                              }
                              label={feed.label}
                              sx={{ fontSize: "0.875rem" }}
                            />
                          ))}
                        </Box>
                        <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
                          <Button
                            size="small"
                            onClick={() =>
                              setSelectedRssFeeds(RSS_FEEDS.map((f) => f.value))
                            }
                            variant="outlined"
                          >
                            Select All
                          </Button>
                          <Button
                            size="small"
                            onClick={() => setSelectedRssFeeds([])}
                            variant="outlined"
                          >
                            Clear All
                          </Button>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </Card>

                {/* Date Range Section */}
                <Card variant="outlined" sx={{ mb: 3, p: 2 }}>
                  <Typography
                    variant="subtitle1"
                    gutterBottom
                    sx={{ fontWeight: 600 }}
                  >
                    Date Range
                  </Typography>

                  <ToggleButtonGroup
                    value={dateRangeType}
                    exclusive
                    onChange={handleDateRangeTypeChange}
                    size="small"
                    sx={{ mb: 2 }}
                  >
                    <ToggleButton value="preset">Quick Select</ToggleButton>
                    <ToggleButton value="custom">Custom Range</ToggleButton>
                  </ToggleButtonGroup>

                  {dateRangeType === "preset" ? (
                    <FormControl sx={{ minWidth: 200 }}>
                      <InputLabel>Time Period</InputLabel>
                      <Select
                        value={daysBack}
                        label="Time Period"
                        onChange={handleDaysBackChange}
                        disabled={isLoading}
                      >
                        <MenuItem value={7}>Last 7 days</MenuItem>
                        <MenuItem value={14}>Last 2 weeks</MenuItem>
                        <MenuItem value={30}>Last 30 days</MenuItem>
                        <MenuItem value={60}>Last 2 months</MenuItem>
                        <MenuItem value={90}>Last 3 months</MenuItem>
                        <MenuItem value={180}>Last 6 months</MenuItem>
                        <MenuItem value={365}>Last year</MenuItem>
                      </Select>
                    </FormControl>
                  ) : (
                    <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                      <TextField
                        label="Start Date"
                        type="date"
                        value={startDate}
                        onChange={handleStartDateChange}
                        disabled={isLoading}
                        InputLabelProps={{ shrink: true }}
                        sx={{ minWidth: 150 }}
                      />
                      <TextField
                        label="End Date"
                        type="date"
                        value={endDate}
                        onChange={handleEndDateChange}
                        disabled={isLoading}
                        InputLabelProps={{ shrink: true }}
                        sx={{ minWidth: 150 }}
                      />
                    </Box>
                  )}
                </Card>

                {/* Search Button */}
                <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={isLoading || !query.trim()}
                    startIcon={
                      isLoading ? <CircularProgress size={20} /> : <Search />
                    }
                    sx={{
                      minWidth: 200,
                      borderRadius: 2,
                      py: 1.5,
                      px: 4,
                    }}
                  >
                    {isLoading ? "Searching..." : "Search for Risk Assessment"}
                  </Button>
                </Box>
              </form>

              {error && (
                <Alert severity="error" sx={{ mt: 3 }}>
                  {error}
                </Alert>
              )}
            </>
          ) : (
            <BatchUpload
              onSaveResults={handleSaveBatchResults}
              dataSource={boeEnabled ? "BOE" : newsEnabled ? "NewsAPI" : "both"}
              dateRange={
                dateRangeType === "preset"
                  ? { type: "preset" as const, daysBack }
                  : { type: "custom" as const, startDate, endDate }
              }
            />
          )}
        </CardContent>
      </Card>

      {/* Current Result Display */}
      {result && (
        <Card sx={{ mb: 4, position: "relative" }}>
          <CardContent sx={{ p: 3 }}>
            {/* Search Summary */}
            <Box sx={{ mb: 3, p: 2, bgcolor: "grey.50", borderRadius: 2 }}>
              <Typography
                variant="subtitle2"
                gutterBottom
                sx={{ fontWeight: 600 }}
              >
                Search Summary
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
                <Chip
                  label={`Company: ${result.company}`}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={`Sources: ${[
                    boeEnabled ? "BOE" : null,
                    newsEnabled ? "NewsAPI" : null,
                    rssEnabled ? "RSS" : null,
                  ]
                    .filter(Boolean)
                    .join(", ")}`}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  label={`Date Range: ${
                    result.dateRange?.type === "preset"
                      ? `Last ${result.dateRange.daysBack} days`
                      : `${result.dateRange?.startDate} to ${result.dateRange?.endDate}`
                  }`}
                  variant="outlined"
                  size="small"
                />
                {result.searchResults && (
                  <Chip
                    label={`Results: ${result.searchResults.results.length} articles`}
                    variant="outlined"
                    size="small"
                    color="primary"
                  />
                )}
              </Box>
            </Box>

            <TrafficLightResult result={result} />

            <Zoom in={true}>
              <Fab
                color="primary"
                onClick={handleSave}
                sx={{
                  position: "absolute",
                  top: 16,
                  right: 16,
                  zIndex: 1,
                }}
                size="medium"
              >
                <Save />
              </Fab>
            </Zoom>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TrafficLightQuery;
