package cloud.mainuddintalukdar.tradiepulse.auth.service;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.AccountStatus;
import cloud.mainuddintalukdar.tradiepulse.auth.domain.User;
import cloud.mainuddintalukdar.tradiepulse.auth.domain.UserRole;
import cloud.mainuddintalukdar.tradiepulse.auth.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class SuperAdminBootstrap implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(SuperAdminBootstrap.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final String superAdminEmail;
    private final String superAdminPassword;

    public SuperAdminBootstrap(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            @Value("${superadmin.email:admin@mainuddintalukdar.cloud}") String superAdminEmail,
            @Value("${superadmin.password:change-me-superadmin-secure-pwd-123!}") String superAdminPassword) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.superAdminEmail = superAdminEmail.toLowerCase();
        this.superAdminPassword = superAdminPassword;
    }

    @Override
    public void run(String... args) {
        if (userRepository.findByRole(UserRole.super_admin).isEmpty()) {
            log.info("Bootstrapping initial Super-Admin account: {}", superAdminEmail);
            User superAdmin = new User(
                    superAdminEmail,
                    passwordEncoder.encode(superAdminPassword),
                    UserRole.super_admin,
                    "Platform",
                    "SuperAdmin"
            );
            superAdmin.setStatus(AccountStatus.active);
            userRepository.save(superAdmin);
            log.info("Super-Admin bootstrap completed successfully.");
        }
    }
}
