package cloud.mainuddintalukdar.tradiepulse.auth.dto;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.UserRole;
import java.util.UUID;

public record TokenResponse(
    String accessToken,
    String refreshToken,
    long expiresInSeconds,
    UUID userId,
    String email,
    UserRole role,
    String firstName,
    String lastName,
    boolean isImpersonating,
    UUID originalAdminId
) {}
