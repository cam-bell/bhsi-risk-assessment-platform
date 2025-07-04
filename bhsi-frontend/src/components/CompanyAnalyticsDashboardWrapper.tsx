import React from "react";
import { useParams } from "react-router-dom";
import CompanyAnalyticsDashboard from "./CompanyAnalyticsDashboard";

const CompanyAnalyticsDashboardWrapper: React.FC = () => {
  const { companyName } = useParams<{ companyName: string }>();
  if (!companyName) return <div>No company selected.</div>;
  return <CompanyAnalyticsDashboard companyName={companyName} />;
};

export default CompanyAnalyticsDashboardWrapper;
