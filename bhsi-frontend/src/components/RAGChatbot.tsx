import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Paper,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
} from "@mui/material";
import {
  Send,
  Bot,
  User,
  FileText,
  Building2,
  Calendar,
  Globe,
  TrendingUp,
  Copy,
  RefreshCw,
  Lightbulb,
} from "lucide-react";
import { useAuth } from "../auth/useAuth";
import { 
  useAskRAGQuestionMutation, 
  useGetRAGExamplesQuery,
  type RAGQueryRequest,
  type RAGAnalysisResponse 
} from "../store/api/analyticsApi";

interface ChatMessage {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: Date;
  sources?: RAGDocumentSource[];
  confidence?: number;
  methodology?: string;
  responseTime?: number;
}

interface RAGDocumentSource {
  id: string;
  score: number;
  title: string;
  company: string;
  date: string;
  source: string;
  text_preview: string;
}



const RAGChatbot: React.FC = () => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      type: "bot",
      content: "¡Hola! Soy tu asistente de análisis de riesgos corporativos. Puedes hacerme preguntas sobre empresas españolas, riesgos financieros, legales, regulatorios y más. ¿En qué puedo ayudarte?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // RTK Query hooks
  const [askQuestion, { isLoading }] = useAskRAGQuestionMutation();
  const { data: examplesData } = useGetRAGExamplesQuery();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setError(null);

    try {
      const request: RAGQueryRequest = {
        question: userMessage.content,
        max_documents: 5,
        language: "es",
      };

      const response = await askQuestion(request).unwrap();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
        methodology: response.methodology,
        responseTime: response.response_time_ms,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      setError(
        err.data?.detail || "Error al procesar tu pregunta. Inténtalo de nuevo."
      );
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getRiskColor = (confidence: number) => {
    if (confidence >= 80) return "success";
    if (confidence >= 60) return "warning";
    return "error";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column", p: 2, bgcolor: "background.paper", borderRadius: 2, boxShadow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          <Bot size={20} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Asistente de Análisis de Riesgos
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Haz preguntas en lenguaje natural sobre riesgos corporativos
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Chat Messages */}
      <Paper
        sx={{
          flex: 1,
          overflow: "auto",
          p: 2,
          mb: 2,
          bgcolor: "grey.50",
          maxHeight: 500,
          borderRadius: 2,
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: "flex",
              justifyContent: message.type === "user" ? "flex-end" : "flex-start",
              mb: 2,
            }}
          >
            <Box
              sx={{
                maxWidth: "80%",
                display: "flex",
                flexDirection: "column",
                alignItems: message.type === "user" ? "flex-end" : "flex-start",
              }}
            >
              {/* Message Header */}
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  mb: 1,
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    bgcolor: message.type === "user" ? "primary.main" : "secondary.main",
                  }}
                >
                  {message.type === "user" ? <User size={16} /> : <Bot size={16} />}
                </Avatar>
                <Typography variant="caption" color="text.secondary">
                  {message.timestamp.toLocaleTimeString("es-ES", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Typography>
                {message.type === "bot" && message.confidence && (
                  <Chip
                    label={`${message.confidence}% confianza`}
                    size="small"
                    color={getRiskColor(message.confidence) as any}
                    variant="outlined"
                  />
                )}
              </Box>

              {/* Message Content */}
              <Card
                sx={{
                  bgcolor: message.type === "user" ? "primary.main" : "white",
                  color: message.type === "user" ? "white" : "text.primary",
                  boxShadow: 2,
                }}
              >
                <CardContent sx={{ py: 1.5, px: 2 }}>
                  <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                    {message.content}
                  </Typography>
                </CardContent>
              </Card>

              {/* Bot Message Metadata */}
              {message.type === "bot" && (message.sources || message.responseTime) && (
                <Box sx={{ mt: 1, display: "flex", gap: 1, flexWrap: "wrap" }}>
                  {message.responseTime && (
                    <Chip
                      label={`${message.responseTime}ms`}
                      size="small"
                      variant="outlined"
                      icon={<TrendingUp size={12} />}
                    />
                  )}
                  {message.methodology && (
                    <Chip
                      label={message.methodology}
                      size="small"
                      variant="outlined"
                      icon={<Lightbulb size={12} />}
                    />
                  )}
                  {message.sources && message.sources.length > 0 && (
                    <Chip
                      label={`${message.sources.length} fuentes`}
                      size="small"
                      variant="outlined"
                      icon={<FileText size={12} />}
                    />
                  )}
                </Box>
              )}

              {/* Sources Accordion */}
              {message.type === "bot" && message.sources && message.sources.length > 0 && (
                <Accordion sx={{ mt: 1, width: "100%" }}>
                  <AccordionSummary>
                    <Typography variant="caption">
                      Ver fuentes ({message.sources.length})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {message.sources.map((source, index) => (
                        <ListItem key={index} sx={{ px: 0 }}>
                          <ListItemIcon>
                            <FileText size={16} />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <Typography variant="body2" fontWeight={500}>
                                  {source.title}
                                </Typography>
                                <Chip
                                  label={`${source.score.toFixed(2)}`}
                                  size="small"
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="caption" display="block">
                                  <Building2 size={12} style={{ marginRight: 4 }} />
                                  {source.company} • {source.source} • {formatDate(source.date)}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {source.text_preview}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          </Box>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main" }}>
                <Bot size={16} />
              </Avatar>
              <Card sx={{ bgcolor: "white", boxShadow: 2 }}>
                <CardContent sx={{ py: 1.5, px: 2 }}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2">Analizando...</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Example Questions */}
      {examplesData?.spanish_examples && examplesData.spanish_examples.length > 0 && messages.length === 1 && (
        <Paper sx={{ p: 2, mb: 2, borderRadius: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            <Lightbulb size={16} style={{ marginRight: 8, verticalAlign: "middle" }} />
            Ejemplos de preguntas:
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {examplesData.spanish_examples.slice(0, 3).map((example: string, index: number) => (
              <Chip
                key={index}
                label={example}
                size="small"
                variant="outlined"
                onClick={() => setInputValue(example)}
                sx={{ cursor: "pointer" }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Input Area */}
      <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Escribe tu pregunta aquí... (ej: ¿Cuáles son los riesgos actuales para Banco Santander?)"
          disabled={isLoading}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 2,
            },
            bgcolor: "background.paper",
          }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          sx={{ minWidth: 56, borderRadius: 2 }}
        >
          <Send size={20} />
        </Button>
      </Box>
    </Box>
  );
};

export default RAGChatbot; 