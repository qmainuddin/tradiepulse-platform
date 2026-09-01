package cloud.mainuddintalukdar.tradiepulse.auth;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.User;
import cloud.mainuddintalukdar.tradiepulse.auth.domain.UserRole;
import cloud.mainuddintalukdar.tradiepulse.auth.security.JwtTokenService;
import io.jsonwebtoken.Claims;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class JwtTokenServiceTest {

    private JwtTokenService jwtTokenService;
    private final String secretKey = "test-secret-key-that-is-at-least-32-bytes-long-for-hmac256!";

    @BeforeEach
    void setUp() {
        jwtTokenService = new JwtTokenService(secretKey, 15);
    }

    @Test
    void shouldGenerateAndValidateStandardAccessToken() {
        User user = new User("customer@example.co.nz", "hash", UserRole.customer, "John", "Doe");
        user.setId(UUID.randomUUID());

        String token = jwtTokenService.generateAccessToken(user);
        assertNotNull(token);

        Claims claims = jwtTokenService.validateAndExtractClaims(token);
        assertEquals(user.getId().toString(), claims.getSubject());
        assertEquals("customer@example.co.nz", claims.get("email"));
        assertEquals("customer", claims.get("role"));
        assertEquals("John", claims.get("first_name"));
        assertEquals(false, claims.get("is_impersonating"));
    }

    @Test
    void shouldGenerateImpersonationTokenWithActAsClaims() {
        User targetCustomer = new User("target@example.co.nz", "hash", UserRole.customer, "Target", "User");
        targetCustomer.setId(UUID.randomUUID());

        User adminUser = new User("admin@mainuddintalukdar.cloud", "hash", UserRole.admin, "Support", "Admin");
        adminUser.setId(UUID.randomUUID());

        String token = jwtTokenService.generateImpersonationToken(targetCustomer, adminUser);
        assertNotNull(token);

        Claims claims = jwtTokenService.validateAndExtractClaims(token);
        assertEquals(targetCustomer.getId().toString(), claims.getSubject());
        assertEquals(true, claims.get("is_impersonating"));
        assertEquals(targetCustomer.getId().toString(), claims.get("act_as"));
        assertEquals(adminUser.getId().toString(), claims.get("impersonator_id"));
    }

    @Test
    void shouldRejectTamperedToken() {
        User user = new User("customer@example.co.nz", "hash", UserRole.customer, "John", "Doe");
        user.setId(UUID.randomUUID());

        String token = jwtTokenService.generateAccessToken(user);
        String tamperedToken = token.substring(0, token.length() - 5) + "abcde";

        assertThrows(JwtTokenService.InvalidJwtException.class, () -> {
            jwtTokenService.validateAndExtractClaims(tamperedToken);
        });
    }
}
