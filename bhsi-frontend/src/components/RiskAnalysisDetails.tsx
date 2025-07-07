import React, { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  IconButton,
  Tooltip,
} from "@mui/material";
import { ExpandMore } from "@mui/icons-material";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Building,
  DollarSign,
  Users,
  Scale,
  Download,
  Share,
} from "lucide-react";
import { SearchResponse } from "../store/api/riskAssessmentApi";
import CircularProgress from "@mui/material/CircularProgress";
import axios from "axios";

interface RiskFactor {
  category: string;
  score: "green" | "orange" | "red";
  weight: number;
  details: string[];
  recommendation?: string;
}

interface Company {
  id: string;
  name: string;
  industry: string;
  location: string;
  employees: number;
  revenue: string;
  founded: number;
}

interface RiskAnalysisDetailsProps {
  company: Company;
  overallRisk: "green" | "orange" | "red";
  riskFactors: RiskFactor[];
  confidence: number;
  searchResults?: SearchResponse;
}

interface WikidataCompanyInfo {
  founded?: string;
  employees?: string;
  revenue?: string;
  headquarters?: string;
}

async function fetchWikidataCompanyInfo(
  companyName: string
): Promise<WikidataCompanyInfo | null> {
  const endpoint = "https://query.wikidata.org/sparql";
  const query = `
    SELECT ?founded ?employees ?revenue ?hqLabel WHERE {
      ?company rdfs:label "${companyName}"@en;
              wdt:P31 wd:Q4830453.
      OPTIONAL { ?company wdt:P571 ?founded. }
      OPTIONAL { ?company wdt:P1128 ?employees. }
      OPTIONAL { ?company wdt:P2139 ?revenue. }
      OPTIONAL { ?company wdt:P159 ?hq. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 1
  `;
  const url = `${endpoint}?query=${encodeURIComponent(query)}&format=json`;
  try {
    const res = await axios.get(url, {
      headers: { Accept: "application/sparql-results+json" },
    });
    const bindings = res.data.results.bindings[0];
    if (!bindings) return null;
    return {
      founded: bindings.founded?.value?.split("T")[0],
      employees: bindings.employees?.value,
      revenue: bindings.revenue?.value,
      headquarters: bindings.hqLabel?.value,
    };
  } catch (e) {
    console.error("Wikidata fetch error:", e);
    return null;
  }
}

