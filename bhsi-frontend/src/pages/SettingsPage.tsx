import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Avatar,
  Paper,
  Stack,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useAuth } from "../auth/useAuth";
import { Building2, Bell, User, Save } from "lucide-react";

const SettingsPage = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    name: user?.name || "",
    email: user?.email || "",
  });
  const [notifications, setNotifications] = useState({
    email: true,
    sms: false,
    push: true,
  });
  const [companyPrefs, setCompanyPrefs] = useState({
    defaultRiskView: "summary",
    showLegalNotices: true,
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleNotificationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNotifications({ ...notifications, [e.target.name]: e.target.checked });
  };

  const handleCompanyPrefsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCompanyPrefs({ ...companyPrefs, [e.target.name]: e.target.checked });
  };

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }, 1200);
  };

  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh", py: 6 }}>
      <Container maxWidth="md">
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage your profile, notification preferences, and company settings.
        </Typography>
        <Grid container spacing={4}>
          {/* User Profile */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <Avatar sx={{ bgcolor: "primary.main", mr: 2 }}>
                    <User size={28} />
                  </Avatar>
                  <Typography variant="h6">User Profile</Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  <TextField
                    label="Name"
                    name="name"
                    value={profile.name}
                    onChange={handleProfileChange}
                    fullWidth
                  />
                  <TextField
                    label="Email"
                    name="email"
                    value={profile.email}
                    onChange={handleProfileChange}
                    fullWidth
                    disabled
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Notification Preferences */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <Bell
                    size={28}
                    style={{
                      marginRight: 16,
                      color: theme.palette.primary.main,
                    }}
                  />
                  <Typography variant="h6">Notification Preferences</Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={notifications.email}
                        onChange={handleNotificationChange}
                        name="email"
                      />
                    }
                    label="Email Notifications"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={notifications.sms}
                        onChange={handleNotificationChange}
                        name="sms"
                      />
                    }
                    label="SMS Notifications"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={notifications.push}
                        onChange={handleNotificationChange}
                        name="push"
                      />
                    }
                    label="Push Notifications"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Company Preferences */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <Building2
                    size={28}
                    style={{
                      marginRight: 16,
                      color: theme.palette.primary.main,
                    }}
                  />
                  <Typography variant="h6">Company Preferences</Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={companyPrefs.showLegalNotices}
                        onChange={handleCompanyPrefsChange}
                        name="showLegalNotices"
                      />
                    }
                    label="Show Legal Notices by Default"
                  />
                  {/* Add more company-specific settings as needed */}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        <Divider sx={{ my: 4 }} />
        <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Save />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : saved ? "Saved!" : "Save Changes"}
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default SettingsPage;
