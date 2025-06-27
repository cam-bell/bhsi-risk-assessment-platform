import React from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Divider,
  Stack,
  Link,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { HelpCircle, Mail, Phone, Bug } from "lucide-react";

const faqs = [
  {
    question: "How do I perform a company risk assessment?",
    answer:
      "Go to the Risk Assessment page, enter a company name or VAT number, and click Get Score. You will receive an instant risk assessment with detailed results.",
  },
  {
    question: "What data sources are used?",
    answer:
      "The system uses official government sources (BOE) and business news to provide comprehensive risk analysis.",
  },
  {
    question: "How do I use Batch Upload?",
    answer:
      "Navigate to Batch Upload, upload a CSV or Excel file with company names, and the system will process multiple companies at once.",
  },
  {
    question: "Who can I contact for support?",
    answer:
      "See the Contact Support section below for email and phone support.",
  },
];

const HelpPage = () => {
  return (
    <Box sx={{ bgcolor: "grey.50", minHeight: "100vh", py: 6 }}>
      <Container maxWidth="md">
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Help & Support
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Find answers to common questions, troubleshooting tips, and ways to
          contact support for the BHSI Risk Assessment Platform.
        </Typography>
        <Grid container spacing={4}>
          {/* FAQ Section */}
          <Grid item xs={12} md={7}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <HelpCircle
                    size={28}
                    style={{ marginRight: 16, color: "#1976d2" }}
                  />
                  <Typography variant="h6">
                    Frequently Asked Questions
                  </Typography>
                </Box>
                <List>
                  {faqs.map((faq, idx) => (
                    <ListItem key={idx} alignItems="flex-start" sx={{ mb: 2 }}>
                      <ListItemText
                        primary={
                          <Typography fontWeight={600}>
                            {faq.question}
                          </Typography>
                        }
                        secondary={
                          <Typography color="text.secondary">
                            {faq.answer}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Contact & Troubleshooting */}
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              {/* Contact Support */}
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Mail
                      size={24}
                      style={{ marginRight: 12, color: "#1976d2" }}
                    />
                    <Typography variant="h6">Contact Support</Typography>
                  </Box>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 1 }}
                  >
                    For technical support or questions, contact our team:
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Email:</strong>{" "}
                    <Link href="mailto:support@bhsi.com">support@bhsi.com</Link>
                  </Typography>
                  <Typography variant="body2">
                    <strong>Phone:</strong>{" "}
                    <Link href="tel:+18001234567">+1 (800) 123-4567</Link>
                  </Typography>
                </CardContent>
              </Card>

              {/* Troubleshooting */}
              <Card>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Bug
                      size={24}
                      style={{ marginRight: 12, color: "#ed6c02" }}
                    />
                    <Typography variant="h6">Troubleshooting</Typography>
                  </Box>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Cannot sign in?"
                        secondary="Ensure your email and password are correct. For demo, use any email and a password of at least 6 characters."
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="No results found?"
                        secondary="Try different company names or check your API keys if running locally."
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Slow response times?"
                        secondary="The first request may take longer as the system initializes. Subsequent requests should be faster."
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Stack>
          </Grid>
        </Grid>
        <Divider sx={{ my: 4 }} />
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="body2" color="text.secondary">
            &copy; {new Date().getFullYear()} Berkshire Hathaway Specialty
            Insurance. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default HelpPage;
