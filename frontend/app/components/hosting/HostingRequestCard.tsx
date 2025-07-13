import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { User, MapPin, Calendar } from "lucide-react";
import { StatusBadge } from "../common/StatusBadge";
import { type EventHostingRequest } from "~/lib/eventHosting";

interface HostingRequestCardProps {
  request: EventHostingRequest;
  isSent?: boolean;
  onCancelRequest?: (requestId: number) => void;
}

export function HostingRequestCard({ request, isSent = true, onCancelRequest }: HostingRequestCardProps) {
  const hostingDetails = request.hosting_details;
  const requesterObject = typeof request.requester === 'object' ? request.requester : null;

  // Déterminer le nom à afficher selon si c'est une demande envoyée ou reçue
  const displayName = isSent
    ? `Hôte ${hostingDetails?.host?.first_name || "?"} ${hostingDetails?.host?.last_name || "?"}`
    : `Demandeur ${requesterObject?.first_name || request.requester_name || "?"}`;

  // Déterminer le message selon si c'est une demande envoyée ou reçue
  const messageLabel = isSent ? "Votre message:" : "Message:";
  const responseLabel = isSent ? "Réponse de l'hôte:" : "Votre réponse:";

  // Formater la date de création
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("fr-FR", {
      dateStyle: "short",
      timeStyle: "short"
    }).format(date);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>
            {isSent
              ? <><User className="h-4 w-4 inline mr-1" />{displayName}</>
              : <><User className="h-4 w-4 inline mr-1" />{displayName}</>
            }
          </CardTitle>
          <StatusBadge status={request.status} />
        </div>
        <CardDescription>
          {isSent && hostingDetails && (
            <><MapPin className="h-3 w-3 inline mr-1" />{hostingDetails.city_override || "Ville non précisée"}</>
          )}
          {!isSent && (
            <>Demande reçue le {formatDate(request.created_at)}</>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between text-sm mb-2">
          <span>
            <Calendar className="h-3 w-3 inline mr-1" />
            Demande {isSent ? "envoyée" : "reçue"} le {formatDate(request.created_at)}
          </span>
          {hostingDetails?.available_beds_remaining !== undefined && (
            <span className="font-semibold">
              {hostingDetails.available_beds_remaining} lit(s) disponible(s)
            </span>
          )}
        </div>
        {request.message && (
          <div className="mb-3">
            <strong>{messageLabel}</strong>
            <p className="text-sm">{request.message}</p>
          </div>
        )}
        {request.host_message && (
          <div className="mb-3">
            <strong>{responseLabel}</strong>
            <p className="text-sm">{request.host_message}</p>
          </div>
        )}
        {request.status === "ACCEPTED" && isSent && (
          <div className="bg-green-50 p-2 rounded text-sm mt-2">
            <p><strong>Demande acceptée !</strong> Vous pouvez contacter votre hôte.</p>
          </div>
        )}
        {request.status === "PENDING" && isSent && onCancelRequest && (
          <Button
            variant="outline"
            color="destructive"
            className="mt-2"
            onClick={() => onCancelRequest(request.id)}
          >
            Annuler ma demande
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
