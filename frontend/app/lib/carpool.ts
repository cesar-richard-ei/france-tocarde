import { z } from "zod";
import { getCSRFToken } from "./django";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PaginatedSchema } from "./paginatedSchema";
import { EventTypeSchema } from "./event";
import { UserSchema } from "./user";

export const CarpoolTripSchema = z.object({
  id: z.number(),
  driver: UserSchema,
  event: EventTypeSchema,
  departure_city: z.string(),
  departure_address: z.string().nullable(),
  arrival_city: z.string(),
  arrival_address: z.string().nullable(),
  departure_datetime: z.string(),
  return_datetime: z.string().nullable(),
  has_return: z.boolean(),
  seats_total: z.number(),
  price_per_seat: z.string(),
  additional_info: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  seats_available: z.number(),
  is_full: z.boolean(),
});

export type CarpoolTrip = z.infer<typeof CarpoolTripSchema>;

export const PaginatedCarpoolTripsSchema = PaginatedSchema(CarpoolTripSchema);
export type PaginatedCarpoolTrips = z.infer<typeof PaginatedCarpoolTripsSchema>;

export const CarpoolRequestStatusEnum = z.enum(["PENDING", "ACCEPTED", "REJECTED", "CANCELLED"]);
export type CarpoolRequestStatus = z.infer<typeof CarpoolRequestStatusEnum>;

export const CarpoolRequestSchema = z.object({
  id: z.number(),
  passenger: UserSchema,
  trip: CarpoolTripSchema,
  status: CarpoolRequestStatusEnum,
  seats_requested: z.number(),
  message: z.string().nullable(),
  response_message: z.string().nullable(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  is_paid: z.boolean(),
  total_paid: z.number(),
  expected_amount: z.number(),
});

export type CarpoolRequest = z.infer<typeof CarpoolRequestSchema>;

export const PaginatedCarpoolRequestsSchema = PaginatedSchema(CarpoolRequestSchema);
export type PaginatedCarpoolRequests = z.infer<typeof PaginatedCarpoolRequestsSchema>;

export const CarpoolPaymentSchema = z.object({
  id: z.number(),
  request: z.union([
    z.number(),
    z.object({}).transform(() => 0),
    z.string().transform(val => Number(val) || 0)
  ]),
  amount: z.union([
    z.number(),
    z.string().transform(val => Number(val) || 0)
  ]),
  payment_method: z.string(),
  is_completed: z.boolean(),
  payment_notes: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  request_details: CarpoolRequestSchema.optional(),
});

export type CarpoolPayment = z.infer<typeof CarpoolPaymentSchema>;

export const PaginatedCarpoolPaymentsSchema = PaginatedSchema(CarpoolPaymentSchema);
export type PaginatedCarpoolPayments = z.infer<typeof PaginatedCarpoolPaymentsSchema>;

// Fonctions pour récupérer les trajets pour un événement
export async function fetchEventCarpoolTrips(eventId: number): Promise<PaginatedCarpoolTrips> {
  const url = `/api/event/carpool-trips/?event=${eventId}`;

  try {
    const resp = await fetch(url, {
      credentials: 'include'
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('Failed to fetch event carpool trips', errorText);
      throw new Error(`Failed to fetch event carpool trips: ${errorText}`);
    }

    const data = await resp.json();

    // Vérifier si les données sont conformes au schéma attendu
    try {
      const parsed = PaginatedCarpoolTripsSchema.parse(data);
      return parsed;
    } catch (parseError) {
      throw parseError;
    }
  } catch (error) {
    console.error('Error in fetchEventCarpoolTrips:', error);
    throw error;
  }
}

// Hook pour récupérer les trajets d'un événement
export function useEventCarpoolTrips(eventId: number | undefined, options?: { enabled?: boolean }) {
  const enabled = options?.enabled !== undefined ? options.enabled && !!eventId : !!eventId;
  return useQuery({
    queryKey: ["event-carpool-trips", eventId],
    queryFn: () => eventId ? fetchEventCarpoolTrips(eventId) : Promise.reject("No event ID"),
    enabled,
  });
}

// Fonction pour récupérer les trajets proposés par l'utilisateur
export async function fetchUserCarpoolTrips(): Promise<PaginatedCarpoolTrips> {
  const resp = await fetch('/api/event/carpool-trips/?as_driver=true');
  if (!resp.ok) throw new Error('Failed to fetch user carpool trips');
  const data = await resp.json();
  return PaginatedCarpoolTripsSchema.parse(data);
}

// Hook pour récupérer les trajets proposés par l'utilisateur
export function useUserCarpoolTrips(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["user-carpool-trips"],
    queryFn: fetchUserCarpoolTrips,
    enabled: options?.enabled !== undefined ? options.enabled : true,
  });
}

// Fonction pour créer un trajet de covoiturage
export async function createCarpoolTrip(trip: Omit<CarpoolTrip, "id" | "driver" | "created_at" | "updated_at">): Promise<CarpoolTrip> {
  const csrfToken = getCSRFToken();

  const resp = await fetch('/api/event/carpool-trips/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify(trip),
    credentials: 'include',
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));
    throw new Error(error.detail || 'Failed to create carpool trip');
  }

  return CarpoolTripSchema.parse(await resp.json());
}

