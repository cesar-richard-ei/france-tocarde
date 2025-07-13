import { z } from "zod";
import { getCSRFToken } from "./django";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "~/components/auth/AuthContext";

export const AnswerEnum = z.enum(["YES", "NO", "MAYBE"]);

export const EventSubscriptionSchema = z.object({
  id: z.number(),
  answer: AnswerEnum,
  can_invite: z.boolean(),
  event: z.number(),
  user: z.number(),
  is_active: z.boolean(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type EventSubscription = z.infer<typeof EventSubscriptionSchema>;

export const PaginatedEventSubscriptionsSchema = z.object({
  count: z.number(),
  next: z.string().nullable(),
  previous: z.string().nullable(),
  results: z.array(EventSubscriptionSchema),
});

export type PaginatedEventSubscriptions = z.infer<typeof PaginatedEventSubscriptionsSchema>;

export type CreateSubscriptionData = {
  answer?: z.infer<typeof AnswerEnum>;
  can_invite?: boolean;
};

export type SubscriptionParams = {
  eventId: number;
  data: CreateSubscriptionData;
};

export async function createSubscription(
  eventId: number,
  data: CreateSubscriptionData = { answer: 'YES', can_invite: false }
): Promise<EventSubscription> {
  const csrfToken = getCSRFToken();

  try {
    const resp = await fetch(`/api/event/events/${eventId}/subscribe/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken || '',
      },
      body: JSON.stringify(data),
      credentials: 'include', // Pour inclure les cookies dans la requête
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(`Failed to create subscription: ${resp.status} ${errorText}`);
    }

    const json = await resp.json();
    return EventSubscriptionSchema.parse(json);
  } catch (error) {
    throw error;
  }
}

export async function fetchUserSubscriptions(): Promise<PaginatedEventSubscriptions> {
  try {
    const resp = await fetch(`/api/event/event-subscriptions/`, {
      credentials: 'include',
    });

    if (!resp.ok) {
      throw new Error(`Failed to fetch subscriptions: ${resp.status}`);
    }

    const data = await resp.json();
    return PaginatedEventSubscriptionsSchema.parse(data);
  } catch (error) {
    console.error("Error fetching user subscriptions:", error);
    throw error;
  }
}

export function useUserSubscriptions() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ["user-subscriptions"],
    queryFn: fetchUserSubscriptions,
    enabled: isAuthenticated, // Ne pas essayer de récupérer si l'utilisateur n'est pas connecté
    staleTime: 1000 * 60 * 5, // Considérer les données fraîches pendant 5 minutes
    retry: 1, // Réessayer une seule fois en cas d'échec
  });
}

export function getUserSubscriptionForEvent(subscriptions: EventSubscription[], eventId: number): EventSubscription | undefined {
  const subscription = subscriptions.find(sub => sub.event === eventId);
  return subscription;
}

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useCreateSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ eventId, data }: SubscriptionParams) => createSubscription(eventId, data),
    onSuccess: () => {
      toast.success("Inscription enregistrée");
      // Invalider les queries d'événements pour forcer un rafraîchissement
      queryClient.invalidateQueries({ queryKey: ['events'] });
      queryClient.invalidateQueries({ queryKey: ['user-subscriptions'] });

      // Rafraîchir la page pour éviter les problèmes de port déconnecté
      setTimeout(() => {
        window.location.reload();
      }, 1000); // Attendre 1 seconde pour que l'utilisateur puisse voir le toast
    },
    onError: (error) => {
      toast.error(`Erreur lors de l'inscription: ${error.message || 'Erreur inconnue'}`);
    },
  });
}
