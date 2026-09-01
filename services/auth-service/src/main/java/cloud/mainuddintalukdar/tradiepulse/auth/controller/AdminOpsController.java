package cloud.mainuddintalukdar.tradiepulse.auth.controller;

import cloud.mainuddintalukdar.tradiepulse.auth.dto.*;
import cloud.mainuddintalukdar.tradiepulse.auth.service.AuthService;
import cloud.mainuddintalukdar.tradiepulse.auth.service.ImpersonationService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/auth/admin")
public class AdminOpsController {

    private final AuthService authService;
    private final ImpersonationService impersonationService;

    public AdminOpsController(AuthService authService, ImpersonationService impersonationService) {
        this.authService = authService;
        this.impersonationService = impersonationService;
    }

    @PostMapping("/invite")
    public ResponseEntity<Map<String, String>> inviteAdmin(@Valid @RequestBody AdminInviteRequest request) {
        authService.inviteAdmin(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "message", "Admin invitation dispatched successfully."
        ));
    }

    @GetMapping("/impersonate/challenge/{targetUserId}")
    public ResponseEntity<ImpersonationChallengeResponse> getImpersonationChallenge(
            @PathVariable UUID targetUserId,
            @RequestHeader(value = "X-User-Id") UUID adminId) {
        ImpersonationChallengeResponse challenge = impersonationService.getSecurityQuestionChallenge(targetUserId, adminId);
        return ResponseEntity.ok(challenge);
    }

    @PostMapping("/impersonate")
    public ResponseEntity<TokenResponse> impersonate(
            @Valid @RequestBody ImpersonationRequest request,
            @RequestHeader(value = "X-User-Id") UUID adminId,
            @RequestHeader(value = "X-Correlation-Id", required = false) String correlationId,
            HttpServletRequest servletRequest) {

        TokenResponse tokenResponse = impersonationService.verifyChallengeAndImpersonate(
                request,
                adminId,
                servletRequest.getRemoteAddr(),
                servletRequest.getHeader("User-Agent"),
                correlationId
        );
        return ResponseEntity.ok(tokenResponse);
    }
}
