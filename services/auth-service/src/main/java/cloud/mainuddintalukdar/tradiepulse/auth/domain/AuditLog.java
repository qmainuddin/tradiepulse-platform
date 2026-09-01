package cloud.mainuddintalukdar.tradiepulse.auth.domain;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "audit_log", schema = "audit")
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "actor_id", nullable = false)
    private UUID actorId;

    @Column(name = "actor_email", nullable = false)
    private String actorEmail;

    @Enumerated(EnumType.STRING)
    @Column(name = "actor_role", nullable = false)
    private UserRole actorRole;

    @Column(nullable = false)
    private String action;

    @Column(name = "target_type", nullable = false)
    private String targetType;

    @Column(name = "target_id")
    private UUID targetId;

    @Column(name = "correlation_id", nullable = false)
    private String correlationId;

    @Column(name = "impersonated_user_id")
    private UUID impersonatedUserId;

    @Column(name = "client_ip")
    private String clientIp;

    @Column(name = "user_agent")
    private String userAgent;

    @Column(columnDefinition = "TEXT")
    private String payload;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    public AuditLog() {}

    public AuditLog(UUID actorId, String actorEmail, UserRole actorRole, String action,
                    String targetType, UUID targetId, String correlationId,
                    UUID impersonatedUserId, String clientIp, String userAgent, String payload) {
        this.actorId = actorId;
        this.actorEmail = actorEmail;
        this.actorRole = actorRole;
        this.action = action;
        this.targetType = targetType;
        this.targetId = targetId;
        this.correlationId = correlationId;
        this.impersonatedUserId = impersonatedUserId;
        this.clientIp = clientIp;
        this.userAgent = userAgent;
        this.payload = payload;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public UUID getActorId() { return actorId; }
    public String getActorEmail() { return actorEmail; }
    public UserRole getActorRole() { return actorRole; }
    public String getAction() { return action; }
    public String getTargetType() { return targetType; }
    public UUID getTargetId() { return targetId; }
    public String getCorrelationId() { return correlationId; }
    public UUID getImpersonatedUserId() { return impersonatedUserId; }
    public String getClientIp() { return clientIp; }
    public String getUserAgent() { return userAgent; }
    public String getPayload() { return payload; }
    public Instant getCreatedAt() { return createdAt; }
}
