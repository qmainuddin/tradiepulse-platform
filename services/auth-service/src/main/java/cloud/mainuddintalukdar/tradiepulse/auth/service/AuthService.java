package cloud.mainuddintalukdar.tradiepulse.auth.service;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.*;
import cloud.mainuddintalukdar.tradiepulse.auth.dto.*;
import cloud.mainuddintalukdar.tradiepulse.auth.repository.*;
import cloud.mainuddintalukdar.tradiepulse.auth.security.JwtTokenService;
import cloud.mainuddintalukdar.tradiepulse.auth.security.LoginRateLimiter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HexFormat;
import java.util.UUID;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final ActivationTokenRepository activationTokenRepository;
    private final RefreshTokenFamilyRepository refreshTokenFamilyRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenService jwtTokenService;
    private final LoginRateLimiter loginRateLimiter;
    private final EmailService emailService;
    private final String domain;
    private final long activationExpiryHours;
    private final long refreshTokenExpiryDays;

    public AuthService(
            UserRepository userRepository,
            ActivationTokenRepository activationTokenRepository,
            RefreshTokenFamilyRepository refreshTokenFamilyRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenService jwtTokenService,
            LoginRateLimiter loginRateLimiter,
            EmailService emailService,
            @Value("${app.domain:tradiepulse.mainuddintalukdar.cloud}") String domain,
            @Value("${security.activation.expiry-hours:48}") long activationExpiryHours,
            @Value("${security.jwt.refresh-token-expiration-days:7}") long refreshTokenExpiryDays) {
        this.userRepository = userRepository;
        this.activationTokenRepository = activationTokenRepository;
        this.refreshTokenFamilyRepository = refreshTokenFamilyRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenService = jwtTokenService;
        this.loginRateLimiter = loginRateLimiter;
        this.emailService = emailService;
        this.domain = domain;
        this.activationExpiryHours = activationExpiryHours;
        this.refreshTokenExpiryDays = refreshTokenExpiryDays;
    }

    @Transactional
    public void signup(SignupRequest request) {
        if (userRepository.existsByEmail(request.email().toLowerCase())) {
            throw new IllegalArgumentException("User with this email already exists");
        }

        User user = new User(
                request.email().toLowerCase(),
                passwordEncoder.encode(request.password()),
                request.role(),
                request.firstName(),
                request.lastName()
        );
        user.setPhone(request.phone());
        user = userRepository.save(user);

        // Generate 48-hour activation token
        String rawToken = UUID.randomUUID().toString();
        String tokenHash = hashToken(rawToken);
        Instant expiry = Instant.now().plus(activationExpiryHours, ChronoUnit.HOURS);

        ActivationToken token = new ActivationToken(user.getId(), tokenHash, TokenType.email_activation, expiry);
        activationTokenRepository.save(token);

        emailService.sendEmailActivationLink(user.getEmail(), rawToken, domain);
    }

    @Transactional
    public void verifyEmail(String rawToken) {
        String tokenHash = hashToken(rawToken);
        ActivationToken token = activationTokenRepository.findByTokenHashAndTokenType(tokenHash, TokenType.email_activation)
                .orElseThrow(() -> new IllegalArgumentException("Invalid or non-existent activation token"));

        if (!token.isValid()) {
            throw new IllegalStateException("Activation link has expired or has already been used");
        }

        User user = userRepository.findById(token.getUserId())
                .orElseThrow(() -> new IllegalArgumentException("User associated with token not found"));

        token.setUsed(true);
        activationTokenRepository.save(token);

        user.setStatus(AccountStatus.active);
        userRepository.save(user);
    }

    @Transactional
    public TokenResponse login(LoginRequest request) {
        String email = request.email().toLowerCase();

        if (loginRateLimiter.isLocked(email)) {
            throw new IllegalStateException("Account temporarily locked due to too many failed login attempts. Try again later.");
        }

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> {
                    loginRateLimiter.recordFailedAttempt(email);
                    return new IllegalArgumentException("Invalid email or password");
                });

        if (user.getStatus() == AccountStatus.pending_verification) {
            throw new IllegalStateException("Account email has not been verified. Please check your activation link.");
        }

        if (user.getStatus() != AccountStatus.active) {
            throw new IllegalStateException("Account is suspended or deactivated.");
        }

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            loginRateLimiter.recordFailedAttempt(email);
            throw new IllegalArgumentException("Invalid email or password");
        }

        loginRateLimiter.resetAttempts(email);

        String accessToken = jwtTokenService.generateAccessToken(user);
        String rawRefreshToken = UUID.randomUUID().toString();
        String refreshTokenHash = hashToken(rawRefreshToken);

        Instant refreshExpiry = Instant.now().plus(refreshTokenExpiryDays, ChronoUnit.DAYS);
        RefreshTokenFamily family = refreshTokenFamilyRepository.findByUserId(user.getId())
                .map(existing -> {
                    existing.setCurrentTokenHash(refreshTokenHash);
                    existing.setRevoked(false);
                    existing.setExpiresAt(refreshExpiry);
                    return existing;
                })
                .orElseGet(() -> new RefreshTokenFamily(user.getId(), refreshTokenHash, refreshExpiry));

        refreshTokenFamilyRepository.save(family);

        return new TokenResponse(
                accessToken,
                rawRefreshToken,
                jwtTokenService.getAccessTokenExpirationSeconds(),
                user.getId(),
                user.getEmail(),
                user.getRole(),
                user.getFirstName(),
                user.getLastName(),
                false,
                null
        );
    }

    @Transactional
    public TokenResponse refreshToken(String rawRefreshToken) {
        String tokenHash = hashToken(rawRefreshToken);
        RefreshTokenFamily family = refreshTokenFamilyRepository.findByCurrentTokenHash(tokenHash)
                .orElseThrow(() -> new IllegalArgumentException("Invalid refresh token"));

        if (family.isRevoked() || !family.isValid(tokenHash)) {
            // Token reuse detected or expired: revoke family immediately
            family.setRevoked(true);
            refreshTokenFamilyRepository.save(family);
            throw new IllegalStateException("Compromised or expired refresh token. Family revoked. Please login again.");
        }

        User user = userRepository.findById(family.getUserId())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        if (user.getStatus() != AccountStatus.active) {
            throw new IllegalStateException("User account is not active");
        }

        String newAccessToken = jwtTokenService.generateAccessToken(user);
        String newRawRefreshToken = UUID.randomUUID().toString();
        String newRefreshTokenHash = hashToken(newRawRefreshToken);

        family.setCurrentTokenHash(newRefreshTokenHash);
        family.setExpiresAt(Instant.now().plus(refreshTokenExpiryDays, ChronoUnit.DAYS));
        refreshTokenFamilyRepository.save(family);

        return new TokenResponse(
                newAccessToken,
                newRawRefreshToken,
                jwtTokenService.getAccessTokenExpirationSeconds(),
                user.getId(),
                user.getEmail(),
                user.getRole(),
                user.getFirstName(),
                user.getLastName(),
                false,
                null
        );
    }

    @Transactional
    public void inviteAdmin(AdminInviteRequest request) {
        if (userRepository.existsByEmail(request.email().toLowerCase())) {
            throw new IllegalArgumentException("User with this email already exists");
        }

        User admin = new User(
                request.email().toLowerCase(),
                null, // Password will be set upon activation
                UserRole.admin,
                request.firstName(),
                request.lastName()
        );
        admin = userRepository.save(admin);

        String rawToken = UUID.randomUUID().toString();
        String tokenHash = hashToken(rawToken);
        Instant expiry = Instant.now().plus(activationExpiryHours, ChronoUnit.HOURS);

        ActivationToken token = new ActivationToken(admin.getId(), tokenHash, TokenType.admin_invite, expiry);
        activationTokenRepository.save(token);

        emailService.sendAdminInviteEmail(admin.getEmail(), rawToken, domain);
    }

    @Transactional
    public void completeAdminActivation(AdminCompleteActivationRequest request) {
        String tokenHash = hashToken(request.token());
        ActivationToken token = activationTokenRepository.findByTokenHashAndTokenType(tokenHash, TokenType.admin_invite)
                .orElseThrow(() -> new IllegalArgumentException("Invalid admin activation token"));

        if (!token.isValid()) {
            throw new IllegalStateException("Admin invite has expired or already used");
        }

        User admin = userRepository.findById(token.getUserId())
                .orElseThrow(() -> new IllegalArgumentException("Admin user not found"));

        admin.setPasswordHash(passwordEncoder.encode(request.password()));
        admin.setStatus(AccountStatus.active);
        userRepository.save(admin);

        token.setUsed(true);
        activationTokenRepository.save(token);
    }

    public static String hashToken(String rawToken) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(rawToken.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm missing", e);
        }
    }
}
