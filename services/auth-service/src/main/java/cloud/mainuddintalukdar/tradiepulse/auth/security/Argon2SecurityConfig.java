package cloud.mainuddintalukdar.tradiepulse.auth.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.argon2.Argon2PasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class Argon2SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        // OWASP recommended Argon2id parameters: salt 16 bytes, hash 32 bytes, parallelism 1, memory 65536 KB (64MB), iterations 3
        return new Argon2PasswordEncoder(16, 32, 1, 65536, 3);
    }
}
