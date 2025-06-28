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

const TrafficLightQuery = () => {
  const { user } = useAuth();
  const { addAssessedCompany } = useCompanies();
  const [query, setQuery] = useState("");
  const [dataSource, setDataSource] = useState<"BOE" | "NewsAPI" | "both">(
    "both"
  );
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

  // RTK Query hook for API calls
  const [searchCompany, { isLoading }] = useSearchCompanyMutation();

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

  const handleDataSourceChange = (
    event: SelectChangeEvent<"BOE" | "NewsAPI" | "both">
  ) => {
    setDataSource(event.target.value as "BOE" | "NewsAPI" | "both");
  };

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
        include_boe: dataSource === "BOE" || dataSource === "both",
        include_news: dataSource === "NewsAPI" || dataSource === "both",
        ...(dateRangeType === "preset"
          ? { days_back: daysBack }
          : { start_date: startDate, end_date: endDate }),
      };

      // Call the backend API
      const searchResponse = await searchCompany(searchRequest).unwrap();

      // Convert to traffic light format
      const trafficLightResult =
        convertSearchResultsToTrafficLight(searchResponse);

      // Add metadata
      const resultWithMetadata: TrafficLightResponse = {
        ...trafficLightResult,
        dataSource,
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
    } catch (err: any) {
      console.error("Search error:", err);
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
                Enter Company Details
              </Typography>
              <form onSubmit={handleSubmit}>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: { xs: "column", sm: "row" },
                    gap: 2,
                    alignItems: { xs: "stretch", sm: "flex-end" },
                    mb: 2,
                  }}
                >
                  <TextField
                    label="Company Name or VAT Number"
                    variant="outlined"
                    fullWidth
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Try: ACME, TECH, RISK, or NOVA"
                    disabled={isLoading}
                    InputProps={{
                      sx: { borderRadius: 2 },
                    }}
                    sx={{ flex: 1 }}
                  />
                  <FormControl sx={{ minWidth: { xs: "100%", sm: "200px" } }}>
                    <InputLabel>Data Source</InputLabel>
                    <Select
                      value={dataSource}
                      label="Data Source"
                      onChange={handleDataSourceChange}
                      disabled={isLoading}
                      sx={{ borderRadius: 2 }}
                    >
                      <MenuItem value="BOE">
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <Database size={16} />
                          BOE (Boletín Oficial del Estado)
                        </Box>
                      </MenuItem>
                      <MenuItem value="NewsAPI">
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <Newspaper size={16} />
                          NewsAPI
                        </Box>
                      </MenuItem>
                      <MenuItem value="both">
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <Globe size={16} />
                          Both Sources
                        </Box>
                      </MenuItem>
                    </Select>
                  </FormControl>
                </Box>

                {/* Date Range Section */}
                <Accordion
                  sx={{
                    mb: 2,
                    borderRadius: 2,
                    "&:before": { display: "none" },
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ChevronDown />}
                    sx={{
                      borderRadius: 2,
                      "& .MuiAccordionSummary-content": {
                        alignItems: "center",
                      },
                    }}
                  >
                    <Calendar size={18} style={{ marginRight: 8 }} />
                    <Typography variant="subtitle2">Date Range</Typography>
                    <Typography
                      variant="caption"
                      sx={{ ml: 2, color: "text.secondary" }}
                    >
                      {dateRangeType === "preset"
                        ? `Last ${daysBack} days`
                        : startDate && endDate
                        ? `${startDate} to ${endDate}`
                        : "Custom range"}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
                    >
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
                        <FormControl sx={{ maxWidth: 300 }}>
                          <InputLabel>Period</InputLabel>
                          <Select
                            value={daysBack}
                            label="Period"
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
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: { xs: "column", sm: "row" },
                            gap: 2,
                          }}
                        >
                          <TextField
                            label="Start Date"
                            type="date"
                            value={startDate}
                            onChange={handleStartDateChange}
                            disabled={isLoading}
                            placeholder="YYYY-MM-DD"
                            InputLabelProps={{
                              shrink: true,
                            }}
                            helperText="Format: YYYY-MM-DD (e.g., 2025-06-01)"
                            sx={{ flex: 1 }}
                          />
                          <TextField
                            label="End Date"
                            type="date"
                            value={endDate}
                            onChange={handleEndDateChange}
                            disabled={isLoading}
                            placeholder="YYYY-MM-DD"
                            InputLabelProps={{
                              shrink: true,
                            }}
                            helperText="Format: YYYY-MM-DD (e.g., 2025-06-13)"
                            sx={{ flex: 1 }}
                          />
                        </Box>
                      )}

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ fontSize: "0.875rem" }}
                      >
                        💡 <strong>Tip:</strong> Date range primarily affects
                        NewsAPI results. BOE data is typically current and less
                        time-sensitive.
                      </Typography>
                    </Box>
                  </AccordionDetails>
                </Accordion>

                <Box sx={{ display: "flex", justifyContent: "center" }}>
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={isLoading}
                    startIcon={
                      isLoading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        <Search />
                      )
                    }
                    sx={{
                      minWidth: "200px",
                      height: "56px",
                      fontSize: "1.1rem",
                      fontWeight: 600,
                    }}
                  >
                    {isLoading ? "Searching..." : "Get Score"}
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
              dataSource={dataSource}
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
          <CardContent>
            <TrafficLightResult result={result} />
            <Zoom in={true}>
              <Fab
                color="primary"
                onClick={handleSave}
                sx={{
                  position: "absolute",
                  top: 16,
                  right: 16,
                  boxShadow: (theme) =>
                    `0 4px 14px ${theme.palette.primary.main}40`,
                  "&:hover": {
                    transform: "scale(1.05)",
                  },
                }}
              >
                <Tooltip title="Save Result" placement="left">
                  <Save />
                </Tooltip>
              </Fab>
            </Zoom>
          </CardContent>
        </Card>
      )}

      {/* Success Snackbar */}
      <Snackbar
        open={showSaveSuccess}
        autoHideDuration={3000}
        onClose={() => setShowSaveSuccess(false)}
        message="Result saved successfully"
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
};

export default TrafficLightQuery;
