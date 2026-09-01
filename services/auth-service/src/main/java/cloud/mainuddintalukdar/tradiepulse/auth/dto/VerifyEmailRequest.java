package cloud.mainuddintalukdar.tradiepulse.auth.dto;

import jakarta.validation.constraints.NotBlank;

public record VerifyEmailRequest(
    @NotBlank(message = "Token is required")
    String token
) {}
