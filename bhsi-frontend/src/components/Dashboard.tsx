import React, { useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Chip,
  Stack,
  useTheme,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  Paper,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Users,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  Building2,
  Calendar,
  User,
  ChevronDown,
  Trash2,
  Eye,
  Filter,
} from "lucide-react";
import { useCompanies, AssessedCompany } from "../context/CompaniesContext";
import { useAuth } from "../auth/useAuth";
import { useNavigate } from "react-router-dom";

interface DashboardStats {
  totalAssessments: number;
  greenRisk: number;
  orangeRisk: number;
  redRisk: number;
  riskTrend: "up" | "down" | "stable";
  weeklyGrowth: number;
}

interface RecentActivity {
  id: string;
  company: string;
  risk: "green" | "orange" | "red";
  timestamp: string;
  assessedBy: string;
}

const mockStats: DashboardStats = {
  totalAssessments: 847,
  greenRisk: 421,
  orangeRisk: 312,
  redRisk: 114,
  riskTrend: "down",
  weeklyGrowth: 12.5,
};

const mockRecentActivity: RecentActivity[] = [
  {
    id: "1",
    company: "TechVision Global S.A.",
    risk: "green",
    timestamp: "2 hours ago",
    assessedBy: "sarah.martinez@bhsi.com",
  },
  {
    id: "2",
    company: "RiskCorp Industries",
    risk: "red",
    timestamp: "4 hours ago",
    assessedBy: "michael.wong@bhsi.com",
  },
  {
    id: "3",
    company: "ACME Solutions",
    risk: "orange",
    timestamp: "6 hours ago",
    assessedBy: "elena.rodriguez@bhsi.com",
  },
];

