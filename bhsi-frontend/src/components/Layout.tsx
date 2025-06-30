import React, { useState } from "react";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Menu as MenuIcon,
  BarChart3 as Dashboard,
  Search,
  FileUp,
  History,
  Settings,
  HelpCircle,
  Bell,
  LogOut,
  User,
  BarChart3,
} from "lucide-react";
import { useAuth } from "../auth/useAuth";
import { NotificationCenter } from "./NotificationSystem";
import { useNavigate, useLocation } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
  currentPage?: string;
}

const navigationItems = [
  { id: "dashboard", label: "Dashboard", icon: Dashboard, path: "/dashboard" },
  { id: "search", label: "Risk Assessment", icon: Search, path: "/" },
  { id: "analytics", label: "Analytics", icon: BarChart3, path: "/analytics" },
  { id: "batch", label: "Batch Upload", icon: FileUp, path: "/batch" },
  {
    id: "history",
    label: "Assessment History",
    icon: History,
    path: "/history",
  },
  { id: "settings", label: "Settings", icon: Settings, path: "/settings" },
  { id: "help", label: "Help & Support", icon: HelpCircle, path: "/help" },
];

const Layout = ({ children, currentPage = "search" }: LayoutProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(
    null
  );

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    logout();
  };

  const handleProfileClick = () => {
    handleUserMenuClose();
    navigate("/profile");
  };

  const handleSettingsClick = () => {
    handleUserMenuClose();
    navigate("/settings");
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  // Determine current page from location
  const getCurrentPage = () => {
    if (location.pathname === "/dashboard") return "dashboard";
    if (location.pathname === "/") return "search";
    if (location.pathname === "/analytics") return "analytics";
    if (location.pathname === "/batch") return "batch";
    if (location.pathname === "/history") return "history";
    if (location.pathname === "/settings") return "settings";
    if (location.pathname === "/help") return "help";
    return currentPage;
  };

  const drawerWidth = 280;

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Logo Section */}
      <Box sx={{ p: 3, bgcolor: "primary.main", color: "white" }}>
        <Typography variant="h6" fontWeight="bold">
          BHSI
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Risk Assessment Platform
        </Typography>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, px: 2, py: 1 }}>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = getCurrentPage() === item.id;
          return (
            <ListItem
              key={item.id}
              onClick={() => handleNavigation(item.path)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                bgcolor: isActive ? "primary.light" : "transparent",
                color: isActive ? "white" : "inherit",
                "&:hover": {
                  bgcolor: isActive ? "primary.light" : "grey.100",
                },
                cursor: "pointer",
                transition: "all 0.2s ease-in-out",
              }}
            >
              <ListItemIcon
                sx={{ color: isActive ? "white" : "inherit", minWidth: 40 }}
              >
                <Icon size={20} />
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: "0.9rem",
                  fontWeight: isActive ? 600 : 400,
                }}
              />
            </ListItem>
          );
        })}
      </List>

      {/* User Info Section */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Avatar
            sx={{ width: 32, height: 32, mr: 2, bgcolor: "primary.main" }}
          >
            {user?.name?.charAt(0).toUpperCase() || "U"}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight={500} noWrap>
              {user?.name || "User"}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.email || "user@bhsi.com"}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: "white",
          color: "text.primary",
          boxShadow: 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navigationItems.find((item) => item.id === getCurrentPage())
              ?.label || "Risk Assessment"}
          </Typography>

          {/* Notifications */}
          <NotificationCenter />

          {/* User Menu */}
          <IconButton
            onClick={handleUserMenuOpen}
            color="inherit"
            sx={{ ml: 1 }}
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main" }}>
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
          >
            <MenuItem onClick={handleProfileClick}>
              <ListItemIcon>
                <User size={20} />
              </ListItemIcon>
              <ListItemText>Profile</ListItemText>
            </MenuItem>
            <MenuItem onClick={handleSettingsClick}>
              <ListItemIcon>
                <Settings size={20} />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogOut size={20} />
              </ListItemIcon>
              <ListItemText>Sign Out</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              borderRight: 0,
              boxShadow: 2,
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          bgcolor: "grey.50",
          minHeight: "100vh",
        }}
      >
        <Toolbar /> {/* Spacer for fixed AppBar */}
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
