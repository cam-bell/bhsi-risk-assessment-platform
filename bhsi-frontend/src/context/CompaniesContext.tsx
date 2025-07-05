import React, { createContext, useContext, useState, useCallback } from "react";

export interface AssessedCompany {
  id: string;
  name: string;
  vat: string;
  overallRisk: "green" | "orange" | "red";
  assessedAt: Date;
  assessedBy: string;
  industry?: string;
  revenue?: string;
  employees?: string;
  riskFactors: {
    turnover: "green" | "orange" | "red";
    shareholding: "green" | "orange" | "red";
    bankruptcy: "green" | "orange" | "red";
    legal: "green" | "orange" | "red";
  };
  confidence?: number;
}

interface CompaniesContextType {
  assessedCompanies: AssessedCompany[];
  addAssessedCompany: (
    company: Omit<AssessedCompany, "id" | "assessedAt">
  ) => void;
  getCompaniesByRisk: (risk: "green" | "orange" | "red") => AssessedCompany[];
  getTotalCompanies: () => number;
  getRecentAssessments: (limit?: number) => AssessedCompany[];
  clearAllCompanies: () => void;
  selectedCompany: string | null;
  setSelectedCompany: (company: string | null) => void;
}

const CompaniesContext = createContext<CompaniesContextType | undefined>(
  undefined
);

export const useCompanies = () => {
  const context = useContext(CompaniesContext);
  if (!context) {
    throw new Error("useCompanies must be used within a CompaniesProvider");
  }
  return context;
};

export const CompaniesProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [assessedCompanies, setAssessedCompanies] = useState<AssessedCompany[]>(
    () => {
      // Load from localStorage on initialization
      const stored = localStorage.getItem("assessedCompanies");
      return stored ? JSON.parse(stored) : [];
    }
  );

  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);

  const addAssessedCompany = useCallback(
    (companyData: Omit<AssessedCompany, "id" | "assessedAt">) => {
      const newCompany: AssessedCompany = {
        ...companyData,
        id: Math.random().toString(36).substr(2, 9),
        assessedAt: new Date(),
      };

      setAssessedCompanies((prev) => {
        // Check if the exact same company was assessed within the last hour
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        const existingIndex = prev.findIndex(
          (company) =>
            company.vat === newCompany.vat &&
            company.name.toLowerCase() === newCompany.name.toLowerCase() &&
            new Date(company.assessedAt) > oneHourAgo
        );

        let updatedCompanies;
        if (existingIndex >= 0) {
          // Update existing company (only if it's the same company assessed within the last hour)
          updatedCompanies = [...prev];
          updatedCompanies[existingIndex] = newCompany;
        } else {
          // Always add new company at the beginning
          updatedCompanies = [newCompany, ...prev];
        }

        // Keep only the last 100 assessments
        const limitedCompanies = updatedCompanies.slice(0, 100);

        // Save to localStorage
        localStorage.setItem(
          "assessedCompanies",
          JSON.stringify(limitedCompanies)
        );

        return limitedCompanies;
      });
    },
    []
  );

  const getCompaniesByRisk = useCallback(
    (risk: "green" | "orange" | "red") => {
      return assessedCompanies.filter(
        (company) => company.overallRisk === risk
      );
    },
    [assessedCompanies]
  );

  const getTotalCompanies = useCallback(() => {
    return assessedCompanies.length;
  }, [assessedCompanies]);

  const getRecentAssessments = useCallback(
    (limit = 10) => {
      return assessedCompanies
        .sort(
          (a, b) =>
            new Date(b.assessedAt).getTime() - new Date(a.assessedAt).getTime()
        )
        .slice(0, limit);
    },
    [assessedCompanies]
  );

  const clearAllCompanies = useCallback(() => {
    setAssessedCompanies([]);
    localStorage.removeItem("assessedCompanies");
  }, []);

  return (
    <CompaniesContext.Provider
      value={{
        assessedCompanies,
        addAssessedCompany,
        getCompaniesByRisk,
        getTotalCompanies,
        getRecentAssessments,
        clearAllCompanies,
        selectedCompany,
        setSelectedCompany,
      }}
    >
      {children}
    </CompaniesContext.Provider>
  );
};
