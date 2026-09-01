package cloud.mainuddintalukdar.tradiepulse.auth.repository;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, UUID> {
    List<AuditLog> findByActorId(UUID actorId);
    List<AuditLog> findByImpersonatedUserId(UUID impersonatedUserId);
    List<AuditLog> findByCorrelationId(String correlationId);
}
