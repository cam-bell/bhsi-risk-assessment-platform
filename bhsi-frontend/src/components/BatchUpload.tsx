import { useState, useRef } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Collapse,
  Tooltip,
  Link,
} from "@mui/material";
import { Upload, X, Save, AlertCircle, Download } from "lucide-react";
import Papa from "papaparse";
import * as XLSX from "xlsx";
import type { TrafficLightResponse, SavedResult } from "./TrafficLightQuery";
import TrafficLightResult from "./TrafficLightResult";
import { useAuth } from "../auth/useAuth";
import {
  useSearchCompanyMutation,
  SearchResponse,
} from "../store/api/riskAssessmentApi";

interface BatchUploadProps {
  onSaveResults: (results: SavedResult[]) => void;
  dataSource?: "BOE" | "NewsAPI" | "both";
  dateRange?: {
    type: "preset" | "custom";
    daysBack?: number;
    startDate?: string;
    endDate?: string;
  };
}

interface ProcessedResult extends TrafficLightResponse {
  status: "pending" | "processing" | "complete" | "error";
  error?: string;
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

const sampleData = [
  ["Company Name"],
  ["ACME Solutions"],
  ["TechVision Global"],
  ["RiskCorp Industries"],
  ["Nova Enterprises"],
];

const BatchUpload = ({
  onSaveResults,
  dataSource = "both",
  dateRange,
}: BatchUploadProps) => {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [results, setResults] = useState<ProcessedResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ProcessedResult | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  // RTK Query hook for API calls
  const [searchCompany] = useSearchCompanyMutation();

  const downloadSampleFile = () => {
    const ws = XLSX.utils.aoa_to_sheet(sampleData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Companies");

    // Auto-size columns
    const colWidths = sampleData.reduce((w, r) => {
      r.forEach((cell, i) => {
        const cellWidth = cell ? cell.toString().length : 10;
        w[i] = Math.max(w[i] || 10, cellWidth);
      });
      return w;
    }, [] as number[]);

    ws["!cols"] = colWidths.map((w) => ({ wch: w + 2 }));

    XLSX.writeFile(wb, "sample-companies.xlsx");
  };

  const processFile = async (file: File) => {
    setError(null);
    setIsProcessing(true);
    const extension = file.name.split(".").pop()?.toLowerCase();

    try {
      let data: string[][] = [];

      if (extension === "csv") {
        // Process CSV
        const text = await file.text();
        const result = Papa.parse(text, { skipEmptyLines: true });
        data = result.data as string[][];
      } else if (extension === "xlsx" || extension === "xls") {
        // Process Excel
        const buffer = await file.arrayBuffer();
        const workbook = XLSX.read(buffer);
        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
        data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
      } else {
        throw new Error(
          "Unsupported file format. Please upload a CSV or Excel file."
        );
      }

      // Skip header row and process data
      const companies = data
        .slice(1)
        .map((row) => row[0]?.toString().trim())
        .filter(Boolean);

      if (companies.length === 0) {
        throw new Error("No valid company data found in the file.");
      }

      if (companies.length > 100) {
        throw new Error("Maximum 100 companies allowed per upload.");
      }

      // Initialize results
      setResults(
        companies.map((company) => ({
          company,
          vat: "N/A",
          overall: "green",
          blocks: {
            turnover: "green",
            shareholding: "green",
            bankruptcy: "green",
            legal: "green",
          },
          status: "pending",
        }))
      );

      // Process each company with API calls
      for (let i = 0; i < companies.length; i++) {
        setResults((prev) => {
          const newResults = [...prev];
          newResults[i] = { ...newResults[i], status: "processing" };
          return newResults;
        });

        try {
          // Prepare search request
          const searchRequest = {
            company_name: companies[i].trim(),
            include_boe: dataSource === "BOE" || dataSource === "both",
            include_news: dataSource === "NewsAPI" || dataSource === "both",
            ...(dateRange?.type === "preset"
              ? { days_back: dateRange.daysBack || 30 }
              : dateRange?.type === "custom"
              ? { start_date: dateRange.startDate, end_date: dateRange.endDate }
              : { days_back: 30 }),
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
            dateRange,
          };

          setResults((prev) => {
            const newResults = [...prev];
            newResults[i] = {
              ...resultWithMetadata,
              status: "complete",
            };
            return newResults;
          });

          // Add delay between requests to avoid rate limiting
          await new Promise((resolve) => setTimeout(resolve, 1000));
        } catch (err: any) {
          console.error(`Error processing ${companies[i]}:`, err);
          setResults((prev) => {
            const newResults = [...prev];
            newResults[i] = {
              ...newResults[i],
              status: "error",
              error:
                err?.data?.detail ||
                err?.message ||
                "Failed to process company",
            };
            return newResults;
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process file");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      processFile(file);
    }
    // Reset input value to allow selecting the same file again
    event.target.value = "";
  };

  const handleSaveAll = () => {
    if (user) {
      const savedResults: SavedResult[] = results
        .filter((result) => result.status === "complete")
        .map((result) => ({
          ...result,
          savedAt: new Date().toISOString(),
          savedBy: user.email,
        }));
      onSaveResults(savedResults);
      setResults([]);
    }
  };

  const handleViewResult = (result: ProcessedResult) => {
    setSelectedResult(result);
  };

  const handleCloseDialog = () => {
    setSelectedResult(null);
  };

  return (
    <Box>
      <input
        type="file"
        ref={fileInputRef}
        accept=".csv,.xlsx,.xls"
        onChange={handleFileSelect}
        style={{ display: "none" }}
      />

      <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<Upload />}
          onClick={() => fileInputRef.current?.click()}
          disabled={isProcessing}
        >
          Upload File
        </Button>
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={downloadSampleFile}
          disabled={isProcessing}
        >
          Download Sample
        </Button>
        {results.length > 0 && (
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveAll}
            disabled={
              isProcessing || results.every((r) => r.status !== "complete")
            }
          >
            Save All Results
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {isProcessing && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <CircularProgress size={20} />
            <Typography>
              Processing{" "}
              {results.filter((r) => r.status === "processing").length} of{" "}
              {results.length} companies...
            </Typography>
          </Box>
        </Alert>
      )}

      {results.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Processing Results (
            {results.filter((r) => r.status === "complete").length}/
            {results.length})
          </Typography>

          <List>
            {results.map((result, index) => (
              <ListItem
                key={index}
                sx={{
                  border: 1,
                  borderColor: "divider",
                  borderRadius: 1,
                  mb: 1,
                  "&:last-child": { mb: 0 },
                }}
              >
                <ListItemText
                  primary={result.company}
                  secondary={
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mt: 1,
                      }}
                    >
                      {result.status === "pending" && (
                        <Chip label="Pending" size="small" color="default" />
                      )}
                      {result.status === "processing" && (
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <CircularProgress size={16} />
                          <Typography variant="caption">
                            Processing...
                          </Typography>
                        </Box>
                      )}
                      {result.status === "complete" && (
                        <>
                          <Chip
                            label={result.overall.toUpperCase()}
                            size="small"
                            color={
                              result.overall === "green"
                                ? "success"
                                : result.overall === "orange"
                                ? "warning"
                                : "error"
                            }
                          />
                          <Button
                            size="small"
                            onClick={() => handleViewResult(result)}
                            disabled={result.status !== "complete"}
                          >
                            View Details
                          </Button>
                        </>
                      )}
                      {result.status === "error" && (
                        <Chip
                          label="Error"
                          size="small"
                          color="error"
                          icon={<AlertCircle size={14} />}
                        />
                      )}
                    </Box>
                  }
                />
                <IconButton
                  onClick={() => {
                    setResults((prev) => prev.filter((_, i) => i !== index));
                  }}
                  size="small"
                >
                  <X size={16} />
                </IconButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Result Details Dialog */}
      <Dialog
        open={!!selectedResult}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Risk Assessment Result</DialogTitle>
        <DialogContent>
          {selectedResult && <TrafficLightResult result={selectedResult} />}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BatchUpload;
