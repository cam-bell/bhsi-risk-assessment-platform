import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
  Tooltip,
  Fab,
  Snackbar,
} from "@mui/material";
import {
  Plus,
  Edit,
  Delete,
  Eye,
  EyeOff,
  RefreshCw,
  UserPlus,
  Users,
} from "lucide-react";
import { useAuth } from "../auth/useAuth";
import axios from "axios";

interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: "admin" | "user";
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface CreateUserData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  user_type: "admin" | "user";
}

interface UpdateUserData {
  first_name?: string;
  last_name?: string;
  email?: string;
  user_type?: "admin" | "user";
  is_active?: boolean;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const UserManagementPage: React.FC = () => {
  const { user: currentUser, token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Form states
  const [createForm, setCreateForm] = useState<CreateUserData>({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    user_type: "user",
  });

  const [editForm, setEditForm] = useState<UpdateUserData>({});
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Check if current user is admin
  const isAdmin = currentUser?.user_type === "admin";

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [isAdmin]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      setFormErrors({});
      setLoading(true);

      // Validate form
      const errors: Record<string, string> = {};
      if (!createForm.email) errors.email = "Email is required";
      if (!createForm.first_name) errors.first_name = "First name is required";
      if (!createForm.last_name) errors.last_name = "Last name is required";
      if (!createForm.password) errors.password = "Password is required";
      if (createForm.password.length < 6)
        errors.password = "Password must be at least 6 characters";

      if (Object.keys(errors).length > 0) {
        setFormErrors(errors);
        return;
      }

      await axios.post(`${API_BASE_URL}/auth/users`, createForm, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setSuccess(
        `User ${createForm.first_name} ${createForm.last_name} created successfully`
      );
      setCreateDialogOpen(false);
      setCreateForm({
        email: "",
        first_name: "",
        last_name: "",
        password: "",
        user_type: "user",
      });
      fetchUsers();
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || "Failed to create user";
      setError(errorMessage);
      console.error("Create user error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    try {
      setFormErrors({});
      setLoading(true);

      // Validate form
      const errors: Record<string, string> = {};
      if (editForm.email && !editForm.email.includes("@")) {
        errors.email = "Invalid email format";
      }

      if (Object.keys(errors).length > 0) {
        setFormErrors(errors);
        return;
      }

      await axios.put(
        `${API_BASE_URL}/auth/users/${selectedUser.user_id}`,
        editForm,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setSuccess(
        `User ${selectedUser.first_name} ${selectedUser.last_name} updated successfully`
      );
      setEditDialogOpen(false);
      setSelectedUser(null);
      setEditForm({});
      fetchUsers();
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || "Failed to update user";
      setError(errorMessage);
      console.error("Update user error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!selectedUser) return;

    try {
      setLoading(true);
      await axios.delete(`${API_BASE_URL}/auth/users/${selectedUser.user_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setSuccess(
        `User ${selectedUser.first_name} ${selectedUser.last_name} deactivated successfully`
      );
      setDeleteDialogOpen(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || "Failed to deactivate user";
      setError(errorMessage);
      console.error("Deactivate user error:", err);
    } finally {
      setLoading(false);
    }
  };

  const openEditDialog = (user: User) => {
    setSelectedUser(user);
    setEditForm({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      user_type: user.user_type,
      is_active: user.is_active,
    });
    setEditDialogOpen(true);
  };

  const openDeleteDialog = (user: User) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isAdmin) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          You don't have permission to access this page. Admin access required.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            User Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage system users and permissions
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshCw />}
            onClick={fetchUsers}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<UserPlus />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Add User
          </Button>
        </Box>
      </Box>

      {/* Error/Success Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert
          severity="success"
          sx={{ mb: 2 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      {/* Users Table */}
      <Paper sx={{ width: "100%", overflow: "hidden" }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary">
                      No users found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.user_id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {user.first_name} {user.last_name}
                      </Typography>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.user_type}
                        color={
                          user.user_type === "admin" ? "primary" : "default"
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? "Active" : "Inactive"}
                        color={user.is_active ? "success" : "error"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell>
                      {user.last_login ? formatDate(user.last_login) : "Never"}
                    </TableCell>
                    <TableCell align="center">
                      <Box
                        sx={{
                          display: "flex",
                          gap: 1,
                          justifyContent: "center",
                        }}
                      >
                        <Tooltip title="Edit User">
                          <IconButton
                            size="small"
                            onClick={() => openEditDialog(user)}
                            disabled={user.user_id === currentUser?.user_id}
                          >
                            <Edit size={16} />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Deactivate User">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => openDeleteDialog(user)}
                            disabled={user.user_id === currentUser?.user_id}
                          >
                            <Delete size={16} />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create User Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            <TextField
              label="Email"
              type="email"
              value={createForm.email}
              onChange={(e) =>
                setCreateForm({ ...createForm, email: e.target.value })
              }
              error={!!formErrors.email}
              helperText={formErrors.email}
              fullWidth
            />
            <TextField
              label="First Name"
              value={createForm.first_name}
              onChange={(e) =>
                setCreateForm({ ...createForm, first_name: e.target.value })
              }
              error={!!formErrors.first_name}
              helperText={formErrors.first_name}
              fullWidth
            />
            <TextField
              label="Last Name"
              value={createForm.last_name}
              onChange={(e) =>
                setCreateForm({ ...createForm, last_name: e.target.value })
              }
              error={!!formErrors.last_name}
              helperText={formErrors.last_name}
              fullWidth
            />
            <TextField
              label="Password"
              type={showPassword ? "text" : "password"}
              value={createForm.password}
              onChange={(e) =>
                setCreateForm({ ...createForm, password: e.target.value })
              }
              error={!!formErrors.password}
              helperText={formErrors.password}
              fullWidth
              InputProps={{
                endAdornment: (
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <EyeOff /> : <Eye />}
                  </IconButton>
                ),
              }}
            />
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={createForm.user_type}
                onChange={(e) =>
                  setCreateForm({
                    ...createForm,
                    user_type: e.target.value as "admin" | "user",
                  })
                }
                label="Role"
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateUser} variant="contained">
            Create User
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
            <TextField
              label="Email"
              type="email"
              value={editForm.email || ""}
              onChange={(e) =>
                setEditForm({ ...editForm, email: e.target.value })
              }
              error={!!formErrors.email}
              helperText={formErrors.email}
              fullWidth
            />
            <TextField
              label="First Name"
              value={editForm.first_name || ""}
              onChange={(e) =>
                setEditForm({ ...editForm, first_name: e.target.value })
              }
              fullWidth
            />
            <TextField
              label="Last Name"
              value={editForm.last_name || ""}
              onChange={(e) =>
                setEditForm({ ...editForm, last_name: e.target.value })
              }
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={editForm.user_type || "user"}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    user_type: e.target.value as "admin" | "user",
                  })
                }
                label="Role"
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Switch
                  checked={editForm.is_active ?? true}
                  onChange={(e) =>
                    setEditForm({ ...editForm, is_active: e.target.checked })
                  }
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateUser} variant="contained">
            Update User
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete User Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Deactivate User</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to deactivate{" "}
            <strong>
              {selectedUser?.first_name} {selectedUser?.last_name}
            </strong>
            ? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteUser} color="error" variant="contained">
            Deactivate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagementPage;
