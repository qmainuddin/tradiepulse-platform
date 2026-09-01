package cloud.mainuddintalukdar.tradiepulse.auth.repository;

import cloud.mainuddintalukdar.tradiepulse.auth.domain.SecurityQuestion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SecurityQuestionRepository extends JpaRepository<SecurityQuestion, UUID> {
    List<SecurityQuestion> findByUserId(UUID userId);
    Optional<SecurityQuestion> findByUserIdAndQuestionKey(UUID userId, String questionKey);
}
