import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Spinner } from "../ui/spinner";
import { useCreateCarpoolTrip } from "~/lib/carpool";
import { type EventType } from "~/lib/event";

interface CreateTripFormProps {
  event: EventType;
  onCancel: () => void;
  onSuccess: () => void;
}

export function CreateTripForm({ event, onCancel, onSuccess }: CreateTripFormProps) {
  const [newTrip, setNewTrip] = useState({
    event: event.id,
    departure_city: "",
    departure_address: "",
    arrival_city: "",
    arrival_address: "",
    departure_datetime: "",
    return_datetime: "",
    has_return: false,
    seats_total: 3,
    price_per_seat: 0,
    additional_info: "",
    is_active: true,
  });

  const createTripMutation = useCreateCarpoolTrip();

  const formatDateToISO = (dateString: string): string => {
    if (!dateString) return "";
    return new Date(dateString).toISOString();
  };

  const handleCreateTrip = () => {
    // Convertir les dates en format ISO 8601
    const formattedDepartureDate = formatDateToISO(newTrip.departure_datetime);
    const formattedReturnDate = newTrip.has_return && newTrip.return_datetime
      ? formatDateToISO(newTrip.return_datetime)
      : null;

    const tripData = {
      ...newTrip,
      event: Number(event.id),
      seats_total: Number(newTrip.seats_total),
      price_per_seat: Number(newTrip.price_per_seat),
      departure_datetime: formattedDepartureDate,
      return_datetime: formattedReturnDate,
    };

    createTripMutation.mutate(tripData, {
      onSuccess: () => {
        onSuccess();
      },
      onError: (error) => {
        console.error("Erreur lors de la création du trajet:", error);
      }
    });
  };

  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Proposer un trajet</h3>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="departure_city">Ville de départ*</Label>
            <Input
              id="departure_city"
              value={newTrip.departure_city}
              onChange={(e) => setNewTrip({ ...newTrip, departure_city: e.target.value })}
              placeholder="Paris"
              required
            />
          </div>
          <div>
            <Label htmlFor="arrival_city">Ville d'arrivée*</Label>
            <Input
              id="arrival_city"
              value={newTrip.arrival_city}
              onChange={(e) => setNewTrip({ ...newTrip, arrival_city: e.target.value })}
              placeholder="Lyon"
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="departure_address">Adresse de départ (optionnel)</Label>
            <Input
              id="departure_address"
              value={newTrip.departure_address}
              onChange={(e) => setNewTrip({ ...newTrip, departure_address: e.target.value })}
              placeholder="5 rue de Paris"
            />
          </div>
          <div>
            <Label htmlFor="arrival_address">Adresse d'arrivée (optionnel)</Label>
            <Input
              id="arrival_address"
              value={newTrip.arrival_address}
              onChange={(e) => setNewTrip({ ...newTrip, arrival_address: e.target.value })}
              placeholder="10 rue de Lyon"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="departure_datetime">Date et heure de départ*</Label>
            <Input
              id="departure_datetime"
              type="datetime-local"
              value={newTrip.departure_datetime}
              onChange={(e) => setNewTrip({ ...newTrip, departure_datetime: e.target.value })}
              required
            />
          </div>
          <div className="flex items-end space-x-2">
            <div className="flex-1">
              <Label htmlFor="seats_total">Nombre de places*</Label>
              <Input
                id="seats_total"
                type="number"
                min="1"
                value={newTrip.seats_total}
                onChange={(e) => setNewTrip({ ...newTrip, seats_total: parseInt(e.target.value) })}
                required
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="price_per_seat">Prix par place (€)</Label>
              <Input
                id="price_per_seat"
                type="number"
                min="0"
                step="0.01"
                value={newTrip.price_per_seat}
                onChange={(e) => setNewTrip({ ...newTrip, price_per_seat: parseFloat(e.target.value) })}
              />
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Input
            id="has_return"
            type="checkbox"
            className="w-4 h-4"
            checked={newTrip.has_return}
            onChange={(e) => setNewTrip({ ...newTrip, has_return: e.target.checked })}
          />
          <Label htmlFor="has_return">Proposer un trajet retour</Label>
        </div>
        {newTrip.has_return && (
          <div>
            <Label htmlFor="return_datetime">Date et heure de retour*</Label>
            <Input
              id="return_datetime"
              type="datetime-local"
              value={newTrip.return_datetime}
              onChange={(e) => setNewTrip({ ...newTrip, return_datetime: e.target.value })}
              required
            />
          </div>
        )}
        <div>
          <Label htmlFor="additional_info">Informations supplémentaires (optionnel)</Label>
          <Textarea
            id="additional_info"
            value={newTrip.additional_info}
            onChange={(e) => setNewTrip({ ...newTrip, additional_info: e.target.value })}
            placeholder="Informations supplémentaires sur le trajet..."
          />
        </div>
        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={onCancel}>Annuler</Button>
          <Button
            onClick={handleCreateTrip}
            disabled={
              createTripMutation.isPending ||
              !newTrip.departure_city ||
              !newTrip.arrival_city ||
              !newTrip.departure_datetime ||
              (newTrip.has_return && !newTrip.return_datetime)
            }
          >
            {createTripMutation.isPending ? <Spinner className="mr-2" /> : null}
            Proposer le trajet
          </Button>
        </div>
      </div>
    </div>
  );
}
