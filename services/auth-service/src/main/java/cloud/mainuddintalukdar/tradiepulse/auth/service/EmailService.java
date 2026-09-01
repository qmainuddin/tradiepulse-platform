package cloud.mainuddintalukdar.tradiepulse.auth.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

@Service
public class EmailService {

    private static final Logger log = LoggerFactory.getLogger(EmailService.class);

    private final String resendApiKey;
    private final String fromEmail;
    private final HttpClient httpClient;

    public EmailService(
            @Value("${resend.api-key:re_mock_api_key}") String resendApiKey,
            @Value("${resend.from-email:noreply@mainuddintalukdar.cloud}") String fromEmail) {
        this.resendApiKey = resendApiKey;
        this.fromEmail = fromEmail;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();
    }

    public void sendEmailActivationLink(String toEmail, String token, String domain) {
        String activationUrl = String.format("https://%s/auth/verify-email?token=%s", domain, token);
        String subject = "Verify your TradiePulse Account";
        String body = String.format("""
            <p>Welcome to TradiePulse!</p>
            <p>Please activate your account by clicking the link below (valid for 48 hours):</p>
            <p><a href="%s">Activate My Account</a></p>
            <p>If you did not sign up for TradiePulse, you can safely ignore this email.</p>
            """, activationUrl);

        sendEmail(toEmail, subject, body);
    }

    public void sendAdminInviteEmail(String toEmail, String token, String domain) {
        String inviteUrl = String.format("https://%s/admin/activate?token=%s", domain, token);
        String subject = "You have been invited as a TradiePulse Admin";
        String body = String.format("""
            <p>You have been invited to join the TradiePulse Administration team.</p>
            <p>Please set your password and activate your admin account by clicking below:</p>
            <p><a href="%s">Accept Admin Invitation</a></p>
            """, inviteUrl);

        sendEmail(toEmail, subject, body);
    }

    public void sendEmail(String to, String subject, String htmlContent) {
        if (resendApiKey == null || resendApiKey.startsWith("re_mock") || resendApiKey.isBlank()) {
            log.info("[MOCK EMAIL DISPATCH] To: {}, Subject: {}, Preview: {}", to, subject, htmlContent.substring(0, Math.min(htmlContent.length(), 100)));
            return;
        }

        try {
            String jsonPayload = String.format("""
                {
                    "from": "%s",
                    "to": ["%s"],
                    "subject": "%s",
                    "html": "%s"
                }
                """, fromEmail, to, subject, htmlContent.replace("\"", "\\\"").replace("\n", ""));

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("https://api.resend.com/emails"))
                    .header("Authorization", "Bearer " + resendApiKey)
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                    .timeout(Duration.ofSeconds(10))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() >= 300) {
                log.error("Failed to send email via Resend: HTTP {} - {}", response.statusCode(), response.body());
            } else {
                log.info("Successfully sent email via Resend to {}", to);
            }
        } catch (Exception e) {
            log.error("Error while sending email via Resend: {}", e.getMessage(), e);
        }
    }
}
