package cloud.mainuddintalukdar.tradiepulse.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.Map;
import java.util.UUID;

public record ImpersonationRequest(
    @NotNull(message = "Target user ID is required")
    UUID targetUserId,

    @NotEmpty(message = "Answers to security questions are required")
    Map<String, String> answers,

    @NotBlank(message = "Reason for impersonation is required for audit")
    String reason
) {}
