import React, { useState, ChangeEvent } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Avatar,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemText,
  TextField,
  Button,
  Alert,
  IconButton,
  Tooltip,
} from "@mui/material";
import { useAuth } from "../auth/useAuth";
import { User, Lock, Camera } from "lucide-react";

const mockActivity = [
  {
    date: "2025-06-26",
    action: "Assessed ACME Solutions S.A.",
    risk: "orange",
  },
  {
    date: "2025-06-25",
    action: "Assessed TechVision Global S.A.",
    risk: "green",
  },
  {
    date: "2025-06-24",
    action: "Assessed RiskCorp Industries S.A.",
    risk: "red",
  },
];

const ProfilePage = () => {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [bio, setBio] = useState(
    "Experienced underwriter specializing in D&O risk assessment."
  );
  const [phone, setPhone] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [location, setLocation] = useState("");
  const [profilePhoto, setProfilePhoto] = useState<string | null>(null);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordChanged, setPasswordChanged] = useState(false);
  const [passwordError, setPasswordError] = useState("");

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordChanged(false);
    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }
    // For demo, just show success
    setPasswordChanged(true);
    setOldPassword("");
    setNewPassword("");
    setConfirmPassword("");
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  };

  const handleBioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBio(e.target.value);
  };

  const handlePhotoChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setProfilePhoto(ev.target?.result as string);
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh", py: 6 }}>
      <Container maxWidth="sm">
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Profile
        </Typography>
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Stack direction="row" spacing={3} alignItems="center" mb={2}>
              <Box sx={{ position: "relative" }}>
                <Avatar
                  src={profilePhoto || undefined}
                  sx={{
                    bgcolor: "primary.main",
                    width: 64,
                    height: 64,
                    fontSize: 32,
                  }}
                >
                  {!profilePhoto && <User size={36} />}
                </Avatar>
                <input
                  accept="image/*"
                  id="profile-photo-upload"
                  type="file"
                  style={{ display: "none" }}
                  onChange={handlePhotoChange}
                />
                <label htmlFor="profile-photo-upload">
                  <Tooltip title="Upload Photo">
                    <IconButton
                      component="span"
                      sx={{
                        position: "absolute",
                        bottom: -8,
                        right: -8,
                        bgcolor: "background.paper",
                        boxShadow: 1,
                        border: "1px solid #eee",
                        p: 0.5,
                        zIndex: 1,
                      }}
                    >
                      <Camera size={18} />
                    </IconButton>
                  </Tooltip>
                </label>
              </Box>
              <Box sx={{ flex: 1 }}>
                <TextField
                  label="Name"
                  value={name}
                  onChange={handleNameChange}
                  variant="standard"
                  sx={{ mb: 1, fontWeight: 600 }}
                  fullWidth
                />
                <Typography variant="body2" color="text.secondary">
                  {user?.email || "user@bhsi.com"}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Role: {user?.role || "Underwriter"}
                </Typography>
              </Box>
            </Stack>
            <TextField
              label="Short Bio"
              value={bio}
              onChange={handleBioChange}
              variant="outlined"
              fullWidth
              multiline
              minRows={2}
              sx={{ mb: 2 }}
            />
            <Stack spacing={2} direction="column" sx={{ mb: 2 }}>
              <TextField
                label="Phone Number"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                fullWidth
              />
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {mockActivity.map((item, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={item.action}
                    secondary={
                      item.date +
                      " • Risk: " +
                      item.risk.charAt(0).toUpperCase() +
                      item.risk.slice(1)
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
        {/* Change Password Section */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={2} mb={2}>
              <Lock size={24} />
              <Typography variant="h6">Change Password</Typography>
            </Stack>
            <form onSubmit={handlePasswordChange}>
              <Stack spacing={2}>
                <TextField
                  label="Old Password"
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  fullWidth
                  autoComplete="current-password"
                />
                <TextField
                  label="New Password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  fullWidth
                  autoComplete="new-password"
                />
                <TextField
                  label="Confirm New Password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  fullWidth
                  autoComplete="new-password"
                />
                {passwordError && (
                  <Alert severity="error">{passwordError}</Alert>
                )}
                {passwordChanged && (
                  <Alert severity="success">
                    Password changed successfully (demo only).
                  </Alert>
                )}
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  sx={{ alignSelf: "flex-end" }}
                >
                  Change Password
                </Button>
              </Stack>
            </form>
          </CardContent>
        </Card>
        <Typography variant="body2" color="text.secondary" align="center">
          &copy; {new Date().getFullYear()} Berkshire Hathaway Specialty
          Insurance. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default ProfilePage;
