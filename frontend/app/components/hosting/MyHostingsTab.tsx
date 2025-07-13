import { useState } from "react";
import { Button } from "../ui/button";
import { Spinner } from "../ui/spinner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { PlusCircle, BedDouble, MapPin, User } from "lucide-react";
import { toast } from "sonner";
import { StatusBadge } from "../common/StatusBadge";
import { CreateHostingForm } from "./CreateHostingForm";
import {
  useEventHostings,
  useReceivedHostingRequests,
  useUpdateHostingRequestStatus,
  type EventHostingRequest
} from "~/lib/eventHosting";
import { type EventType } from "~/lib/event";
import { useAuth } from "../auth/AuthContext";

interface MyHostingsTabProps {
  event: EventType;
}

export function MyHostingsTab({ event }: MyHostingsTabProps) {
  const { user } = useAuth();
  const [showNewHostingForm, setShowNewHostingForm] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<EventHostingRequest | null>(null);
  const [responseMessage, setResponseMessage] = useState("");

  const { data: hostings, isLoading: isLoadingHostings } = useEventHostings(event?.id);
  const { data: receivedRequests, isLoading: isLoadingReceivedRequests } = useReceivedHostingRequests();
  const updateRequestStatusMutation = useUpdateHostingRequestStatus();

  // Filtrer les demandes pour l'événement actuel
  const filteredRequests = receivedRequests?.results.filter(
    req => Number(req.hosting_details?.event) === Number(event?.id)
  );

  const handleUpdateRequestStatus = (requestId: number, status: "ACCEPTED" | "REJECTED") => {
    updateRequestStatusMutation.mutate({
      requestId,
      status,
      hostMessage: responseMessage,
    }, {
      onSuccess: () => {
        setSelectedRequest(null);
        setResponseMessage("");
      }
    });
  };

  if (showNewHostingForm) {
    return (
      <CreateHostingForm
        event={event}
        onCancel={() => setShowNewHostingForm(false)}
        onSuccess={() => setShowNewHostingForm(false)}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Mes hébergements proposés */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Mes propositions d'hébergement</h3>
        {isLoadingHostings ? (
          <div className="flex justify-center p-4">
            <Spinner />
          </div>
        ) : !hostings || hostings.results.filter(h => h.host?.id === user?.user.id).length === 0 ? (
          <div className="text-center p-4 border rounded-lg">
            <p>Vous n'avez pas encore proposé d'hébergement pour cet événement</p>
            <Button onClick={() => setShowNewHostingForm(true)} className="mt-4">
              <PlusCircle className="h-4 w-4 mr-2" />
              Proposer un hébergement
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {hostings.results
              .filter(hosting => hosting.host?.id === user?.user.id)
              .map((hosting) => (
                <Card key={hosting.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle>
                        <BedDouble className="h-4 w-4 inline mr-1" />
                        {hosting.available_beds} lit(s)
                      </CardTitle>
                      <Badge variant={hosting.is_active ? "default" : "secondary"}>
                        {hosting.is_active ? "Actif" : "Inactif"}
                      </Badge>
                    </div>
                    <CardDescription>
                      <MapPin className="h-3 w-3 inline mr-1" />
                      {hosting.city_override || "Ville non précisée"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {hosting.custom_rules && (
                      <p className="text-sm mb-2">
                        <strong>Règles:</strong> {hosting.custom_rules}
                      </p>
                    )}
                    <Button
                      variant="outline"
                      className="w-full mt-2"
                      onClick={() => {
                        // TODO: Implémenter la modification d'un hébergement
                        toast.info("La modification d'hébergement n'est pas encore disponible");
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
        <h3 className="text-lg font-semibold mb-4">Demandes d'hébergement reçues</h3>
        {isLoadingReceivedRequests ? (
          <div className="flex justify-center p-4">
            <Spinner />
          </div>
        ) : !filteredRequests || filteredRequests.length === 0 ? (
          <div className="text-center p-4 border rounded-lg">
            <p>Vous n'avez pas encore reçu de demande d'hébergement pour cet événement</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRequests.map((request) => (
              <Card key={request.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle>
                      <User className="h-4 w-4 inline mr-1" />
                      {request.requester_name || `Demandeur #${request.requester}`}
                    </CardTitle>
                    <StatusBadge status={request.status} />
                  </div>
                  <CardDescription>
                    Demande reçue le {new Date(request.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {request.message && (
                    <div className="mb-3">
                      <strong>Message:</strong>
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
                            setSelectedRequest(request);
                            setResponseMessage(e.target.value);
                          }}
                          placeholder="Message à l'attention du demandeur..."
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
                    request.host_message && (
                      <div>
                        <strong>Votre réponse:</strong>
                        <p className="text-sm">{request.host_message}</p>
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
