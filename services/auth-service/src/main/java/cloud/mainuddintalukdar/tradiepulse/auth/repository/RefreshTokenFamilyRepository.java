package cloud.mainuddintalukdar.tradiepulse.auth.repository;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.RefreshTokenFamily;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface RefreshTokenFamilyRepository extends JpaRepository<RefreshTokenFamily, UUID> {
    Optional<RefreshTokenFamily> findByCurrentTokenHash(String currentTokenHash);
    Optional<RefreshTokenFamily> findByUserId(UUID userId);
}
