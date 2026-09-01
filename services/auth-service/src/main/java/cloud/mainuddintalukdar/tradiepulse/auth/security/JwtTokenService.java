package cloud.mainuddintalukdar.tradiepulse.auth.security;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class JwtTokenService {

    private final SecretKey key;
    private final long accessTokenExpirationMinutes;
    private final String issuer = "tradiepulse-auth";

    public JwtTokenService(
            @Value("${security.jwt.secret-key:change-me-to-a-secure-256-bit-secret-key-at-least-32-chars-long}") String secretKey,
            @Value("${security.jwt.access-token-expiration-minutes:15}") long accessTokenExpirationMinutes) {
        byte[] keyBytes = secretKey.getBytes(StandardCharsets.UTF_8);
        if (keyBytes.length < 32) {
            byte[] padded = new byte[32];
            System.arraycopy(keyBytes, 0, padded, 0, Math.min(keyBytes.length, 32));
            this.key = Keys.hmacShaKeyFor(padded);
        } else {
            this.key = Keys.hmacShaKeyFor(keyBytes);
        }
        this.accessTokenExpirationMinutes = accessTokenExpirationMinutes;
    }

    public String generateAccessToken(User user) {
        return generateTokenInternal(user, null, null);
    }

    public String generateImpersonationToken(User targetUser, User originalAdmin) {
        return generateTokenInternal(targetUser, targetUser.getId(), originalAdmin.getId());
    }

    private String generateTokenInternal(User user, UUID actAsUserId, UUID impersonatorId) {
        Instant now = Instant.now();
        Instant expiry = now.plus(accessTokenExpirationMinutes, ChronoUnit.MINUTES);

        Map<String, Object> claims = new HashMap<>();
        claims.put("email", user.getEmail());
        claims.put("role", user.getRole().name());
        claims.put("first_name", user.getFirstName());
        claims.put("last_name", user.getLastName());

        if (actAsUserId != null && impersonatorId != null) {
            claims.put("act_as", actAsUserId.toString());
            claims.put("impersonator_id", impersonatorId.toString());
            claims.put("is_impersonating", true);
        } else {
            claims.put("is_impersonating", false);
        }

        return Jwts.builder()
                .issuer(issuer)
                .subject(user.getId().toString())
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiry))
                .claims(claims)
                .signWith(key)
                .compact();
    }

    public Claims validateAndExtractClaims(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (JwtException | IllegalArgumentException e) {
            throw new InvalidJwtException("Invalid or expired JWT token: " + e.getMessage(), e);
        }
    }

    public long getAccessTokenExpirationSeconds() {
        return accessTokenExpirationMinutes * 60;
    }

    public static class InvalidJwtException extends RuntimeException {
        public InvalidJwtException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
