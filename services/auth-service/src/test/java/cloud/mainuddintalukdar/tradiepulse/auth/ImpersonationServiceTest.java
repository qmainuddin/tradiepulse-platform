package cloud.mainuddintalukdar.tradiepulse.auth;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.*;
import cloud.mainuddintalukdar.tradiepulse.auth.dto.*;
import cloud.mainuddintalukdar.tradiepulse.auth.repository.*;
import cloud.mainuddintalukdar.tradiepulse.auth.security.JwtTokenService;
import cloud.mainuddintalukdar.tradiepulse.auth.service.ImpersonationService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ImpersonationServiceTest {

    @Mock private UserRepository userRepository;
    @Mock private SecurityQuestionRepository securityQuestionRepository;
    @Mock private AuditLogRepository auditLogRepository;
    @Mock private JwtTokenService jwtTokenService;
    @Mock private PasswordEncoder passwordEncoder;

    private ImpersonationService impersonationService;

    @BeforeEach
    void setUp() {
        impersonationService = new ImpersonationService(
                userRepository,
                securityQuestionRepository,
                auditLogRepository,
                jwtTokenService,
                passwordEncoder
        );
    }

    @Test
    void shouldAllowAdminToImpersonateCustomerWhenStepUpAnswersMatch() {
        UUID adminId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();

        User admin = new User("support@tradiepulse.nz", "hash", UserRole.admin, "Support", "Lead");
        admin.setId(adminId);

        User customer = new User("customer@example.co.nz", "hash", UserRole.customer, "John", "Doe");
        customer.setId(customerId);

        SecurityQuestion q1 = new SecurityQuestion(customerId, "first_pet", "hashed_rover");

        when(userRepository.findById(adminId)).thenReturn(Optional.of(admin));
        when(userRepository.findById(customerId)).thenReturn(Optional.of(customer));
        when(securityQuestionRepository.findByUserId(customerId)).thenReturn(List.of(q1));
        when(passwordEncoder.matches("rover", "hashed_rover")).thenReturn(true);
        when(jwtTokenService.generateImpersonationToken(customer, admin)).thenReturn("mock_impersonation_jwt");

        ImpersonationRequest request = new ImpersonationRequest(customerId, Map.of("first_pet", "rover"), "Customer requested booking assistance over phone");

        TokenResponse response = impersonationService.verifyChallengeAndImpersonate(
                request, adminId, "127.0.0.1", "Mozilla/5.0", "corr-123"
        );

        assertNotNull(response);
        assertEquals("mock_impersonation_jwt", response.accessToken());
        assertTrue(response.isImpersonating());
        assertEquals(adminId, response.originalAdminId());

        verify(auditLogRepository).save(any(AuditLog.class));
    }

    @Test
    void shouldRejectImpersonationWhenStepUpAnswerFails() {
        UUID adminId = UUID.randomUUID();
        UUID customerId = UUID.randomUUID();

        User admin = new User("support@tradiepulse.nz", "hash", UserRole.admin, "Support", "Lead");
        admin.setId(adminId);

        User customer = new User("customer@example.co.nz", "hash", UserRole.customer, "John", "Doe");
        customer.setId(customerId);

        SecurityQuestion q1 = new SecurityQuestion(customerId, "first_pet", "hashed_rover");

        when(userRepository.findById(adminId)).thenReturn(Optional.of(admin));
        when(userRepository.findById(customerId)).thenReturn(Optional.of(customer));
        when(securityQuestionRepository.findByUserId(customerId)).thenReturn(List.of(q1));
        when(passwordEncoder.matches("wrong_pet", "hashed_rover")).thenReturn(false);

        ImpersonationRequest request = new ImpersonationRequest(customerId, Map.of("first_pet", "wrong_pet"), "Troubleshooting issue");

        assertThrows(IllegalArgumentException.class, () -> {
            impersonationService.verifyChallengeAndImpersonate(
                    request, adminId, "127.0.0.1", "Mozilla/5.0", "corr-123"
            );
        });

        // Verifies failed attempt was recorded to audit log
        verify(auditLogRepository).save(any(AuditLog.class));
    }

    @Test
    void shouldForbidImpersonatingSuperAdmin() {
        UUID adminId = UUID.randomUUID();
        UUID superAdminId = UUID.randomUUID();

        User admin = new User("support@tradiepulse.nz", "hash", UserRole.admin, "Support", "Lead");
        admin.setId(adminId);

        User superAdmin = new User("super@tradiepulse.nz", "hash", UserRole.super_admin, "Super", "Admin");
        superAdmin.setId(superAdminId);

        when(userRepository.findById(adminId)).thenReturn(Optional.of(admin));
        when(userRepository.findById(superAdminId)).thenReturn(Optional.of(superAdmin));

        ImpersonationRequest request = new ImpersonationRequest(superAdminId, Map.of("first_pet", "rover"), "Unauthorized attempt");

        assertThrows(IllegalArgumentException.class, () -> {
            impersonationService.verifyChallengeAndImpersonate(
                    request, adminId, "127.0.0.1", "Mozilla/5.0", "corr-123"
            );
        });
    }
}
