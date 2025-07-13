import { useState } from "react";
import { Button } from "../ui/button";
import { Spinner } from "../ui/spinner";
import { PlusCircle } from "lucide-react";
import { CarpoolTripCard } from "./CarpoolTripCard";
import { CreateTripForm } from "./CreateTripForm";
import { CreateRequestForm } from "./CreateRequestForm";
import { useEventCarpoolTrips, type CarpoolTrip } from "~/lib/carpool";
import { type EventType } from "~/lib/event";

interface AvailableTripsTabProps {
  event: EventType;
  sentRequestTripIds: number[];
}

export function AvailableTripsTab({ event, sentRequestTripIds }: AvailableTripsTabProps) {
  const [showNewTripForm, setShowNewTripForm] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<CarpoolTrip | null>(null);

  const { data: trips, isLoading: isLoadingTrips } = useEventCarpoolTrips(event?.id);

  const handleTripClick = (trip: CarpoolTrip) => {
    setSelectedTrip(trip);
    setShowRequestForm(true);
  };

  const handleRequestSuccess = () => {
    setShowRequestForm(false);
    setSelectedTrip(null);
  };

  const handleTripSuccess = () => {
    setShowNewTripForm(false);
  };

  if (isLoadingTrips) {
    return (
      <div className="flex justify-center p-8">
        <Spinner />
      </div>
    );
  }

  if (showNewTripForm) {
    return (
      <CreateTripForm
        event={event}
        onCancel={() => setShowNewTripForm(false)}
        onSuccess={handleTripSuccess}
      />
    );
  }

  if (showRequestForm && selectedTrip) {
    return (
      <CreateRequestForm
        trip={selectedTrip}
        onCancel={() => {
          setShowRequestForm(false);
          setSelectedTrip(null);
        }}
        onSuccess={handleRequestSuccess}
      />
    );
  }

  if (!trips || trips.results.length === 0) {
    return (
      <div className="text-center p-6">
        <p>Aucun trajet disponible pour le moment</p>
        <Button onClick={() => setShowNewTripForm(true)} className="mt-4">
          <PlusCircle className="h-4 w-4 mr-2" />
          Proposer un trajet
        </Button>
      </div>
    );
  }

  // Filtrer les trajets pour l'événement actuel et actifs
  const filteredTrips = trips.results.filter(trip => {
    const tripEventId = Number(trip.event.id);
    const currentEventId = Number(event.id);
    return trip.is_active && tripEventId === currentEventId;
  });

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {filteredTrips.map((trip) => (
          <CarpoolTripCard
            key={trip.id}
            trip={trip}
            onRequestClick={handleTripClick}
            sentRequestIds={sentRequestTripIds}
          />
        ))}
      </div>
      <div className="flex justify-center">
        <Button onClick={() => setShowNewTripForm(true)}>
          <PlusCircle className="h-4 w-4 mr-2" />
          Proposer un trajet
        </Button>
      </div>
    </div>
  );
}
