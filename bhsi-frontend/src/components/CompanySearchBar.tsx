import React, { useState } from "react";
import { useCompanies } from "../context/CompaniesContext";
import { TextField, Button, Box } from "@mui/material";

const CompanySearchBar: React.FC = () => {
  const { selectedCompany, setSelectedCompany } = useCompanies();
  const [input, setInput] = useState(selectedCompany || "");

  const handleSearch = () => {
    setSelectedCompany(input.trim() || null);
  };

  return (
    <Box display="flex" gap={2} mb={2}>
      <TextField
        label="Company Name"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        fullWidth
      />
      <Button
        variant="contained"
        onClick={handleSearch}
        disabled={!input.trim()}
      >
        Load Analytics
      </Button>
    </Box>
  );
};

export default CompanySearchBar;
