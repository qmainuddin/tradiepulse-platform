import { z } from "zod";

export const UserRoleSchema = z.enum(["super_admin", "admin", "customer", "tradesperson"]);
export type UserRole = z.infer<typeof UserRoleSchema>;

export const AccountStatusSchema = z.enum(["pending_verification", "active", "suspended", "deactivated"]);
export type AccountStatus = z.infer<typeof AccountStatusSchema>;

export const SignupRequestSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  phone: z.string().optional(),
  role: UserRoleSchema,
});
export type SignupRequest = z.infer<typeof SignupRequestSchema>;

export const LoginRequestSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string().min(1, "Password is required"),
});
export type LoginRequest = z.infer<typeof LoginRequestSchema>;

export const TokenResponseSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string().nullable().optional(),
  expiresInSeconds: z.number(),
  userId: z.string().uuid(),
  email: z.string().email(),
  role: UserRoleSchema,
  firstName: z.string(),
  lastName: z.string(),
  isImpersonating: z.boolean(),
  originalAdminId: z.string().uuid().nullable().optional(),
});
export type TokenResponse = z.infer<typeof TokenResponseSchema>;

export const AdminInviteRequestSchema = z.object({
  email: z.string().email("Invalid email format"),
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
});
export type AdminInviteRequest = z.infer<typeof AdminInviteRequestSchema>;

export const ImpersonationChallengeSchema = z.object({
  targetUserId: z.string().uuid(),
  targetEmail: z.string().email(),
  targetName: z.string(),
  questionKeys: z.array(z.string()),
});
export type ImpersonationChallenge = z.infer<typeof ImpersonationChallengeSchema>;

export const ImpersonationRequestSchema = z.object({
  targetUserId: z.string().uuid(),
  answers: z.record(z.string(), z.string()),
  reason: z.string().min(5, "Reason must be at least 5 characters for audit compliance"),
});
export type ImpersonationRequest = z.infer<typeof ImpersonationRequestSchema>;
