package cloud.mainuddintalukdar.tradiepulse.auth.service;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.*;
import cloud.mainuddintalukdar.tradiepulse.auth.dto.*;
import cloud.mainuddintalukdar.tradiepulse.auth.repository.*;
import cloud.mainuddintalukdar.tradiepulse.auth.security.JwtTokenService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class ImpersonationService {

    private final UserRepository userRepository;
    private final SecurityQuestionRepository securityQuestionRepository;
    private final AuditLogRepository auditLogRepository;
    private final JwtTokenService jwtTokenService;
    private final PasswordEncoder passwordEncoder;

    public ImpersonationService(
            UserRepository userRepository,
            SecurityQuestionRepository securityQuestionRepository,
            AuditLogRepository auditLogRepository,
            JwtTokenService jwtTokenService,
            PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.securityQuestionRepository = securityQuestionRepository;
        this.auditLogRepository = auditLogRepository;
        this.jwtTokenService = jwtTokenService;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional(readOnly = true)
    public ImpersonationChallengeResponse getSecurityQuestionChallenge(UUID targetUserId, UUID adminId) {
        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new IllegalArgumentException("Admin not found"));
        validateAdminRole(admin);

        User targetUser = userRepository.findById(targetUserId)
                .orElseThrow(() -> new IllegalArgumentException("Target user not found"));

        List<SecurityQuestion> questions = securityQuestionRepository.findByUserId(targetUserId);
        if (questions.isEmpty()) {
            throw new IllegalStateException("Target user has no security questions configured for step-up verification");
        }

        List<String> questionKeys = questions.stream().map(SecurityQuestion::getQuestionKey).toList();

        return new ImpersonationChallengeResponse(
                targetUser.getId(),
                targetUser.getEmail(),
                targetUser.getFirstName() + " " + targetUser.getLastName(),
                questionKeys
        );
    }

    @Transactional
    public TokenResponse verifyChallengeAndImpersonate(
            ImpersonationRequest request,
            UUID adminId,
            String clientIp,
            String userAgent,
            String correlationId) {

        User admin = userRepository.findById(adminId)
                .orElseThrow(() -> new IllegalArgumentException("Admin not found"));
        validateAdminRole(admin);

        User targetUser = userRepository.findById(request.targetUserId())
                .orElseThrow(() -> new IllegalArgumentException("Target user not found"));

        if (targetUser.getRole() == UserRole.super_admin) {
            throw new IllegalArgumentException("Impersonation of Super-Admin accounts is strictly forbidden");
        }

        List<SecurityQuestion> questions = securityQuestionRepository.findByUserId(request.targetUserId());
        if (questions.isEmpty()) {
            throw new IllegalStateException("Target user has no security questions set");
        }

        // Verify each question answer
        for (SecurityQuestion sq : questions) {
            String submittedAnswer = request.answers().get(sq.getQuestionKey());
            if (submittedAnswer == null || !passwordEncoder.matches(submittedAnswer.trim().toLowerCase(), sq.getHashedAnswer())) {
                // Log failed step-up attempt
                auditLogRepository.save(new AuditLog(
                        admin.getId(),
                        admin.getEmail(),
                        admin.getRole(),
                        "IMPERSONATION_CHALLENGE_FAILED",
                        "user",
                        targetUser.getId(),
                        correlationId != null ? correlationId : UUID.randomUUID().toString(),
                        targetUser.getId(),
                        clientIp,
                        userAgent,
                        String.format("Failed step-up answer for question '%s'. Reason provided: %s", sq.getQuestionKey(), request.reason())
                ));
                throw new IllegalArgumentException("Invalid answer to security question: " + sq.getQuestionKey());
            }
        }

        // Generate scoped act_as token
        String impersonationToken = jwtTokenService.generateImpersonationToken(targetUser, admin);

        // Record successful impersonation in audit log
        auditLogRepository.save(new AuditLog(
                admin.getId(),
                admin.getEmail(),
                admin.getRole(),
                "IMPERSONATION_STARTED",
                "user",
                targetUser.getId(),
                correlationId != null ? correlationId : UUID.randomUUID().toString(),
                targetUser.getId(),
                clientIp,
                userAgent,
                String.format("Step-up challenge passed. Reason: %s", request.reason())
        ));

        return new TokenResponse(
                impersonationToken,
                null, // Refresh token is not issued during impersonation session
                jwtTokenService.getAccessTokenExpirationSeconds(),
                targetUser.getId(),
                targetUser.getEmail(),
                targetUser.getRole(),
                targetUser.getFirstName(),
                targetUser.getLastName(),
                true,
                admin.getId()
        );
    }

    private void validateAdminRole(User user) {
        if (user.getRole() != UserRole.admin && user.getRole() != UserRole.super_admin) {
            throw new SecurityException("Only users with Admin or Super-Admin role can perform step-up impersonation");
        }
    }
}
