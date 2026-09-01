package cloud.mainuddintalukdar.tradiepulse.auth;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.*;
import cloud.mainuddintalukdar.tradiepulse.auth.dto.*;
import cloud.mainuddintalukdar.tradiepulse.auth.repository.*;
import cloud.mainuddintalukdar.tradiepulse.auth.security.JwtTokenService;
import cloud.mainuddintalukdar.tradiepulse.auth.security.LoginRateLimiter;
import cloud.mainuddintalukdar.tradiepulse.auth.service.AuthService;
import cloud.mainuddintalukdar.tradiepulse.auth.service.EmailService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock private UserRepository userRepository;
    @Mock private ActivationTokenRepository activationTokenRepository;
    @Mock private RefreshTokenFamilyRepository refreshTokenFamilyRepository;
    @Mock private PasswordEncoder passwordEncoder;
    @Mock private JwtTokenService jwtTokenService;
    @Mock private EmailService emailService;

    private LoginRateLimiter loginRateLimiter;
    private AuthService authService;

    @BeforeEach
    void setUp() {
        loginRateLimiter = new LoginRateLimiter(5, 15);
        authService = new AuthService(
                userRepository,
                activationTokenRepository,
                refreshTokenFamilyRepository,
                passwordEncoder,
                jwtTokenService,
                loginRateLimiter,
                emailService,
                "tradiepulse.mainuddintalukdar.cloud",
                48,
                7
        );
    }

    @Test
    void shouldRegisterCustomerAndSendActivationEmail() {
        SignupRequest request = new SignupRequest("alex@example.co.nz", "SecurePwd123!", "Alex", "Smith", "0211234567", UserRole.customer);
        when(userRepository.existsByEmail("alex@example.co.nz")).thenReturn(false);
        when(passwordEncoder.encode("SecurePwd123!")).thenReturn("argon2_hash");

        User savedUser = new User("alex@example.co.nz", "argon2_hash", UserRole.customer, "Alex", "Smith");
        savedUser.setId(UUID.randomUUID());
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        authService.signup(request);

        verify(activationTokenRepository).save(any(ActivationToken.class));
        verify(emailService).sendEmailActivationLink(eq("alex@example.co.nz"), anyString(), anyString());
    }

    @Test
    void shouldVerifyEmailWithin48HourWindow() {
        UUID userId = UUID.randomUUID();
        String rawToken = UUID.randomUUID().toString();
        String tokenHash = AuthService.hashToken(rawToken);

        ActivationToken token = new ActivationToken(userId, tokenHash, TokenType.email_activation, Instant.now().plus(24, ChronoUnit.HOURS));
        User user = new User("alex@example.co.nz", "hash", UserRole.customer, "Alex", "Smith");
        user.setId(userId);
        user.setStatus(AccountStatus.pending_verification);

        when(activationTokenRepository.findByTokenHashAndTokenType(tokenHash, TokenType.email_activation)).thenReturn(Optional.of(token));
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));

        authService.verifyEmail(rawToken);

        assertTrue(token.isUsed());
        assertEquals(AccountStatus.active, user.getStatus());
        verify(userRepository).save(user);
    }

    @Test
    void shouldRejectExpiredActivationToken() {
        UUID userId = UUID.randomUUID();
        String rawToken = UUID.randomUUID().toString();
        String tokenHash = AuthService.hashToken(rawToken);

        // Expired 1 hour ago
        ActivationToken token = new ActivationToken(userId, tokenHash, TokenType.email_activation, Instant.now().minus(1, ChronoUnit.HOURS));

        when(activationTokenRepository.findByTokenHashAndTokenType(tokenHash, TokenType.email_activation)).thenReturn(Optional.of(token));

        assertThrows(IllegalStateException.class, () -> authService.verifyEmail(rawToken));
    }

    @Test
    void shouldRevokeFamilyOnRefreshTokenReuse() {
        UUID userId = UUID.randomUUID();
        String oldToken = "old_compromised_token";
        String oldHash = AuthService.hashToken(oldToken);

        // Family has already rotated to a new token
        RefreshTokenFamily family = new RefreshTokenFamily(userId, "new_active_hash", Instant.now().plus(7, ChronoUnit.DAYS));

        when(refreshTokenFamilyRepository.findByCurrentTokenHash(oldHash)).thenReturn(Optional.of(family));

        assertThrows(IllegalStateException.class, () -> authService.refreshToken(oldToken));
        assertTrue(family.isRevoked());
        verify(refreshTokenFamilyRepository).save(family);
    }
}
