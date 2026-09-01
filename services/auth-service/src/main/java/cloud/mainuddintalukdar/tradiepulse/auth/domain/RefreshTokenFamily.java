package cloud.mainuddintalukdar.tradiepulse.auth.domain;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "refresh_token_families", schema = "identity")
public class RefreshTokenFamily {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "current_token_hash", nullable = false, unique = true)
    private String currentTokenHash;

    @Column(name = "is_revoked", nullable = false)
    private boolean isRevoked = false;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    public RefreshTokenFamily() {}

    public RefreshTokenFamily(UUID userId, String currentTokenHash, Instant expiresAt) {
        this.userId = userId;
        this.currentTokenHash = currentTokenHash;
        this.expiresAt = expiresAt;
        this.isRevoked = false;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }

    public UUID getId() { return id; }
    public UUID getUserId() { return userId; }
    public String getCurrentTokenHash() { return currentTokenHash; }
    public void setCurrentTokenHash(String currentTokenHash) {
        this.currentTokenHash = currentTokenHash;
        this.updatedAt = Instant.now();
    }
    public boolean isRevoked() { return isRevoked; }
    public void setRevoked(boolean revoked) { isRevoked = revoked; }
    public Instant getExpiresAt() { return expiresAt; }
    public void setExpiresAt(Instant expiresAt) { this.expiresAt = expiresAt; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }

    public boolean isValid(String tokenHash) {
        return !isRevoked && currentTokenHash.equals(tokenHash) && Instant.now().isBefore(expiresAt);
    }
}
