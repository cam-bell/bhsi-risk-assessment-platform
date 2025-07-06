import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Divider,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableRow,
  TableContainer,
} from "@mui/material";

const riskLevelColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case "high":
      return "error";
    case "medium":
      return "warning";
    case "low":
      return "success";
    default:
      return "info";
  }
};

const FinancialInsightsPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleSearch = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      let res;
      let url = "";
      if (/^[a-zA-Z0-9.]{1,7}$/.test(query.trim())) {
        // Looks like a ticker
        url = `/api/v1/finance/${encodeURIComponent(query.trim())}`;
      } else {
        // Treat as company name
        url = `/api/v1/finance/by-name?company_name=${encodeURIComponent(
          query.trim()
        )}`;
      }
      res = await fetch(url);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      if (
        !data ||
        data.search_summary?.errors?.length ||
        !data.financial_data ||
        data.financial_data.length === 0
      ) {
        setError(
          data.search_summary?.errors?.[0] ||
            "No financial data found for this company."
        );
        setResult(null);
      } else {
        setResult(data.financial_data[0]);
      }
    } catch (e: any) {
      setError(e.message || "Unknown error");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 900, mx: "auto" }}>
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Financial Insights
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Search for a company by name or ticker to view financial risk data and
          key indicators. This page will soon allow you to analyze company
          financials, risk levels, and trends using real-time data.
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
            {loading ? <CircularProgress size={22} /> : "Search"}
          </Button>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        {result && (
          <Box>
            <Stack direction="row" spacing={2} alignItems="center" mb={2}>
              <Typography variant="h5" component="h2">
                {result.company_name} {result.ticker && `(${result.ticker})`}
              </Typography>
              <Chip
                label={result.risk_level || "Unknown"}
                color={riskLevelColor(result.risk_level)}
                sx={{
                  fontWeight: 600,
                  fontSize: "1rem",
                  textTransform: "capitalize",
                }}
                aria-label={`Risk level: ${result.risk_level}`}
              />
            </Stack>
            <TableContainer component={Paper} sx={{ mb: 3 }}>
              <Table size="small" aria-label="financial metrics">
                <TableBody>
                  {result.current_price !== undefined && (
                    <TableRow>
                      <TableCell>Current Price</TableCell>
                      <TableCell>
                        {result.current_price} {result.currency}
                      </TableCell>
                    </TableRow>
                  )}
                  {result.market_cap !== undefined && (
                    <TableRow>
                      <TableCell>Market Cap</TableCell>
                      <TableCell>
                        {result.market_cap.toLocaleString()}
                      </TableCell>
                    </TableRow>
                  )}
                  {result.fifty_two_week_high !== undefined && (
                    <TableRow>
                      <TableCell>52 Week High</TableCell>
                      <TableCell>{result.fifty_two_week_high}</TableCell>
                    </TableRow>
                  )}
                  {result.fifty_two_week_low !== undefined && (
                    <TableRow>
                      <TableCell>52 Week Low</TableCell>
                      <TableCell>{result.fifty_two_week_low}</TableCell>
                    </TableRow>
                  )}
                  {result.dividend_yield !== undefined && (
                    <TableRow>
                      <TableCell>Dividend Yield</TableCell>
                      <TableCell>{result.dividend_yield}</TableCell>
                    </TableRow>
                  )}
                  {result.forward_pe !== undefined && (
                    <TableRow>
                      <TableCell>Forward P/E</TableCell>
                      <TableCell>{result.forward_pe}</TableCell>
                    </TableRow>
                  )}
                  {result.website && (
                    <TableRow>
                      <TableCell>Website</TableCell>
                      <TableCell>
                        <a
                          href={result.website}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {result.website}
                        </a>
                      </TableCell>
                    </TableRow>
                  )}
                  {result.price_change_7d && (
                    <TableRow>
                      <TableCell>Price Change (7d)</TableCell>
                      <TableCell>
                        {result.price_change_7d.percentage?.toFixed(2)}% (
                        {result.price_change_7d.from} →{" "}
                        {result.price_change_7d.to})
                      </TableCell>
                    </TableRow>
                  )}
                  {result.revenue_change_yoy && (
                    <TableRow>
                      <TableCell>Revenue Change (YoY)</TableCell>
                      <TableCell>
                        {result.revenue_change_yoy.percentage?.toFixed(2)}% (
                        {result.revenue_change_yoy.from} →{" "}
                        {result.revenue_change_yoy.to})
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            {result.risk_indicators && result.risk_indicators.length > 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Risk Indicators
                </Typography>
                <Stack spacing={1}>
                  {result.risk_indicators.map((indicator: any, idx: number) => (
                    <Alert
                      key={idx}
                      severity={riskLevelColor(indicator.severity)}
                      icon={false}
                      sx={{ fontWeight: 500 }}
                    >
                      {indicator.description}
                    </Alert>
                  ))}
                </Stack>
              </Box>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default FinancialInsightsPage;
