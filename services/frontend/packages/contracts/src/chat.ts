import { z } from "zod";

export const TradeTypeSchema = z.enum(["plumber", "electrician", "mechanic"]);
export type TradeType = z.infer<typeof TradeTypeSchema>;

export const CandidateTradieSchema = z.object({
  tradie_id: z.string(),
  name: z.string(),
  business_name: z.string(),
  trade: TradeTypeSchema,
  distance_meters: z.number(),
  service_radius_km: z.number(),
  rating_avg: z.number(),
  rating_count: z.number(),
  hourly_rate_nzd: z.number().nullable().optional(),
  phone: z.string().nullable().optional(),
});
export type CandidateTradie = z.infer<typeof CandidateTradieSchema>;

export const AgentTurnResponseSchema = z.object({
  message: z.string(),
  stage: z.string(),
  trade: TradeTypeSchema.nullable().optional(),
  location: z.string().nullable().optional(),
  matched_tradies: z.array(CandidateTradieSchema).default([]),
  cache_hit: z.boolean().default(false),
  tokens_used: z.number().default(0),
  estimated_cost_usd: z.number().default(0.0),
});
export type AgentTurnResponse = z.infer<typeof AgentTurnResponseSchema>;

export const ChatTurnRequestSchema = z.object({
  session_id: z.string().optional(),
  message: z.string().min(1, "Message cannot be empty"),
  media_urls: z.array(z.string()).default([]),
});
export type ChatTurnRequest = z.infer<typeof ChatTurnRequestSchema>;
