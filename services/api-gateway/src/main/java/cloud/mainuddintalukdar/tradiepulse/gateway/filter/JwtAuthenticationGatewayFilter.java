package cloud.mainuddintalukdar.tradiepulse.gateway.filter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;

@Component
public class JwtAuthenticationGatewayFilter implements GlobalFilter, Ordered {

    private final SecretKey secretKey;
    private final List<String> publicPathPrefixes = List.of(
            "/auth/signup",
            "/auth/login",
            "/auth/verify-email",
            "/auth/refresh",
            "/auth/activate-admin",
            "/actuator/health",
            "/actuator/info",
            "/api/health",
            "/favicon.ico"
    );

    public JwtAuthenticationGatewayFilter(
            @Value("${security.jwt.secret-key:change-me-to-a-secure-256-bit-secret-key-at-least-32-chars-long}") String secretKeyString) {
        byte[] keyBytes = secretKeyString.getBytes(StandardCharsets.UTF_8);
        if (keyBytes.length < 32) {
            byte[] padded = new byte[32];
            System.arraycopy(keyBytes, 0, padded, 0, Math.min(keyBytes.length, 32));
            this.secretKey = Keys.hmacShaKeyFor(padded);
        } else {
            this.secretKey = Keys.hmacShaKeyFor(keyBytes);
        }
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getURI().getPath();

        // 1. Strip any client-supplied identity headers to prevent header spoofing
        ServerHttpRequest.Builder requestBuilder = request.mutate()
                .headers(httpHeaders -> {
                    httpHeaders.remove("X-User-Id");
                    httpHeaders.remove("X-User-Roles");
                    httpHeaders.remove("X-User-Email");
                    httpHeaders.remove("X-Is-Impersonating");
                    httpHeaders.remove("X-Impersonator-Id");
                });

        // 2. Allow public endpoints without authentication
        if (isPublicPath(path)) {
            return chain.filter(exchange.mutate().request(requestBuilder.build()).build());
        }

        // 3. Extract and validate Bearer token
        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return writeUnauthorizedResponse(exchange, "Missing or malformed Authorization header");
        }

        String token = authHeader.substring(7);
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();

            String userId = claims.getSubject();
            String email = (String) claims.get("email");
            String role = (String) claims.get("role");
            Boolean isImpersonating = (Boolean) claims.get("is_impersonating");
            String impersonatorId = (String) claims.get("impersonator_id");

            // 4. Inject trusted headers for downstream microservices
            requestBuilder.header("X-User-Id", userId != null ? userId : "");
            requestBuilder.header("X-User-Email", email != null ? email : "");
            requestBuilder.header("X-User-Roles", role != null ? role : "");
            requestBuilder.header("X-Is-Impersonating", isImpersonating != null ? isImpersonating.toString() : "false");
            if (impersonatorId != null) {
                requestBuilder.header("X-Impersonator-Id", impersonatorId);
            }

            return chain.filter(exchange.mutate().request(requestBuilder.build()).build());

        } catch (JwtException | IllegalArgumentException e) {
            return writeUnauthorizedResponse(exchange, "Invalid, expired, or tampered JWT token: " + e.getMessage());
        }
    }

    private boolean isPublicPath(String path) {
        return publicPathPrefixes.stream().anyMatch(path::startsWith);
    }

    private Mono<Void> writeUnauthorizedResponse(ServerWebExchange exchange, String detail) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().setContentType(MediaType.APPLICATION_PROBLEM_JSON);

        String body = String.format("""
            {
                "type": "https://tradiepulse.mainuddintalukdar.cloud/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "%s",
                "timestamp": "%s"
            }
            """, detail.replace("\"", "'"), Instant.now());

        DataBuffer buffer = response.bufferFactory().wrap(body.getBytes(StandardCharsets.UTF_8));
        return response.writeWith(Mono.just(buffer));
    }

    @Override
    public int getOrder() {
        return -100; // Run early in filter chain
    }
}