// Function to convert backend search results to risk analysis format
export const convertSearchResultsToRiskAnalysis = (
  searchResponse: SearchResponse
): {
  company: Company;
  overallRisk: "green" | "orange" | "red";
  riskFactors: RiskFactor[];
  confidence: number;
} => {
  const results = searchResponse.results;

  // Analyze risk levels
  const highRiskCount = results.filter((r) =>
    r.risk_level.startsWith("High")
  ).length;
  const mediumRiskCount = results.filter((r) =>
    r.risk_level.startsWith("Medium")
  ).length;
  const lowRiskCount = results.filter((r) =>
    r.risk_level.startsWith("Low")
  ).length;

  // Determine overall risk
  let overallRisk: "green" | "orange" | "red" = "green";
  if (highRiskCount > 0) {
    overallRisk = "red";
  } else if (mediumRiskCount > 0) {
    overallRisk = "orange";
  }

  // Calculate confidence based on result quality
  const avgConfidence =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.confidence, 0) / results.length
      : 0.5;
  const confidence = Math.round(avgConfidence * 100);

  // Categorize results
  const legalResults = results.filter((r) => r.risk_level.includes("Legal"));
  const financialResults = results.filter((r) =>
    r.risk_level.includes("Financial")
  );
  const regulatoryResults = results.filter((r) =>
    r.risk_level.includes("Regulatory")
  );
  const economicResults = results.filter((r) =>
    r.risk_level.includes("Economic")
  );

  // Create risk factors
  const riskFactors: RiskFactor[] = [];

  // Legal Risk Factor
  if (legalResults.length > 0) {
    const legalRisk = legalResults.some((r) => r.risk_level.startsWith("High"))
      ? "red"
      : legalResults.some((r) => r.risk_level.startsWith("Medium"))
      ? "orange"
      : "green";

    riskFactors.push({
      category: "Legal & Compliance",
      score: legalRisk,
      weight: 30,
      details: legalResults.map(
        (r) =>
          `${r.title} (${r.source}, ${new Date(r.date).toLocaleDateString()})`
      ),
      recommendation:
        legalRisk === "red"
          ? "Immediate legal review required"
          : legalRisk === "orange"
          ? "Monitor legal developments closely"
          : "Legal compliance appears satisfactory",
    });
  }

  // Financial Risk Factor
  if (financialResults.length > 0) {
    const financialRisk = financialResults.some((r) =>
      r.risk_level.startsWith("High")
    )
      ? "red"
      : financialResults.some((r) => r.risk_level.startsWith("Medium"))
      ? "orange"
      : "green";

    riskFactors.push({
      category: "Financial Health",
      score: financialRisk,
      weight: 25,
      details: financialResults.map(
        (r) =>
          `${r.title} (${r.source}, ${new Date(r.date).toLocaleDateString()})`
      ),
      recommendation:
        financialRisk === "red"
          ? "Financial stability concerns detected"
          : financialRisk === "orange"
          ? "Monitor financial indicators"
          : "Financial position appears stable",
    });
  }

  // Regulatory Risk Factor
  if (regulatoryResults.length > 0) {
    const regulatoryRisk = regulatoryResults.some((r) =>
      r.risk_level.startsWith("High")
    )
      ? "red"
      : regulatoryResults.some((r) => r.risk_level.startsWith("Medium"))
      ? "orange"
      : "green";

    riskFactors.push({
      category: "Regulatory Environment",
      score: regulatoryRisk,
      weight: 20,
      details: regulatoryResults.map(
        (r) =>
          `${r.title} (${r.source}, ${new Date(r.date).toLocaleDateString()})`
      ),
      recommendation:
        regulatoryRisk === "red"
          ? "Regulatory compliance issues identified"
          : regulatoryRisk === "orange"
          ? "Stay updated on regulatory changes"
          : "Regulatory compliance appears adequate",
    });
  }

  // Economic Risk Factor
  if (economicResults.length > 0) {
    const economicRisk = economicResults.some((r) =>
      r.risk_level.startsWith("High")
    )
      ? "red"
      : economicResults.some((r) => r.risk_level.startsWith("Medium"))
      ? "orange"
      : "green";

    riskFactors.push({
      category: "Economic & Market",
      score: economicRisk,
      weight: 15,
      details: economicResults.map(
        (r) =>
          `${r.title} (${r.source}, ${new Date(r.date).toLocaleDateString()})`
      ),
      recommendation:
        economicRisk === "red"
          ? "Economic risks may impact operations"
          : economicRisk === "orange"
          ? "Monitor economic indicators"
          : "Economic environment appears favorable",
    });
  }

  // Add general risk factor if no specific categories found
  if (riskFactors.length === 0 && results.length > 0) {
    riskFactors.push({
      category: "General Risk Assessment",
      score: overallRisk,
      weight: 100,
      details: results.map(
        (r) =>
          `${r.title} (${r.source}, ${new Date(r.date).toLocaleDateString()})`
      ),
      recommendation:
        overallRisk === "red"
          ? "High risk profile requires immediate attention"
          : overallRisk === "orange"
          ? "Medium risk profile requires monitoring"
          : "Low risk profile suitable for standard operations",
    });
  }

  return {
    company: {
      id: "1",
      name: searchResponse.company_name,
      industry: "Not specified",
      location: "Not available",
      employees: 0,
      revenue: "Not available",
      founded: 0,
    },
    overallRisk,
    riskFactors,
    confidence,
  };
};

