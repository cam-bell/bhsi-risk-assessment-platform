import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { 
  TrendingUp, 
  Globe, 
  Users, 
  Award 
} from 'lucide-react';

// Stats data
const statsData = [
  {
    title: 'Written Premium',
    value: '€5B+',
    icon: <TrendingUp size={24} />,
    color: '#003366',
  },
  {
    title: 'Global Branches',
    value: '30+',
    icon: <Globe size={24} />,
    color: '#8C1D40',
  },
  {
    title: 'Industry Experts',
    value: '2,500+',
    icon: <Users size={24} />,
    color: '#006064',
  },
  {
    title: 'AM Best Rating',
    value: 'A++',
    icon: <Award size={24} />,
    color: '#2e7d32',
  },
];

const StatsCards = () => {
  return (
    <Grid container spacing={3}>
      {statsData.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: '12px',
                    display: 'flex',
                    backgroundColor: `${stat.color}10`,
                    color: stat.color,
                    mr: 2,
                  }}
                >
                  {stat.icon}
                </Box>
                <Typography variant="h6" component="div">
                  {stat.title}
                </Typography>
              </Box>
              <Typography
                variant="h3"
                component="div"
                sx={{ fontWeight: 700, color: stat.color }}
              >
                {stat.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StatsCards;