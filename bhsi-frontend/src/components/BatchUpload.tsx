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

interface BatchUploadProps {
  onSaveResults: (results: SavedResult[]) => void;
  getMockResponse: (query: string) => TrafficLightResponse;
}

interface ProcessedResult extends TrafficLightResponse {
  status: "pending" | "processing" | "complete" | "error";
  error?: string;
}

const sampleData = [
  [
    "Company Name",
    "VAT",
    "Financial Turnover",
    "Shareholding Structure",
    "Bankruptcy History",
    "Legal Issues",
    "Turnover Source",
    "Shareholding Source",
    "Bankruptcy Source",
    "Legal Source",
  ],
  [
    "ACME Solutions S.A.",
    "ESX78901234",
    "GREEN",
    "ORANGE",
    "GREEN",
    "RED",
    "SABI Bureau van Dijk Database",
    "Companies House Registry",
    "Insolvency Service Records",
    "UK Court Service",
  ],
  [
    "TechVision Global S.A.",
    "ESX45678901",
    "GREEN",
    "GREEN",
    "GREEN",
    "ORANGE",
    "SABI Bureau van Dijk Database",
    "Companies House Registry",
    "Insolvency Service Records",
    "Spanish Regulatory Agency",
  ],
  [
    "RiskCorp Industries S.A.",
    "ESX12345678",
    "RED",
    "RED",
    "ORANGE",
    "RED",
    "SABI Bureau van Dijk Database",
    "Companies House Registry",
    "Insolvency Service Records",
    "UK Court Service",
  ],
  [
    "Nova Enterprises S.A.",
    "ESX23456789",
    "ORANGE",
    "GREEN",
    "ORANGE",
    "GREEN",
    "SABI Bureau van Dijk Database",
    "Companies House Registry",
    "Insolvency Service Records",
    "Spanish Regulatory Agency",
  ],
];

const BatchUpload = ({ onSaveResults, getMockResponse }: BatchUploadProps) => {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [results, setResults] = useState<ProcessedResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ProcessedResult | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

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
          ...getMockResponse(company),
          status: "pending",
        }))
      );

      // Process each company with a delay
      for (let i = 0; i < companies.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        setResults((prev) => {
          const newResults = [...prev];
          try {
            newResults[i] = {
              ...getMockResponse(companies[i]),
              status: "complete",
            };
          } catch (err) {
            newResults[i] = {
              ...newResults[i],
              status: "error",
              error: "Failed to process company",
            };
          }
          return newResults;
        });
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
              isProcessing || !results.some((r) => r.status === "complete")
            }
          >
            Save All Results
          </Button>
        )}
      </Box>

      <Collapse in={Boolean(error)}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Collapse>

      {results.length > 0 && (
        <Paper variant="outlined" sx={{ mt: 2 }}>
          <List>
            {results.map((result, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    {result.status === "complete" && (
                      <Chip
                        label={result.overall.toUpperCase()}
                        color={
                          result.overall === "green"
                            ? "success"
                            : result.overall === "orange"
                            ? "warning"
                            : "error"
                        }
                        size="small"
                      />
                    )}
                    {result.status === "complete" ? (
                      <Tooltip title="View Details">
                        <IconButton
                          edge="end"
                          onClick={() => handleViewResult(result)}
                          size="small"
                        >
                          <AlertCircle size={20} />
                        </IconButton>
                      </Tooltip>
                    ) : result.status === "processing" ? (
                      <CircularProgress size={20} />
                    ) : result.status === "error" ? (
                      <Tooltip title={result.error}>
                        <X color="error" size={20} />
                      </Tooltip>
                    ) : null}
                  </Box>
                }
              >
                <ListItemText primary={result.company} secondary={result.vat} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Dialog
        open={Boolean(selectedResult)}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedResult && (
          <>
            <DialogTitle
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                pb: 1,
              }}
            >
              Risk Assessment Details
              <IconButton
                edge="end"
                color="inherit"
                onClick={handleCloseDialog}
                aria-label="close"
                size="small"
              >
                <X size={20} />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <TrafficLightResult result={selectedResult} />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog} variant="contained">
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Box sx={{ mt: 4 }}>
        <Typography variant="body2" color="text.secondary" paragraph>
          Upload a CSV or Excel file with company names in the first column.
          Maximum 100 companies per upload.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Need help getting started?{" "}
          <Link component="button" onClick={downloadSampleFile}>
            Download our sample file
          </Link>{" "}
          to see the expected format.
        </Typography>
      </Box>
    </Box>
  );
};

export default BatchUpload;
