package cloud.mainuddintalukdar.tradiepulse.auth.dto;

import java.util.List;
import java.util.UUID;

public record ImpersonationChallengeResponse(
    UUID targetUserId,
    String targetEmail,
    String targetName,
    List<String> questionKeys
) {}
