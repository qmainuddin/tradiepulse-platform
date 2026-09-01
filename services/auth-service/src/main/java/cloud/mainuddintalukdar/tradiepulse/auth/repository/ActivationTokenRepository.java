package cloud.mainuddintalukdar.tradiepulse.auth.repository;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.ActivationToken;
import cloud.mainuddintalukdar.tradiepulse.auth.domain.TokenType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ActivationTokenRepository extends JpaRepository<ActivationToken, UUID> {
    Optional<ActivationToken> findByTokenHash(String tokenHash);
    Optional<ActivationToken> findByTokenHashAndTokenType(String tokenHash, TokenType tokenType);
    void deleteByUserId(UUID userId);
}