const StatCard = ({
  title,
  value,
  icon,
  color,
  subtitle,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: "primary" | "success" | "warning" | "error";
  subtitle?: string;
}) => {
  const theme = useTheme();

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: `${color}.main`,
              color: "white",
              width: 48,
              height: 48,
              mr: 2,
            }}
          >
            {icon}
          </Avatar>
          <Box>
            <Typography variant="h4" component="div" fontWeight="bold">
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const RiskDistributionCard = ({ stats }: { stats: DashboardStats }) => {
  const theme = useTheme();
  const total = stats.greenRisk + stats.orangeRisk + stats.redRisk;

  const greenPercent = (stats.greenRisk / total) * 100;
  const orangePercent = (stats.orangeRisk / total) * 100;
  const redPercent = (stats.redRisk / total) * 100;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Risk Distribution
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <Box>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
            >
              <Typography variant="body2">Low Risk (Green)</Typography>
              <Typography variant="body2" fontWeight="bold">
                {stats.greenRisk} ({greenPercent.toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={greenPercent}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: theme.palette.grey[200],
                "& .MuiLinearProgress-bar": {
                  backgroundColor: theme.palette.success.main,
                },
              }}
            />
          </Box>

          <Box>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
            >
              <Typography variant="body2">Medium Risk (Orange)</Typography>
              <Typography variant="body2" fontWeight="bold">
                {stats.orangeRisk} ({orangePercent.toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={orangePercent}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: theme.palette.grey[200],
                "& .MuiLinearProgress-bar": {
                  backgroundColor: theme.palette.warning.main,
                },
              }}
            />
          </Box>

          <Box>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
            >
              <Typography variant="body2">High Risk (Red)</Typography>
              <Typography variant="body2" fontWeight="bold">
                {stats.redRisk} ({redPercent.toFixed(1)}%)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={redPercent}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: theme.palette.grey[200],
                "& .MuiLinearProgress-bar": {
                  backgroundColor: theme.palette.error.main,
                },
              }}
            />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const RecentActivityCard = ({
  activities,
}: {
  activities: RecentActivity[];
}) => {
  const getRiskIcon = (risk: "green" | "orange" | "red") => {
    switch (risk) {
      case "green":
        return <CheckCircle size={16} color="#2e7d32" />;
      case "orange":
        return <AlertTriangle size={16} color="#ed6c02" />;
      case "red":
        return <XCircle size={16} color="#d32f2f" />;
    }
  };

  const getRiskColor = (risk: "green" | "orange" | "red") => {
    switch (risk) {
      case "green":
        return "success";
      case "orange":
        return "warning";
      case "red":
        return "error";
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {activities.map((activity) => (
            <Box
              key={activity.id}
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                p: 1,
                borderRadius: 1,
                bgcolor: "grey.50",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center" }}>
                {getRiskIcon(activity.risk)}
                <Box sx={{ ml: 2 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {activity.company}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    by {activity.assessedBy.split("@")[0]}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ textAlign: "right" }}>
                <Chip
                  label={activity.risk.toUpperCase()}
                  size="small"
                  color={getRiskColor(activity.risk) as any}
                  variant="outlined"
                />
                <Typography
                  variant="caption"
                  display="block"
                  color="text.secondary"
                >
                  {activity.timestamp}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

// Company Card Component
const CompanyCard = ({
  company,
  onView,
}: {
  company: AssessedCompany;
  onView: (company: AssessedCompany) => void;
}) => {
  const getRiskColor = (risk: "green" | "orange" | "red") => {
    switch (risk) {
      case "green":
        return "#2e7d32";
      case "orange":
        return "#ed6c02";
      case "red":
        return "#d32f2f";
    }
  };

  const getRiskIcon = (risk: "green" | "orange" | "red") => {
    switch (risk) {
      case "green":
        return <CheckCircle size={16} color="#2e7d32" />;
      case "orange":
        return <AlertTriangle size={16} color="#ed6c02" />;
      case "red":
        return <XCircle size={16} color="#d32f2f" />;
    }
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Card
      sx={{
        mb: 1,
        cursor: "pointer",
        transition: "all 0.2s",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: 3,
        },
        borderLeft: `4px solid ${getRiskColor(company.overallRisk)}`,
      }}
      onClick={() => onView(company)}
    >
      <CardContent sx={{ py: 2 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
              <Building2 size={16} style={{ marginRight: 8, color: "#666" }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {company.name}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {company.sector}
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
            >
              Assessed: {formatDate(company.assessedAt)} by {company.assessedBy}
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {getRiskIcon(company.overallRisk)}
            <Chip
              label={company.overallRisk.toUpperCase()}
              size="small"
              sx={{
                backgroundColor: getRiskColor(company.overallRisk),
                color: "white",
                fontWeight: "bold",
                fontSize: "0.7rem",
              }}
            />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const {
    getCompaniesByRisk,
    getTotalCompanies,
    getRecentAssessments,
    clearAllCompanies,
  } = useCompanies();
  const { user } = useAuth();

  const [selectedCompany, setSelectedCompany] =
    useState<AssessedCompany | null>(null);
  const [expandedSections, setExpandedSections] = useState({
    green: true,
    orange: true,
    red: true,
  });

  const greenCompanies = getCompaniesByRisk("green");
  const orangeCompanies = getCompaniesByRisk("orange");
  const redCompanies = getCompaniesByRisk("red");
  const totalCompanies = getTotalCompanies();
  const recentAssessments = getRecentAssessments(5);

  const handleSectionToggle = (section: "green" | "orange" | "red") => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const handleViewCompany = (company: AssessedCompany) => {
    setSelectedCompany(company);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Box>
          <Typography variant="h4" gutterBottom>
            Companies Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track and monitor all assessed companies by risk level
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Tooltip title="Clear all companies">
            <IconButton
              onClick={clearAllCompanies}
              disabled={totalCompanies === 0}
              color="error"
            >
              <Trash2 size={20} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Companies"
            value={totalCompanies}
            icon={<Building2 size={24} />}
            color="primary"
            subtitle="Assessed companies"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Low Risk"
            value={greenCompanies.length}
            icon={<CheckCircle size={24} />}
            color="success"
            subtitle={`${
              totalCompanies > 0
                ? Math.round((greenCompanies.length / totalCompanies) * 100)
                : 0
            }% of total`}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Medium Risk"
            value={orangeCompanies.length}
            icon={<AlertTriangle size={24} />}
            color="warning"
            subtitle={`${
              totalCompanies > 0
                ? Math.round((orangeCompanies.length / totalCompanies) * 100)
                : 0
            }% of total`}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="High Risk"
            value={redCompanies.length}
            icon={<XCircle size={24} />}
            color="error"
            subtitle={`${
              totalCompanies > 0
                ? Math.round((redCompanies.length / totalCompanies) * 100)
                : 0
            }% of total`}
          />
        </Grid>
      </Grid>

      {totalCompanies === 0 ? (
        <Card sx={{ textAlign: "center", py: 8 }}>
          <CardContent>
            <Building2 size={64} color="#ccc" style={{ marginBottom: 16 }} />
            <Typography variant="h6" gutterBottom>
              No Companies Assessed Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Start by searching and assessing companies on the Risk Assessment
              page. They will appear here organized by risk level.
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate("/risk-assessment")}
            >
              Go to Risk Assessment
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {/* Companies by Risk Level */}
          <Grid item xs={12} lg={8}>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {/* Low Risk Companies */}
              <Accordion
                expanded={expandedSections.green}
                onChange={() => handleSectionToggle("green")}
              >
                <AccordionSummary expandIcon={<ChevronDown />}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                    }}
                  >
                    <CheckCircle
                      size={24}
                      color="#2e7d32"
                      style={{ marginRight: 12 }}
                    />
                    <Typography
                      variant="h6"
                      sx={{ color: "#2e7d32", fontWeight: "bold" }}
                    >
                      Low Risk Companies
                    </Typography>
                    <Badge
                      badgeContent={greenCompanies.length}
                      color="success"
                      sx={{ ml: 2 }}
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {greenCompanies.length === 0 ? (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ py: 2 }}
                    >
                      No low risk companies assessed yet.
                    </Typography>
                  ) : (
                    <Box>
                      {greenCompanies.map((company) => (
                        <CompanyCard
                          key={company.id}
                          company={company}
                          onView={handleViewCompany}
                        />
                      ))}
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>

              {/* Medium Risk Companies */}
              <Accordion
                expanded={expandedSections.orange}
                onChange={() => handleSectionToggle("orange")}
              >
                <AccordionSummary expandIcon={<ChevronDown />}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                    }}
                  >
                    <AlertTriangle
                      size={24}
                      color="#ed6c02"
                      style={{ marginRight: 12 }}
                    />
                    <Typography
                      variant="h6"
                      sx={{ color: "#ed6c02", fontWeight: "bold" }}
                    >
                      Medium Risk Companies
                    </Typography>
                    <Badge
                      badgeContent={orangeCompanies.length}
                      color="warning"
                      sx={{ ml: 2 }}
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {orangeCompanies.length === 0 ? (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ py: 2 }}
                    >
                      No medium risk companies assessed yet.
                    </Typography>
                  ) : (
                    <Box>
                      {orangeCompanies.map((company) => (
                        <CompanyCard
                          key={company.id}
                          company={company}
                          onView={handleViewCompany}
                        />
                      ))}
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>

              {/* High Risk Companies */}
              <Accordion
                expanded={expandedSections.red}
                onChange={() => handleSectionToggle("red")}
              >
                <AccordionSummary expandIcon={<ChevronDown />}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                    }}
                  >
                    <XCircle
                      size={24}
                      color="#d32f2f"
                      style={{ marginRight: 12 }}
                    />
                    <Typography
                      variant="h6"
                      sx={{ color: "#d32f2f", fontWeight: "bold" }}
                    >
                      High Risk Companies
                    </Typography>
                    <Badge
                      badgeContent={redCompanies.length}
                      color="error"
                      sx={{ ml: 2 }}
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {redCompanies.length === 0 ? (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ py: 2 }}
                    >
                      No high risk companies assessed yet.
                    </Typography>
                  ) : (
                    <Box>
                      {redCompanies.map((company) => (
                        <CompanyCard
                          key={company.id}
                          company={company}
                          onView={handleViewCompany}
                        />
                      ))}
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            </Box>
          </Grid>

          {/* Recent Activity Sidebar */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Assessments
                </Typography>
                <Divider sx={{ mb: 2 }} />

                {recentAssessments.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No recent assessments
                  </Typography>
                ) : (
                  <List dense>
                    {recentAssessments.map((company, index) => (
                      <React.Fragment key={company.id}>
                        <ListItem
                          sx={{ px: 0, cursor: "pointer" }}
                          onClick={() => handleViewCompany(company)}
                        >
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            {company.overallRisk === "green" && (
                              <CheckCircle size={16} color="#2e7d32" />
                            )}
                            {company.overallRisk === "orange" && (
                              <AlertTriangle size={16} color="#ed6c02" />
                            )}
                            {company.overallRisk === "red" && (
                              <XCircle size={16} color="#d32f2f" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Typography variant="body2" fontWeight="medium">
                                {company.name}
                              </Typography>
                            }
                            secondary={
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                {new Date(
                                  company.assessedAt
                                ).toLocaleDateString()}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {index < recentAssessments.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;
