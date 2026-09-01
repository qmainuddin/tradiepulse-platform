package cloud.mainuddintalukdar.tradiepulse.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record AdminCompleteActivationRequest(
    @NotBlank(message = "Token is required")
    String token,

    @NotBlank(message = "Password is required")
    @Size(min = 10, message = "Admin password must be at least 10 characters")
    String password
) {}
