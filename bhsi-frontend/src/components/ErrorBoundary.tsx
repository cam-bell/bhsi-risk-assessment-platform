import React, { Component, ErrorInfo, ReactNode } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  AlertTitle,
  Collapse,
  IconButton,
} from "@mui/material";
import {
  AlertTriangle,
  RefreshCw,
  Bug,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

// Error Boundary Class Component
export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    showDetails: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      showDetails: false,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });
  };

  private toggleDetails = () => {
    this.setState({ showDetails: !this.state.showDetails });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "50vh",
            p: 3,
          }}
        >
          <Card sx={{ maxWidth: 600, width: "100%" }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                <AlertTriangle
                  size={32}
                  color="#d32f2f"
                  style={{ marginRight: 16 }}
                />
                <Typography variant="h5" color="error">
                  Something went wrong
                </Typography>
              </Box>

              <Typography variant="body1" paragraph>
                We apologize for the inconvenience. An unexpected error has
                occurred. Our development team has been notified and is working
                to resolve this issue.
              </Typography>

              <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<RefreshCw size={16} />}
                  onClick={this.handleReset}
                >
                  Try Again
                </Button>
                <Button
                  variant="outlined"
                  startIcon={
                    this.state.showDetails ? (
                      <ChevronUp size={16} />
                    ) : (
                      <ChevronDown size={16} />
                    )
                  }
                  onClick={this.toggleDetails}
                >
                  {this.state.showDetails ? "Hide" : "Show"} Details
                </Button>
              </Box>

              <Collapse in={this.state.showDetails}>
                <Alert severity="error" sx={{ textAlign: "left" }}>
                  <AlertTitle>Error Details</AlertTitle>
                  <Typography
                    variant="body2"
                    sx={{ fontFamily: "monospace", mt: 1 }}
                  >
                    <strong>Error:</strong> {this.state.error?.message}
                  </Typography>
                  {this.state.errorInfo && (
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: "monospace",
                        mt: 1,
                        whiteSpace: "pre-wrap",
                        fontSize: "0.75rem",
                      }}
                    >
                      <strong>Stack Trace:</strong>
                      {this.state.errorInfo.componentStack}
                    </Typography>
                  )}
                </Alert>
              </Collapse>
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

// API Error Display Component
export const ApiErrorAlert = ({
  error,
  onRetry,
  onDismiss,
}: {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}) => (
  <Alert
    severity="error"
    action={
      <Box sx={{ display: "flex", gap: 1 }}>
        {onRetry && (
          <Button color="inherit" size="small" onClick={onRetry}>
            Retry
          </Button>
        )}
        {onDismiss && (
          <Button color="inherit" size="small" onClick={onDismiss}>
            Dismiss
          </Button>
        )}
      </Box>
    }
    sx={{ mb: 2 }}
  >
    <AlertTitle>Request Failed</AlertTitle>
    {error}
  </Alert>
);

// Network Error Component
export const NetworkErrorCard = ({ onRetry }: { onRetry?: () => void }) => (
  <Card sx={{ textAlign: "center", p: 4, maxWidth: 400, mx: "auto" }}>
    <CardContent>
      <AlertTriangle size={48} color="#d32f2f" style={{ marginBottom: 16 }} />
      <Typography variant="h6" gutterBottom>
        Connection Error
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Unable to connect to the server. Please check your internet connection
        and try again.
      </Typography>
      {onRetry && (
        <Button
          variant="contained"
          startIcon={<RefreshCw size={16} />}
          onClick={onRetry}
        >
          Retry Connection
        </Button>
      )}
    </CardContent>
  </Card>
);

// Not Found Component
export const NotFoundError = () => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "50vh",
      textAlign: "center",
    }}
  >
    <Typography
      variant="h1"
      sx={{ fontSize: "6rem", fontWeight: "bold", color: "primary.main" }}
    >
      404
    </Typography>
    <Typography variant="h4" gutterBottom>
      Page Not Found
    </Typography>
    <Typography variant="body1" color="text.secondary" paragraph>
      The page you're looking for doesn't exist or has been moved.
    </Typography>
    <Button variant="contained" onClick={() => (window.location.href = "/")}>
      Go Home
    </Button>
  </Box>
);

// Validation Error Component
export const ValidationErrorAlert = ({
  errors,
}: {
  errors: Array<{ field: string; message: string }>;
}) => (
  <Alert severity="warning" sx={{ mb: 2 }}>
    <AlertTitle>Validation Errors</AlertTitle>
    <ul style={{ margin: 0, paddingLeft: 20 }}>
      {errors.map((error, index) => (
        <li key={index}>
          <strong>{error.field}:</strong> {error.message}
        </li>
      ))}
    </ul>
  </Alert>
);

// Generic Error Display
export const ErrorDisplay = ({
  title = "Error",
  message,
  onRetry,
  showReportButton = false,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
  showReportButton?: boolean;
}) => (
  <Box sx={{ textAlign: "center", p: 4 }}>
    <AlertTriangle size={48} color="#d32f2f" style={{ marginBottom: 16 }} />
    <Typography variant="h6" gutterBottom>
      {title}
    </Typography>
    <Typography variant="body2" color="text.secondary" paragraph>
      {message}
    </Typography>
    <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
      {onRetry && (
        <Button
          variant="contained"
          onClick={onRetry}
          startIcon={<RefreshCw size={16} />}
        >
          Try Again
        </Button>
      )}
      {showReportButton && (
        <Button variant="outlined" startIcon={<Bug size={16} />}>
          Report Issue
        </Button>
      )}
    </Box>
  </Box>
);
