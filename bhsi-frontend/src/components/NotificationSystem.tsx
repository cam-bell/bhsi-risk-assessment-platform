import React, { useState, useContext, createContext, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Button,
  Box,
  IconButton,
  Slide,
  Stack,
  Typography,
  Paper,
  Badge,
  Menu,
  MenuItem,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
} from '@mui/material';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  X,
  Bell,
  Settings,
  Eye,
  Trash2,
} from 'lucide-react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  persistent?: boolean;
  actionLabel?: string;
  onAction?: () => void;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

// Slide transition for snackbars
const SlideTransition = (props: any) => {
  return <Slide {...props} direction="left" />;
};

// Toast notification component
const ToastNotification = ({
  notification,
  onClose,
}: {
  notification: Notification;
  onClose: () => void;
}) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle size={20} />;
      case 'error':
        return <XCircle size={20} />;
      case 'warning':
        return <AlertTriangle size={20} />;
      case 'info':
        return <Info size={20} />;
    }
  };

  return (
    <Snackbar
      open={true}
      autoHideDuration={notification.persistent ? null : 6000}
      onClose={onClose}
      TransitionComponent={SlideTransition}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        severity={notification.type}
        onClose={onClose}
        action={
          notification.actionLabel && notification.onAction ? (
            <Button color="inherit" size="small" onClick={notification.onAction}>
              {notification.actionLabel}
            </Button>
          ) : undefined
        }
        icon={getIcon()}
        sx={{ minWidth: 300 }}
      >
        <AlertTitle>{notification.title}</AlertTitle>
        {notification.message}
      </Alert>
    </Snackbar>
  );
};

// Notification center component
export const NotificationCenter = () => {
  const { notifications, markAsRead, markAllAsRead, clearAll, removeNotification } = useNotifications();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const unreadCount = notifications.filter(n => !n.read).length;
  const recentNotifications = notifications.slice(0, 5);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAsRead = (id: string) => {
    markAsRead(id);
  };

  const handleDelete = (id: string) => {
    removeNotification(id);
  };

  const getNotificationIcon = (type: NotificationType) => {
    const iconProps = { size: 16 };
    switch (type) {
      case 'success':
        return <CheckCircle {...iconProps} color="#2e7d32" />;
      case 'error':
        return <XCircle {...iconProps} color="#d32f2f" />;
      case 'warning':
        return <AlertTriangle {...iconProps} color="#ed6c02" />;
      case 'info':
        return <Info {...iconProps} color="#0288d1" />;
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        color="inherit"
        sx={{ ml: 1 }}
      >
        <Badge badgeContent={unreadCount} color="error">
          <Bell size={20} />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: { width: 380, maxHeight: 500 }
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6">Notifications</Typography>
            <Box>
              <IconButton size="small" onClick={markAllAsRead} disabled={unreadCount === 0}>
                <Eye size={16} />
              </IconButton>
              <IconButton size="small" onClick={clearAll} disabled={notifications.length === 0}>
                <Trash2 size={16} />
              </IconButton>
            </Box>
          </Box>
          {unreadCount > 0 && (
            <Typography variant="body2" color="text.secondary">
              {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </Typography>
          )}
        </Box>

        {notifications.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Bell size={48} color="#ccc" style={{ marginBottom: 8 }} />
            <Typography variant="body2" color="text.secondary">
              No notifications yet
            </Typography>
          </Box>
        ) : (
          <List sx={{ p: 0, maxHeight: 300, overflow: 'auto' }}>
            {recentNotifications.map((notification) => (
              <MenuItem
                key={notification.id}
                onClick={() => handleMarkAsRead(notification.id)}
                sx={{
                  backgroundColor: notification.read ? 'transparent' : 'action.hover',
                  borderLeft: notification.read ? 'none' : '3px solid',
                  borderLeftColor: 
                    notification.type === 'success' ? 'success.main' :
                    notification.type === 'error' ? 'error.main' :
                    notification.type === 'warning' ? 'warning.main' : 'info.main',
                  py: 1.5,
                  alignItems: 'flex-start',
                }}
              >
                <ListItemIcon sx={{ mt: 0.5 }}>
                  {getNotificationIcon(notification.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 'normal' : 'bold' }}>
                      {notification.title}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatTime(notification.timestamp)}
                      </Typography>
                    </Box>
                  }
                />
                <IconButton 
                  size="small" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(notification.id);
                  }}
                  sx={{ ml: 1 }}
                >
                  <X size={14} />
                </IconButton>
              </MenuItem>
            ))}
          </List>
        )}

        {notifications.length > 5 && (
          <>
            <Divider />
            <MenuItem onClick={handleClose} sx={{ justifyContent: 'center' }}>
              <Typography variant="body2" color="primary">
                View all notifications
              </Typography>
            </MenuItem>
          </>
        )}
      </Menu>
    </>
  );
};

// Main notification provider
export const NotificationProvider = ({ children }: { children: React.ReactNode }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [activeToasts, setActiveToasts] = useState<Notification[]>([]);

  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const notification: Notification = {
      ...notificationData,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => [notification, ...prev]);
    
    // Add to active toasts for display
    setActiveToasts(prev => [...prev, notification]);
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    setActiveToasts(prev => prev.filter(n => n.id !== id));
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
    setActiveToasts([]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setActiveToasts(prev => prev.filter(n => n.id !== id));
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        markAsRead,
        markAllAsRead,
        clearAll,
      }}
    >
      {children}
      
      {/* Render active toast notifications */}
      <Box sx={{ position: 'fixed', top: 80, right: 16, zIndex: 9999 }}>
        <Stack spacing={1}>
          {activeToasts.map((notification) => (
            <ToastNotification
              key={notification.id}
              notification={notification}
              onClose={() => removeToast(notification.id)}
            />
          ))}
        </Stack>
      </Box>
    </NotificationContext.Provider>
  );
};

// Utility hook for common notification patterns
export const useToast = () => {
  const { addNotification } = useNotifications();

  return {
    success: (title: string, message: string) => 
      addNotification({ type: 'success', title, message }),
    
    error: (title: string, message: string) => 
      addNotification({ type: 'error', title, message, persistent: true }),
    
    warning: (title: string, message: string) => 
      addNotification({ type: 'warning', title, message }),
    
    info: (title: string, message: string) => 
      addNotification({ type: 'info', title, message }),
  };
}; 