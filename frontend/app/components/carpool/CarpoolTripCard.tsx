import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Car, Calendar, User } from "lucide-react";
import { type CarpoolTrip } from "~/lib/carpool";
import { toast } from "sonner";
import { useAuth } from "../auth/AuthContext";

interface CarpoolTripCardProps {
  trip: CarpoolTrip;
  onRequestClick: (trip: CarpoolTrip) => void;
  sentRequestIds?: number[];
}

export function formatDate(dateString: string) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(date);
}

export function CarpoolTripCard({ trip, onRequestClick, sentRequestIds = [] }: CarpoolTripCardProps) {
  const { user } = useAuth();
  const isUserDriver = trip.driver.id === user?.user.id;
  const hasUserRequested = sentRequestIds.includes(trip.id);

  const handleClick = () => {
    if (trip.is_full) {
      toast.error("Ce trajet est complet");
      return;
    }
    onRequestClick(trip);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle>
            {trip.departure_city} → {trip.arrival_city}
          </CardTitle>
          <Badge variant={trip.is_full ? "secondary" : "outline"}>
            <Car className="h-3 w-3 mr-1" />
            {trip.seats_available ?? trip.seats_total} place(s)
          </Badge>
        </div>
        <CardDescription>
          <Calendar className="h-3 w-3 inline mr-1" />
          {formatDate(trip.departure_datetime)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center mb-2 text-sm">
          <User className="h-3 w-3 mr-1" />
          <span>{`${trip.driver.first_name} ${trip.driver.last_name}`}</span>
          <span className="ml-auto font-semibold">
            {Number(trip.price_per_seat) > 0 ? `${trip.price_per_seat} € / place` : 'Gratuit'}
          </span>
        </div>
        {trip.additional_info && (
          <p className="text-sm my-2">
            <strong>Info:</strong> {trip.additional_info}
          </p>
        )}
        <Button
          className="w-full mt-2"
          variant={
            trip.is_full || isUserDriver || hasUserRequested
              ? "outline"
              : "default"
          }
          onClick={handleClick}
          disabled={trip.is_full || isUserDriver || hasUserRequested}
        >
          {trip.is_full
            ? "Trajet complet"
            : isUserDriver
              ? "C'est votre trajet"
              : hasUserRequested
                ? "Déjà réservé"
                : "Réserver"}
        </Button>
      </CardContent>
    </Card>
  );
}
