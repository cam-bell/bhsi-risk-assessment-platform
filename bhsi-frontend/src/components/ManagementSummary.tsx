import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Fade,
} from "@mui/material";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  FileText,
  Shield,
  DollarSign,
} from "lucide-react";
import { useGetManagementSummaryMutation } from "../store/api/analyticsApi";
import { useCompanies } from "../context/CompaniesContext";
import SummaryHeader from "./ManagementSummary/SummaryHeader";
import ExecutiveSummaryCard from "./ManagementSummary/ExecutiveSummaryCard";
import RiskBreakdownGrid from "./ManagementSummary/RiskBreakdownGrid";
import FinancialHealthPanel from "./ManagementSummary/FinancialHealthPanel";
import KeyFindingsList from "./ManagementSummary/KeyFindingsList";
import RecommendationsChecklist from "./ManagementSummary/RecommendationsChecklist";
import KeyRisksPanel from "./ManagementSummary/KeyRisksPanel";
import ComplianceStatusPanel from "./ManagementSummary/ComplianceStatusPanel";

const StatusIcon: React.FC<{
  status?:
    | "healthy"
    | "concerning"
    | "critical"
    | "compliant"
    | "partial"
    | "non_compliant"
    | "positive"
    | "neutral"
    | "negative"
    | undefined;
}> = ({ status }) => {
  switch (status) {
    case "healthy":
    case "compliant":
    case "positive":
      return <CheckCircle size={16} color="#4caf50" />;
    case "concerning":
    case "partial":
    case "neutral":
      return <AlertTriangle size={16} color="#ff9800" />;
    case "critical":
    case "non_compliant":
    case "negative":
      return <XCircle size={16} color="#f44336" />;
    default:
      return <Info size={16} color="#9e9e9e" />;
  }
};

const SeverityChip: React.FC<{ severity?: "low" | "medium" | "high" }> = ({
  severity,
}) => {
  const colors = {
    low: "success",
    medium: "warning",
    high: "error",
  } as const;

  if (!severity) return null;
  return (
    <Chip
      label={severity.toUpperCase()}
      color={colors[severity]}
      size="small"
      variant="outlined"
    />
  );
};

const LANGUAGES = [
  { code: "es", label: "Español" },
  { code: "en", label: "English" },
];

const ManagementSummary: React.FC<{
  companyName: string;
  language: string;
  languages: { code: string; label: string }[];
  onLanguageChange: (lang: string) => void;
}> = ({ companyName, language, languages, onLanguageChange }) => {
  const { selectedCompany } = useCompanies();
  const [getManagementSummary, { data: summary, isLoading, error }] =
    useGetManagementSummaryMutation();

  useEffect(() => {
    if (companyName) {
      getManagementSummary({
        company_name: companyName,
        language,
      });
    }
  }, [companyName, language, getManagementSummary]);

  // Print/export handler (bonus)
  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight={400}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading management summary for {companyName}. Please try again.
      </Alert>
    );
  }

  if (!summary) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        No management summary available for {companyName}.
      </Alert>
    );
  }

  return (
    <Fade in timeout={600}>
      <Box>
        {/* Header Section with language toggle and print/export */}
        <SummaryHeader
          companyName={companyName}
          overallRisk={summary.overall_risk}
          generatedAt={summary.generated_at}
          method={summary.method}
          language={language}
          onLanguageChange={onLanguageChange}
          languages={languages}
          onPrint={handlePrint}
        />

        <Grid container spacing={3}>
          {/* Executive Summary */}
          <Grid item xs={12}>
            <ExecutiveSummaryCard summary={summary.executive_summary} />
          </Grid>

          {/* Risk Breakdown */}
          <Grid item xs={12}>
            <RiskBreakdownGrid riskBreakdown={summary.risk_breakdown} />
          </Grid>

          {/* Financial Health & Key Risks */}
          <Grid item xs={12} md={6}>
            <FinancialHealthPanel financialHealth={summary.financial_health} />
          </Grid>
          <Grid item xs={12} md={6}>
            <KeyRisksPanel keyRisks={summary.key_risks} />
          </Grid>

          {/* Key Findings & Recommendations */}
          <Grid item xs={12} md={6}>
            <KeyFindingsList keyFindings={summary.key_findings} />
          </Grid>
          <Grid item xs={12} md={6}>
            <RecommendationsChecklist
              recommendations={summary.recommendations}
            />
          </Grid>

          {/* Compliance Status */}
          <Grid item xs={12}>
            <ComplianceStatusPanel
              complianceStatus={summary.compliance_status}
            />
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );
};

export default ManagementSummary;