// Hook pour créer un trajet de covoiturage
export function useCreateCarpoolTrip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createCarpoolTrip,
    onSuccess: (data) => {
      toast.success("Trajet de covoiturage créé avec succès");
      queryClient.invalidateQueries({ queryKey: ["event-carpool-trips"] });
      queryClient.invalidateQueries({ queryKey: ["user-carpool-trips"] });

      if (data.event) {
        queryClient.invalidateQueries({ queryKey: ["event-carpool-trips", data.event] });
      }
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la création du trajet: ${error.message}`);
    }
  });
}

// Fonction pour créer une demande de covoiturage
export async function createCarpoolRequest(
  tripId: number,
  seatsRequested: number = 1,
  message: string | null = null
): Promise<CarpoolRequest> {
  const csrfToken = getCSRFToken();

  const resp = await fetch('/api/event/carpool-requests/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify({
      trip_id: tripId,
      seats_requested: seatsRequested,
      message
    }),
    credentials: 'include',
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));

    // Gérer les erreurs de validation Django REST Framework
    if (errorData.passenger) {
      throw new Error(errorData.passenger[0] || errorData.passenger);
    }
    if (errorData.trip_id) {
      throw new Error(errorData.trip_id[0] || errorData.trip_id);
    }
    if (errorData.trip) {
      throw new Error(errorData.trip[0] || errorData.trip);
    }
    if (errorData.seats_requested) {
      throw new Error(errorData.seats_requested[0] || errorData.seats_requested);
    }
    if (errorData.message) {
      throw new Error(errorData.message[0] || errorData.message);
    }

    // Erreur générique
    throw new Error(errorData.detail || "Failed to create carpool request");
  }

  return CarpoolRequestSchema.parse(await resp.json());
}

// Hook pour créer une demande de covoiturage
export function useCreateCarpoolRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      tripId,
      seatsRequested,
      message
    }: {
      tripId: number,
      seatsRequested?: number,
      message?: string | null
    }) => createCarpoolRequest(tripId, seatsRequested, message),
    onSuccess: () => {
      toast.success("Demande de covoiturage envoyée avec succès");
      queryClient.invalidateQueries({ queryKey: ["sent-carpool-requests"] });
      queryClient.invalidateQueries({ queryKey: ["event-carpool-trips"] });
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la demande de covoiturage: ${error.message}`);
    }
  });
}

// Fonction pour récupérer les demandes de covoiturage reçues
export async function fetchReceivedCarpoolRequests(): Promise<PaginatedCarpoolRequests> {
  const resp = await fetch('/api/event/carpool-requests/?as_driver=true');
  if (!resp.ok) throw new Error('Failed to fetch received carpool requests');
  const data = await resp.json();
  return PaginatedCarpoolRequestsSchema.parse(data);
}

// Hook pour récupérer les demandes de covoiturage reçues
export function useReceivedCarpoolRequests(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["received-carpool-requests"],
    queryFn: fetchReceivedCarpoolRequests,
    enabled: options?.enabled !== undefined ? options.enabled : true,
  });
}

// Fonction pour récupérer les demandes de covoiturage envoyées
export async function fetchSentCarpoolRequests(): Promise<PaginatedCarpoolRequests> {
  const resp = await fetch('/api/event/carpool-requests/?as_passenger=true');
  if (!resp.ok) throw new Error('Failed to fetch sent carpool requests');
  const data = await resp.json();
  try {
    return PaginatedCarpoolRequestsSchema.parse(data);
  } catch (error) {
    console.error("Error parsing carpool requests", error);
    throw error;
  }
}

// Hook pour récupérer les demandes de covoiturage envoyées
export function useSentCarpoolRequests(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["sent-carpool-requests"],
    queryFn: fetchSentCarpoolRequests,
    enabled: options?.enabled !== undefined ? options.enabled : true,
  });
}

// Fonction pour mettre à jour le statut d'une demande de covoiturage
export async function updateCarpoolRequestStatus(
  requestId: number,
  status: CarpoolRequestStatus,
  responseMessage: string | null = null
): Promise<CarpoolRequest> {
  const csrfToken = getCSRFToken();

  const resp = await fetch(`/api/event/carpool-requests/${requestId}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken || '',
    },
    body: JSON.stringify({ status, response_message: responseMessage }),
    credentials: 'include',
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Une erreur est survenue' }));
    throw new Error(error.detail || "Failed to update carpool request status");
  }

  return CarpoolRequestSchema.parse(await resp.json());
}

// Hook pour mettre à jour le statut d'une demande de covoiturage
export function useUpdateCarpoolRequestStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      requestId,
      status,
      responseMessage
    }: {
      requestId: number,
      status: CarpoolRequestStatus,
      responseMessage?: string | null
    }) => updateCarpoolRequestStatus(requestId, status, responseMessage),
    onSuccess: (_, variables) => {
      const actionMap: Record<CarpoolRequestStatus, string> = {
        ACCEPTED: "acceptée",
        REJECTED: "refusée",
        CANCELLED: "annulée",
        PENDING: "mise en attente",
      };

      toast.success(`Demande ${actionMap[variables.status]} avec succès`);
      queryClient.invalidateQueries({ queryKey: ["received-carpool-requests"] });
      queryClient.invalidateQueries({ queryKey: ["sent-carpool-requests"] });
      queryClient.invalidateQueries({ queryKey: ["event-carpool-trips"] });
    },
    onError: (error: Error) => {
      toast.error(`Erreur lors de la mise à jour de la demande: ${error.message}`);
    }
  });
}
