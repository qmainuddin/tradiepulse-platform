package cloud.mainuddintalukdar.tradiepulse.auth.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class LoginRateLimiter {

    private final int maxAttempts;
    private final int lockoutDurationMinutes;
    private final Map<String, AttemptRecord> attempts = new ConcurrentHashMap<>();

    public LoginRateLimiter(
            @Value("${security.rate-limit.max-attempts:5}") int maxAttempts,
            @Value("${security.rate-limit.lockout-duration-minutes:15}") int lockoutDurationMinutes) {
        this.maxAttempts = maxAttempts;
        this.lockoutDurationMinutes = lockoutDurationMinutes;
    }

    public boolean isLocked(String email) {
        AttemptRecord record = attempts.get(email.toLowerCase());
        if (record == null) {
            return false;
        }
        if (record.lockedUntil != null) {
            if (Instant.now().isBefore(record.lockedUntil)) {
                return true;
            }
            // Lockout expired, reset
            attempts.remove(email.toLowerCase());
            return false;
        }
        return false;
    }

    public void recordFailedAttempt(String email) {
        String key = email.toLowerCase();
        attempts.compute(key, (k, existing) -> {
            if (existing == null) {
                return new AttemptRecord(1, null);
            }
            int newCount = existing.count + 1;
            if (newCount >= maxAttempts) {
                Instant lockUntil = Instant.now().plus(lockoutDurationMinutes, ChronoUnit.MINUTES);
                return new AttemptRecord(newCount, lockUntil);
            }
            return new AttemptRecord(newCount, null);
        });
    }

    public void resetAttempts(String email) {
        attempts.remove(email.toLowerCase());
    }

    public static class AttemptRecord {
        final int count;
        final Instant lockedUntil;

        AttemptRecord(int count, Instant lockedUntil) {
            this.count = count;
            this.lockedUntil = lockedUntil;
        }
    }
}
