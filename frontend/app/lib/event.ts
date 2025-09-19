import { z } from "zod";
import { PaginatedSchema } from "./paginatedSchema";

export const EventTypesSchema = z.enum(['CONGRESS', 'DRINK', 'OFFICE', 'OTHER']);
export type EventTypes = z.infer<typeof EventTypesSchema>;

export const SubscriptionStatsSchema = z.object({
  YES: z.number(),
  NO: z.number(),
  MAYBE: z.number(),
});

export type SubscriptionStats = z.infer<typeof SubscriptionStatsSchema>;

export const EventTypeSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().optional(),
  prices: z.string().optional(),
  start_date: z.string(),
  end_date: z.string(),
  location: z.string(),
  at_compiegne: z.boolean(),
  is_public: z.boolean(),
  type: EventTypesSchema,
  url_image: z.string().nullable().optional(),
  subscriptions_count: z.union([
    z.number(), // Pour rétrocompatibilité avec l'ancienne API
    SubscriptionStatsSchema
  ]).default({ YES: 0, NO: 0, MAYBE: 0 }),
  first_subscribers: z.array(z.string()).default([]),
});

export type EventType = z.infer<typeof EventTypeSchema>;

export const PaginatedEventsSchema = PaginatedSchema(EventTypeSchema);
export type PaginatedEvents = z.infer<typeof PaginatedEventsSchema>;

export async function fetchEvents(): Promise<PaginatedEvents> {
  const resp = await fetch('/api/event/events/');
  if (!resp.ok) throw new Error('Failed to fetch events');
  const data = await resp.json();
  return PaginatedEventsSchema.parse(data);
}

export function getEventTypes (status: EventTypes) {
  if (!status) {
      return null;
  }
  switch (status) {
      case 'CONGRESS':
          return 'Congrès';
      case 'DRINK':
          return 'Apéral';
      case 'OFFICE':
          return 'Office';
      case 'OTHER':
          return 'Autre';
  }
}
