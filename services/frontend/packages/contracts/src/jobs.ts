import { z } from "zod";
import { TradeTypeSchema } from "./chat.js";

export const JobStatusSchema = z.enum([
  "draft",
  "matched",
  "assigned",
  "in_progress",
  "completed",
  "cancelled"
]);
export type JobStatus = z.infer<typeof JobStatusSchema>;

export const JobSchema = z.object({
  id: z.string().uuid(),
  customerId: z.string().uuid(),
  assignedTradieId: z.string().uuid().nullable().optional(),
  trade: TradeTypeSchema,
  title: z.string(),
  description: z.string(),
  status: JobStatusSchema,
  streetAddress: z.string(),
  suburb: z.string().optional(),
  city: z.string().default("Christchurch"),
  estimatedCostNzd: z.number().nullable().optional(),
  finalCostNzd: z.number().nullable().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});
export type Job = z.infer<typeof JobSchema>;

export const VerificationStageSchema = z.enum([
  "email_verified",
  "docs_submitted",
  "identity_checked",
  "licence_checked",
  "tax_checked",
  "references_checked",
  "approved",
  "rejected",
  "needs_info"
]);
export type VerificationStage = z.infer<typeof VerificationStageSchema>;

export const RatingSubmissionSchema = z.object({
  jobId: z.string().uuid(),
  score: z.number().int().min(1).max(5),
  feedbackText: z.string().optional(),
});
export type RatingSubmission = z.infer<typeof RatingSubmissionSchema>;
