import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Calendar, User } from "lucide-react";
import { StatusBadge } from "../common/StatusBadge";
import { type CarpoolRequest } from "~/lib/carpool";
import { formatDate } from "./CarpoolTripCard";

interface CarpoolRequestCardProps {
  request: CarpoolRequest;
  isSent?: boolean;
  onCancelRequest?: (requestId: number) => void;
}

export function CarpoolRequestCard({ request, isSent = true, onCancelRequest }: CarpoolRequestCardProps) {
  const tripObject = typeof request.trip === 'object' ? request.trip : null;

  // Déterminer le nom à afficher selon si c'est une demande envoyée ou reçue
  const displayName = isSent
    ? (`Conducteur ${tripObject?.driver?.first_name || "?"} ${tripObject?.driver?.last_name || "?"}`)
    : `Passager ${request.passenger?.first_name || "?"} ${request.passenger?.last_name || "?"}`;

  // Déterminer le message selon si c'est une demande envoyée ou reçue
  const messageLabel = isSent ? "Votre message:" : "Message:";
  const responseLabel = isSent ? "Réponse du conducteur:" : "Votre réponse:";

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>
            {isSent
              ? `${tripObject?.departure_city || "Départ"} → ${tripObject?.arrival_city || "Arrivée"}`
              : <><User className="h-4 w-4 inline mr-1" />{displayName}</>
            }
          </CardTitle>
          <StatusBadge status={request.status} />
        </div>
        <CardDescription>
          {isSent
            ? <><User className="h-3 w-3 inline mr-1" />{displayName}</>
            : `Trajet: ${tripObject?.departure_city || "Départ"} → ${tripObject?.arrival_city || "Arrivée"}`
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between text-sm mb-2">
          <span>
            <Calendar className="h-3 w-3 inline mr-1" />
            {tripObject?.departure_datetime ? formatDate(tripObject.departure_datetime) : "Date non précisée"}
          </span>
          <span className="font-semibold">
            {request.seats_requested} place(s) {tripObject?.price_per_seat && Number(tripObject.price_per_seat) > 0
              ? `× ${tripObject.price_per_seat} € = ${(Number(tripObject.price_per_seat) * request.seats_requested).toFixed(2)} €`
              : ''}
          </span>
        </div>
        {request.message && (
          <div className="mb-3">
            <strong>{messageLabel}</strong>
            <p className="text-sm">{request.message}</p>
          </div>
        )}
        {request.response_message && (
          <div className="mb-3">
            <strong>{responseLabel}</strong>
            <p className="text-sm">{request.response_message}</p>
          </div>
        )}
        {request.status === "ACCEPTED" && isSent && (
          <div className="bg-green-50 p-2 rounded text-sm mt-2">
            <p><strong>Réservation confirmée !</strong> Vous pouvez contacter le conducteur.</p>
            {tripObject?.price_per_seat && Number(tripObject.price_per_seat) > 0 && (
              <p className="mt-1">
                <strong>À payer:</strong> {(Number(tripObject.price_per_seat) * request.seats_requested).toFixed(2)} €
              </p>
            )}
          </div>
        )}
        {request.status === "PENDING" && isSent && onCancelRequest && (
          <Button
            variant="outline"
            color="destructive"
            className="mt-2"
            onClick={() => onCancelRequest(request.id)}
          >
            Annuler ma réservation
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