const mockCompanies: Company[] = [
  {
    id: "1",
    name: "Banco de España",
    industry: "Banking & Finance", 
    location: "Madrid, Spain",
    employees: 3200,
    revenue: "€2.1B",
    founded: 1782,
  },
  {
    id: "2",
    name: "Repsol S.A.",
    industry: "Energy & Petroleum",
    location: "Madrid, Spain", 
    employees: 25000,
    revenue: "€48.7B",
    founded: 1987,
  },
];

const mockData: RiskAnalysisDetailsProps = {
  company: {
    id: "1",
    name: "Banco de España",
    industry: "Banking & Finance",
    location: "Madrid, Spain",
    employees: 3200,
    revenue: "€2.1B",
    founded: 1782,
  },
  overallRisk: "green",
  confidence: 87,
  riskFactors: [
    {
      category: "Financial Health",
      score: "green",
      weight: 35,
      details: [
        "Steady revenue growth of 15% year-over-year",
        "Strong cash flow position",
        "Low debt-to-equity ratio (0.3)",
        "Profitable for 3 consecutive years",
      ],
      recommendation:
        "Excellent financial position supports low-risk classification",
    },
    {
      category: "Corporate Structure",
      score: "green",
      weight: 25,
      details: [
        "Clear ownership structure",
        "No complex holding structures",
        "Transparent board composition",
        "Regular financial reporting",
      ],
    },
    {
      category: "Legal & Compliance",
      score: "orange",
      weight: 20,
      details: [
        "Minor regulatory fine in 2022 (€15K)",
        "No ongoing litigation",
        "Compliance framework in place",
        "Regular audits conducted",
      ],
      recommendation: "Monitor regulatory compliance improvements",
    },
    {
      category: "Market Position",
      score: "green",
      weight: 20,
      details: [
        "Market leader in B2B software",
        "Diversified client base",
        "Strong competitive moat",
        "Innovation pipeline active",
      ],
    },
  ],
};

const getRiskColor = (risk: "green" | "orange" | "red") => {
  switch (risk) {
    case "green":
      return { color: "#2e7d32", bg: "#e8f5e8" };
    case "orange":
      return { color: "#ed6c02", bg: "#fff3e0" };
    case "red":
      return { color: "#d32f2f", bg: "#ffebee" };
  }
};

const getRiskIcon = (risk: "green" | "orange" | "red") => {
  switch (risk) {
    case "green":
      return <CheckCircle size={20} color="#2e7d32" />;
    case "orange":
      return <AlertTriangle size={20} color="#ed6c02" />;
    case "red":
      return <XCircle size={20} color="#d32f2f" />;
  }
};

