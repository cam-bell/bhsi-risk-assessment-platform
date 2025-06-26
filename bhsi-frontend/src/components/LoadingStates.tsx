import React from 'react';
import {
  Box,
  CircularProgress,
  Skeleton,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Fade,
} from '@mui/material';
import { Search, FileText, TrendingUp } from 'lucide-react';

// Loading skeleton for search results
export const SearchResultSkeleton = () => (
  <Card sx={{ mb: 2 }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Skeleton variant="circular" width={60} height={60} sx={{ mr: 2 }} />
        <Box sx={{ flex: 1 }}>
          <Skeleton variant="text" width="40%" height={32} />
          <Skeleton variant="text" width="60%" height={20} />
        </Box>
      </Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
        <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
        <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
        <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
      </Box>
      <Skeleton variant="text" width="100%" />
      <Skeleton variant="text" width="80%" />
    </CardContent>
  </Card>
);

// Loading skeleton for dashboard stats
export const DashboardStatsSkeleton = () => (
  <Box sx={{ display: 'flex', gap: 3 }}>
    {[1, 2, 3, 4].map((item) => (
      <Card key={item} sx={{ flex: 1 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Skeleton variant="circular" width={48} height={48} sx={{ mr: 2 }} />
            <Box>
              <Skeleton variant="text" width={60} height={24} />
              <Skeleton variant="text" width={100} height={16} />
            </Box>
          </Box>
          <Skeleton variant="text" width="70%" />
        </CardContent>
      </Card>
    ))}
  </Box>
);

// Animated search loading
export const SearchLoading = () => (
  <Fade in>
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
      }}
    >
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        <CircularProgress size={60} thickness={4} />
        <Box
          sx={{
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Search size={24} color="#1976d2" />
        </Box>
      </Box>
      
      <Typography variant="h6" gutterBottom>
        Analyzing Company Risk...
      </Typography>
      <Typography variant="body2" color="text.secondary" textAlign="center">
        Our AI is processing financial data, corporate structure,<br />
        and market intelligence to provide accurate risk assessment.
      </Typography>
      
      <Box sx={{ width: '100%', maxWidth: 400, mt: 3 }}>
        <LinearProgress />
      </Box>
    </Box>
  </Fade>
);

// Batch processing loading
export const BatchProcessingLoading = ({ 
  processed, 
  total, 
  currentCompany 
}: { 
  processed: number; 
  total: number; 
  currentCompany?: string; 
}) => (
  <Fade in>
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
      }}
    >
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        <CircularProgress 
          variant="determinate" 
          value={(processed / total) * 100} 
          size={80} 
          thickness={4} 
        />
        <Box
          sx={{
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <FileText size={24} color="#1976d2" />
        </Box>
      </Box>
      
      <Typography variant="h6" gutterBottom>
        Processing Batch Analysis
      </Typography>
      <Typography variant="body1" gutterBottom>
        {processed} of {total} companies analyzed
      </Typography>
      {currentCompany && (
        <Typography variant="body2" color="text.secondary">
          Currently processing: {currentCompany}
        </Typography>
      )}
      
      <Box sx={{ width: '100%', maxWidth: 400, mt: 3 }}>
        <LinearProgress variant="determinate" value={(processed / total) * 100} />
      </Box>
    </Box>
  </Fade>
);

// Dashboard loading
export const DashboardLoading = () => (
  <Box sx={{ p: 3 }}>
    <Skeleton variant="text" width={200} height={40} sx={{ mb: 3 }} />
    
    {/* Stats Cards Loading */}
    <DashboardStatsSkeleton />
    
    {/* Charts Loading */}
    <Box sx={{ mt: 4, display: 'flex', gap: 3 }}>
      <Card sx={{ flex: 2 }}>
        <CardContent>
          <Skeleton variant="text" width={150} height={24} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={200} />
        </CardContent>
      </Card>
      
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Skeleton variant="text" width={120} height={24} sx={{ mb: 2 }} />
          {[1, 2, 3].map((item) => (
            <Box key={item} sx={{ mb: 2 }}>
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="text" width="80%" />
            </Box>
          ))}
        </CardContent>
      </Card>
    </Box>
  </Box>
);

// Generic page loading
export const PageLoading = ({ message = "Loading..." }: { message?: string }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '50vh',
    }}
  >
    <CircularProgress size={50} />
    <Typography variant="body1" sx={{ mt: 2 }}>
      {message}
    </Typography>
  </Box>
); 