import { z } from "zod";
import { getCSRFToken } from "./django";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PaginatedSchema } from "./paginatedSchema";
import { UserSchema } from "./user";

export const EventHostingSchema = z.object({
  id: z.number(),
  event: z.number(),
  host: UserSchema,
  available_beds: z.number(),
  custom_rules: z.string().nullable(),
  address_override: z.string().nullable(),
  city_override: z.string().nullable(),
  zip_code_override: z.string().nullable(),
  country_override: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  host_name: z.string().optional(),
  available_beds_remaining: z.number().optional(),
});

export type EventHosting = z.infer<typeof EventHostingSchema>;

export const PaginatedEventHostingsSchema = PaginatedSchema(EventHostingSchema);
export type PaginatedEventHostings = z.infer<typeof PaginatedEventHostingsSchema>;

export const EventHostingRequestStatusEnum = z.enum(["PENDING", "ACCEPTED", "REJECTED", "CANCELLED"]);
export type EventHostingRequestStatus = z.infer<typeof EventHostingRequestStatusEnum>;

export const EventHostingRequestSchema = z.object({
  id: z.number(),
  hosting: z.number(),
  requester: z.union([z.number(), UserSchema]),
  status: EventHostingRequestStatusEnum,
  message: z.string().nullable(),
  host_message: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  requester_name: z.string().optional(),
  hosting_details: EventHostingSchema.optional(),
});

export type EventHostingRequest = z.infer<typeof EventHostingRequestSchema>;

export const PaginatedEventHostingRequestsSchema = PaginatedSchema(EventHostingRequestSchema);
export type PaginatedEventHostingRequests = z.infer<typeof PaginatedEventHostingRequestsSchema>;

export async function fetchEventHostings(eventId: number): Promise<PaginatedEventHostings> {
  const url = `/api/event/event-hostings/?event=${eventId}`;

  try {
    const resp = await fetch(url, {
      credentials: 'include'
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('Failed to fetch event hostings', errorText);
      throw new Error(`Failed to fetch event hostings: ${errorText}`);
    }

    const data = await resp.json();

    try {
      const parsed = PaginatedEventHostingsSchema.parse(data);
      return parsed;
    } catch (parseError) {
      console.error('Error parsing response data:', parseError);
      throw parseError;
    }
  } catch (error) {
    console.error('Error in fetchEventHostings:', error);
    throw error;
  }
}

export function useEventHostings(eventId: number | undefined) {
  return useQuery({
    queryKey: ["event-hostings", eventId],
    queryFn: () => eventId ? fetchEventHostings(eventId) : Promise.reject("No event ID"),
    enabled: !!eventId,
  });
}

export async function fetchUserHostings(): Promise<PaginatedEventHostings> {
  const resp = await fetch('/api/event/event-hostings/');
  if (!resp.ok) throw new Error('Failed to fetch user hostings');
  const data = await resp.json();
  return PaginatedEventHostingsSchema.parse(data);
}

export function useUserHostings() {
  return useQuery({
    queryKey: ["user-hostings"],
    queryFn: fetchUserHostings,
  });
}

export async function createEventHosting(hosting: Omit<EventHosting, "id" | "host" | "created_at" | "updated_at">): Promise<EventHosting> {
  const csrfToken = getCSRFToken();

  const resp = await fetch('/api/event/event-hostings/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify(hosting),
    credentials: 'include',
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));
    throw new Error(error.detail || 'Failed to create event hosting');
  }

  return EventHostingSchema.parse(await resp.json());
}

export function useCreateEventHosting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createEventHosting,
    onSuccess: () => {
      toast.success("Proposition d'hébergement créée avec succès");
      queryClient.invalidateQueries({ queryKey: ["event-hostings"] });
      queryClient.invalidateQueries({ queryKey: ["user-hostings"] });
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la création de l'hébergement: ${error.message}`);
    }
  });
}

export async function createEventHostingRequest(
  hostingId: number,
  message: string | null = null
): Promise<EventHostingRequest> {
  const csrfToken = getCSRFToken();

  const resp = await fetch('/api/event/event-hosting-requests/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify({ hosting_id: hostingId, message }),
    credentials: 'include',
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));
    throw new Error(error.detail || "Failed to create hosting request");
  }

  return EventHostingRequestSchema.parse(await resp.json());
}

export function useCreateEventHostingRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ hostingId, message }: { hostingId: number, message: string | null }) =>
      createEventHostingRequest(hostingId, message),
    onSuccess: () => {
      toast.success("Demande d'hébergement envoyée avec succès");
      queryClient.invalidateQueries({ queryKey: ["event-hosting-requests"] });
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la demande d'hébergement: ${error.message}`);
    }
  });
}

export async function fetchReceivedHostingRequests(): Promise<PaginatedEventHostingRequests> {
  const resp = await fetch('/api/event/event-hosting-requests/?as_host=true');
  if (!resp.ok) throw new Error('Failed to fetch received hosting requests');
  const data = await resp.json();
  return PaginatedEventHostingRequestsSchema.parse(data);
}

export function useReceivedHostingRequests() {
  return useQuery({
    queryKey: ["received-hosting-requests"],
    queryFn: fetchReceivedHostingRequests,
  });
}

export async function fetchSentHostingRequests(): Promise<PaginatedEventHostingRequests> {
  const resp = await fetch('/api/event/event-hosting-requests/?as_requester=true');
  if (!resp.ok) throw new Error('Failed to fetch sent hosting requests');
  const data = await resp.json();
  return PaginatedEventHostingRequestsSchema.parse(data);
}

export function useSentHostingRequests(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["sent-hosting-requests"],
    queryFn: fetchSentHostingRequests,
    enabled: options?.enabled !== undefined ? options.enabled : true,
  });
}

export async function updateHostingRequestStatus(
  requestId: number,
  status: EventHostingRequestStatus,
  hostMessage: string | null = null
): Promise<EventHostingRequest> {
  const csrfToken = getCSRFToken();

  const resp = await fetch(`/api/event/event-hosting-requests/${requestId}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify({ status, host_message: hostMessage }),
    credentials: 'include',
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));
    throw new Error(error.detail || "Failed to update hosting request status");
  }

  return EventHostingRequestSchema.parse(await resp.json());
}

export function useUpdateHostingRequestStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      requestId,
      status,
      hostMessage
    }: {
      requestId: number,
      status: EventHostingRequestStatus,
      hostMessage?: string | null
    }) => updateHostingRequestStatus(requestId, status, hostMessage),
    onSuccess: (_, variables) => {
      const actionMap: Record<EventHostingRequestStatus, string> = {
        ACCEPTED: "acceptée",
        REJECTED: "refusée",
        CANCELLED: "annulée",
        PENDING: "mise en attente",
      };

      toast.success(`Demande ${actionMap[variables.status]} avec succès`);
      queryClient.invalidateQueries({ queryKey: ["received-hosting-requests"] });
      queryClient.invalidateQueries({ queryKey: ["sent-hosting-requests"] });
      queryClient.invalidateQueries({ queryKey: ["event-hostings"] });
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la mise à jour de la demande: ${error.message}`);
    }
  });
}
