package cloud.mainuddintalukdar.tradiepulse.auth.domain;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "security_questions", schema = "identity",
       uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "question_key"}))
public class SecurityQuestion {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "question_key", nullable = false)
    private String questionKey;

    @Column(name = "hashed_answer", nullable = false)
    private String hashedAnswer;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    public SecurityQuestion() {}

    public SecurityQuestion(UUID userId, String questionKey, String hashedAnswer) {
        this.userId = userId;
        this.questionKey = questionKey;
        this.hashedAnswer = hashedAnswer;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public UUID getUserId() { return userId; }
    public String getQuestionKey() { return questionKey; }
    public String getHashedAnswer() { return hashedAnswer; }
    public Instant getCreatedAt() { return createdAt; }
}
