import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Spinner } from "../ui/spinner";
import { useCreateCarpoolRequest } from "~/lib/carpool";
import { type CarpoolTrip } from "~/lib/carpool";
import { formatDate } from "./CarpoolTripCard";

interface CreateRequestFormProps {
  trip: CarpoolTrip;
  onCancel: () => void;
  onSuccess: () => void;
}

export function CreateRequestForm({ trip, onCancel, onSuccess }: CreateRequestFormProps) {
  const [carpoolRequest, setCarpoolRequest] = useState({
    tripId: trip.id,
    seatsRequested: 1,
    message: "",
  });

  const createRequestMutation = useCreateCarpoolRequest();

  const handleCreateRequest = () => {
    createRequestMutation.mutate(carpoolRequest, {
      onSuccess: () => {
        onSuccess();
      }
    });
  };

  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Réserver des places</h3>
      <p className="mb-2">
        <strong>Trajet:</strong> {trip.departure_city} → {trip.arrival_city}
      </p>
      <p className="mb-2">
        <strong>Départ:</strong> {formatDate(trip.departure_datetime)}
      </p>
      <p className="mb-2">
        <strong>Prix:</strong> {Number(trip.price_per_seat) > 0 ? `${trip.price_per_seat} € par place` : 'Gratuit'}
      </p>
      <div className="space-y-4 mt-4">
        <div>
          <Label htmlFor="seats_requested">Nombre de places*</Label>
          <Input
            id="seats_requested"
            type="number"
            min="1"
            max={trip.seats_available || trip.seats_total}
            value={carpoolRequest.seatsRequested}
            onChange={(e) => setCarpoolRequest({ ...carpoolRequest, seatsRequested: parseInt(e.target.value) })}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            {trip.seats_available || trip.seats_total} place(s) disponible(s)
          </p>
        </div>
        <div>
          <Label htmlFor="request_message">Message au conducteur (optionnel)</Label>
          <Textarea
            id="request_message"
            value={carpoolRequest.message}
            onChange={(e) => setCarpoolRequest({ ...carpoolRequest, message: e.target.value })}
            placeholder="Message à l'attention du conducteur..."
          />
        </div>
        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={onCancel}>
            Annuler
          </Button>
          <Button
            onClick={handleCreateRequest}
            disabled={createRequestMutation.isPending || carpoolRequest.seatsRequested < 1}
          >
            {createRequestMutation.isPending ? <Spinner className="mr-2" /> : null}
            Réserver
          </Button>
        </div>
      </div>
    </div>
  );
}
