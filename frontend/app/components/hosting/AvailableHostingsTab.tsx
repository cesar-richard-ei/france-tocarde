import { useState } from "react";
import { Button } from "../ui/button";
import { Spinner } from "../ui/spinner";
import { PlusCircle } from "lucide-react";
import { HostingCard } from "./HostingCard";
import { CreateHostingForm } from "./CreateHostingForm";
import { CreateHostingRequestForm } from "./CreateHostingRequestForm";
import { useEventHostings, useSentHostingRequests, type EventHosting } from "~/lib/eventHosting";
import { type EventType } from "~/lib/event";

interface AvailableHostingsTabProps {
  event: EventType;
  acceptedRequestHostingIds?: number[];
}

export function AvailableHostingsTab({ event, acceptedRequestHostingIds = [] }: AvailableHostingsTabProps) {
  const [showNewHostingForm, setShowNewHostingForm] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [selectedHosting, setSelectedHosting] = useState<EventHosting | null>(null);

  const { data: hostings, isLoading: isLoadingHostings } = useEventHostings(event?.id);
  const { data: sentRequests } = useSentHostingRequests();

  // Filtrer les IDs d'hébergement pour lesquels l'utilisateur a une demande en cours
  // (tous les statuts sauf CANCELLED et REJECTED)
  const sentRequestIds = sentRequests?.results
    .filter(req => !["CANCELLED", "REJECTED"].includes(req.status))
    .map(req => Number(req.hosting.id)) || [];

  // Vérifier si l'utilisateur a déjà une demande acceptée pour l'événement
  const hasAcceptedRequestForEvent = sentRequests?.results
    .some(req =>
      req.status === "ACCEPTED" &&
      Number(req.hosting?.event) === Number(event?.id)
    ) || false;

  const handleHostingClick = (hosting: EventHosting) => {
    // Si l'utilisateur a déjà une demande acceptée pour cet événement, ne pas permettre de nouvelles demandes
    if (hasAcceptedRequestForEvent && !acceptedRequestHostingIds.includes(hosting.id)) {
      return;
    }

    // Si l'utilisateur a déjà une demande en cours pour cet hébergement, ne pas permettre une nouvelle demande
    if (sentRequestIds.includes(hosting.id)) {
      return;
    }

    setSelectedHosting(hosting);
    setShowRequestForm(true);
  };

  const handleRequestSuccess = () => {
    setShowRequestForm(false);
    setSelectedHosting(null);
  };

  const handleHostingSuccess = () => {
    setShowNewHostingForm(false);
  };

  if (isLoadingHostings) {
    return (
      <div className="flex justify-center p-8">
        <Spinner />
      </div>
    );
  }

  if (showNewHostingForm) {
    return (
      <CreateHostingForm
        event={event}
        onCancel={() => setShowNewHostingForm(false)}
        onSuccess={handleHostingSuccess}
      />
    );
  }

  if (showRequestForm && selectedHosting) {
    return (
      <CreateHostingRequestForm
        hosting={selectedHosting}
        onCancel={() => {
          setShowRequestForm(false);
          setSelectedHosting(null);
        }}
        onSuccess={handleRequestSuccess}
      />
    );
  }

  if (!hostings || hostings.results.length === 0) {
    return (
      <div className="text-center p-6">
        <p>Aucun hébergement disponible pour le moment</p>
        <Button onClick={() => setShowNewHostingForm(true)} className="mt-4">
          <PlusCircle className="h-4 w-4 mr-2" />
          Proposer un hébergement
        </Button>
      </div>
    );
  }

  // Filtrer les hébergements pour l'événement actuel
  const filteredHostings = hostings.results.filter(hosting => {
    const hostingEventId = Number(hosting.event);
    const currentEventId = Number(event.id);
    return hostingEventId === currentEventId;
  });

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {filteredHostings.map((hosting) => (
          <HostingCard
            key={hosting.id}
            hosting={hosting}
            onRequestClick={handleHostingClick}
            sentRequestIds={sentRequestIds}
            hasAcceptedRequestForEvent={hasAcceptedRequestForEvent}
            isAcceptedHosting={acceptedRequestHostingIds.includes(hosting.id)}
          />
        ))}
      </div>
      <div className="flex justify-center">
        <Button onClick={() => setShowNewHostingForm(true)}>
          <PlusCircle className="h-4 w-4 mr-2" />
          Proposer un hébergement
        </Button>
      </div>
    </div>
  );
}
