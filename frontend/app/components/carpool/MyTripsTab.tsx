import { useState } from "react";
import { Button } from "../ui/button";
import { Spinner } from "../ui/spinner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { PlusCircle, Car, Calendar } from "lucide-react";
import { toast } from "sonner";
import { CreateTripForm } from "./CreateTripForm";
import { CarpoolRequestCard } from "./CarpoolRequestCard";
import {
  useEventCarpoolTrips,
  useReceivedCarpoolRequests,
  useUpdateCarpoolRequestStatus,
  type CarpoolRequest
} from "~/lib/carpool";
import { type EventType } from "~/lib/event";
import { useAuth } from "../auth/AuthContext";
import { formatDate } from "./CarpoolTripCard";
import { StatusBadge } from "../common/StatusBadge";

interface MyTripsTabProps {
  event: EventType;
}

export function MyTripsTab({ event }: MyTripsTabProps) {
  const { user } = useAuth();
  const [showNewTripForm, setShowNewTripForm] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<CarpoolRequest | null>(null);
  const [responseMessage, setResponseMessage] = useState("");

  const { data: trips, isLoading: isLoadingTrips } = useEventCarpoolTrips(event?.id);
  const { data: receivedRequests, isLoading: isLoadingReceivedRequests } = useReceivedCarpoolRequests();
  const updateRequestStatusMutation = useUpdateCarpoolRequestStatus();

  // Filtrer les demandes pour l'événement actuel
  const filteredRequests = receivedRequests?.results.filter(
    req => Number(req.trip?.event.id) === Number(event?.id)
  );

  const handleUpdateRequestStatus = (requestId: number, status: "ACCEPTED" | "REJECTED") => {
    updateRequestStatusMutation.mutate({
      requestId,
      status,
      responseMessage,
    }, {
      onSuccess: () => {
        setSelectedRequest(null);
        setResponseMessage("");
      }
    });
  };

  if (showNewTripForm) {
    return (
      <CreateTripForm
        event={event}
        onCancel={() => setShowNewTripForm(false)}
        onSuccess={() => setShowNewTripForm(false)}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Mes trajets proposés */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Mes trajets proposés</h3>
        {isLoadingTrips ? (
          <div className="flex justify-center p-4">
            <Spinner />
          </div>
        ) : !trips || trips.results.filter(t => t.driver.id === user?.user.id).length === 0 ? (
          <div className="text-center p-4 border rounded-lg">
            <p>Vous n'avez pas encore proposé de trajet pour cet événement</p>
            <Button onClick={() => setShowNewTripForm(true)} className="mt-4">
              <PlusCircle className="h-4 w-4 mr-2" />
              Proposer un trajet
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {trips.results
              .filter(trip => trip.driver.id === user?.user.id)
              .map((trip) => (
                <Card key={trip.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle>
                        {trip.departure_city} → {trip.arrival_city}
                      </CardTitle>
                      <Badge variant={trip.is_active ? "default" : "secondary"}>
                        {trip.is_active ? "Actif" : "Inactif"}
                      </Badge>
                    </div>
                    <CardDescription>
                      <Calendar className="h-3 w-3 inline mr-1" />
                      {formatDate(trip.departure_datetime)}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-2 text-sm">
                      <span>
                        <Car className="h-3 w-3 inline mr-1" />
                        {trip.seats_available ?? trip.seats_total} / {trip.seats_total} places
                      </span>
                      <span className="font-semibold">
                        {Number(trip.price_per_seat) > 0 ? `${trip.price_per_seat} € / place` : 'Gratuit'}
                      </span>
                    </div>
                    {trip.additional_info && (
                      <p className="text-sm mb-2">
                        <strong>Info:</strong> {trip.additional_info}
                      </p>
                    )}
                    <Button
                      variant="outline"
                      className="w-full mt-2"
                      onClick={() => {
                        // TODO: Implémenter la modification d'un trajet
                        toast.info("La modification de trajet n'est pas encore disponible");
                      }}
                    >
                      Modifier
                    </Button>
                  </CardContent>
                </Card>
              ))}
          </div>
        )}
      </div>

      {/* Demandes reçues */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Demandes de covoiturage reçues</h3>
        {isLoadingReceivedRequests ? (
          <div className="flex justify-center p-4">
            <Spinner />
          </div>
        ) : !filteredRequests || filteredRequests.length === 0 ? (
          <div className="text-center p-4 border rounded-lg">
            <p>Vous n'avez pas encore reçu de demande de covoiturage pour cet événement</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRequests.map((request) => (
              <Card key={request.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle>
                      {`${request.passenger.first_name} ${request.passenger.last_name}`}
                    </CardTitle>
                    <StatusBadge status={request.status} />
                  </div>
                  <CardDescription>
                    Trajet: {request.trip?.departure_city || "Départ"} → {request.trip?.arrival_city || "Arrivée"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between text-sm mb-2">
                    <span>
                      Demande pour {request.seats_requested} place(s)
                    </span>
                    <span className="font-semibold">
                      {request.trip?.price_per_seat && Number(request.trip?.price_per_seat) > 0
                        ? `${(Number(request.trip.price_per_seat) * request.seats_requested).toFixed(2)} €`
                        : 'Gratuit'}
                    </span>
                  </div>
                  {request.message && (
                    <div className="mb-3">
                      <strong>Message du passager :</strong>
                      <p className="text-sm">{request.message}</p>
                    </div>
                  )}
                  {request.status === "PENDING" ? (
                    <div className="space-y-4 mt-4">
                      <div>
                        <Label htmlFor="response_message">Message de réponse (optionnel)</Label>
                        <Textarea
                          id="response_message"
                          value={selectedRequest?.id === request.id ? responseMessage : ""}
                          onChange={(e) => {
                            setSelectedRequest(request as CarpoolRequest);
                            setResponseMessage(e.target.value);
                          }}
                          placeholder="Message à l'attention du passager..."
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          className="text-red-500 border-red-200 hover:bg-red-50"
                          onClick={() => handleUpdateRequestStatus(request.id, "REJECTED")}
                          disabled={updateRequestStatusMutation.isPending}
                        >
                          Refuser
                        </Button>
                        <Button
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => handleUpdateRequestStatus(request.id, "ACCEPTED")}
                          disabled={updateRequestStatusMutation.isPending}
                        >
                          {updateRequestStatusMutation.isPending ? <Spinner className="mr-2" /> : null}
                          Accepter
                        </Button>
                      </div>
                    </div>
                  ) : (
                    request.response_message && (
                      <div>
                        <strong>Votre réponse:</strong>
                        <p className="text-sm">{request.response_message}</p>
                      </div>
                    )
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