const RiskAnalysisDetails = ({
  company,
  overallRisk,
  riskFactors,
  confidence,
  searchResults,
}: RiskAnalysisDetailsProps = mockData) => {
  const riskColors = getRiskColor(overallRisk);

  // Wikidata integration
  const [wikidata, setWikidata] = useState<WikidataCompanyInfo | null>(null);
  const [loadingWikidata, setLoadingWikidata] = useState(false);

  useEffect(() => {
    let ignore = false;
    if (company?.name) {
      setLoadingWikidata(true);
      fetchWikidataCompanyInfo(company.name).then((data) => {
        if (!ignore) {
          setWikidata(data);
          setLoadingWikidata(false);
        }
      });
    }
    return () => {
      ignore = true;
    };
  }, [company?.name]);

  return (
    <Box sx={{ maxWidth: "100%", mx: "auto", p: 3 }}>
      {/* Header Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              mb: 3,
            }}
          >
            <Box>
              <Typography variant="h4" gutterBottom>
                {company.name}
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                {company.industry}
              </Typography>
              {searchResults && (
                <Typography variant="body2" color="text.secondary">
                  Analysis based on {searchResults.results.length} documents
                  from{" "}
                  {searchResults.date_range.start ||
                    `${searchResults.date_range.days_back} days ago`}{" "}
                  to {searchResults.date_range.end || "today"}
                </Typography>
              )}
            </Box>

            <Box sx={{ display: "flex", gap: 1 }}>
              <Tooltip title="Download Report">
                <IconButton>
                  <Download size={20} />
                </IconButton>
              </Tooltip>
              <Tooltip title="Share Analysis">
                <IconButton>
                  <Share size={20} />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Overall Risk Assessment */}
          <Box
            sx={{
              p: 3,
              borderRadius: 2,
              bgcolor: riskColors.bg,
              border: `2px solid ${riskColors.color}`,
              mb: 3,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              {getRiskIcon(overallRisk)}
              <Typography
                variant="h5"
                sx={{ ml: 2, color: riskColors.color, fontWeight: "bold" }}
              >
                {overallRisk.toUpperCase()} RISK
              </Typography>
              <Chip
                label={`${confidence}% Confidence`}
                sx={{ ml: "auto" }}
                color={
                  confidence > 80
                    ? "success"
                    : confidence > 60
                    ? "warning"
                    : "error"
                }
              />
            </Box>

            <Typography variant="body1">
              Based on comprehensive analysis of{" "}
              {searchResults
                ? "search results from multiple sources"
                : "financial health, corporate structure, legal compliance, and market position"}
              .
            </Typography>
          </Box>

          {/* Company Info Grid */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Building size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">
                  Founded
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {loadingWikidata ? (
                  <CircularProgress size={16} />
                ) : (
                  wikidata?.founded || company.founded || "Not available"
                )}
              </Typography>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Users size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">
                  Employees
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {loadingWikidata ? (
                  <CircularProgress size={16} />
                ) : (
                  wikidata?.employees || company.employees || "Not available"
                )}
              </Typography>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <DollarSign size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">
                  Revenue
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {loadingWikidata ? (
                  <CircularProgress size={16} />
                ) : (
                  wikidata?.revenue || company.revenue || "Not available"
                )}
              </Typography>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Scale size={16} style={{ marginRight: 8 }} />
                <Typography variant="body2" color="text.secondary">
                  Headquarters
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight="medium">
                {loadingWikidata ? (
                  <CircularProgress size={16} />
                ) : (
                  wikidata?.headquarters ||
                  company.location ||
                  "Not available"
                )}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk Factors Analysis */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Detailed Risk Analysis
      </Typography>

      {riskFactors.map((factor, index) => {
        const factorColors = getRiskColor(factor.score);

        return (
          <Accordion key={index} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box
                sx={{ display: "flex", alignItems: "center", width: "100%" }}
              >
                <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
                  {getRiskIcon(factor.score)}
                  <Typography variant="h6" sx={{ ml: 2 }}>
                    {factor.category}
                  </Typography>
                </Box>

                <Box sx={{ display: "flex", alignItems: "center", mr: 2 }}>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mr: 2 }}
                  >
                    Weight: {factor.weight}%
                  </Typography>
                  <Chip
                    label={factor.score.toUpperCase()}
                    size="small"
                    sx={{
                      bgcolor: factorColors.bg,
                      color: factorColors.color,
                      fontWeight: "bold",
                    }}
                  />
                </Box>
              </Box>
            </AccordionSummary>

            <AccordionDetails>
              <Box sx={{ p: 2 }}>
                <List dense>
                  {factor.details.map((detail, detailIndex) => (
                    <ListItem key={detailIndex} sx={{ pl: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Info size={16} color="#666" />
                      </ListItemIcon>
                      <ListItemText primary={detail} />
                    </ListItem>
                  ))}
                </List>

                {factor.recommendation && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Recommendation:</strong> {factor.recommendation}
                      </Typography>
                    </Alert>
                  </>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
};

export default RiskAnalysisDetails;
