import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { MapPin, User, BedDouble } from "lucide-react";
import { type EventHosting } from "~/lib/eventHosting";
import { useAuth } from "../auth/AuthContext";
import { toast } from "sonner";

interface HostingCardProps {
  hosting: EventHosting;
  onRequestClick: (hosting: EventHosting) => void;
  sentRequestIds?: number[];
  hasAcceptedRequestForEvent?: boolean;
  isAcceptedHosting?: boolean;
}

export function HostingCard({
  hosting,
  onRequestClick,
  sentRequestIds = [],
  hasAcceptedRequestForEvent = false,
  isAcceptedHosting = false
}: HostingCardProps) {
  const { user } = useAuth();
  const isUserHost = hosting.host.id === user?.user.id;
  const hasUserRequested = sentRequestIds.includes(hosting.id);
  const isFull = hosting.available_beds_remaining === 0;

  const handleClick = () => {
    if (isFull) {
      toast.error("Cet hébergement n'a plus de place disponible");
      return;
    }

    if (hasAcceptedRequestForEvent && !isAcceptedHosting) {
      toast.error("Vous avez déjà une demande acceptée pour cet événement");
      return;
    }

    onRequestClick(hosting);
  };

  // Déterminer si le bouton doit être désactivé
  const isButtonDisabled = isFull ||
    isUserHost ||
    hasUserRequested ||
    (hasAcceptedRequestForEvent && !isAcceptedHosting);

  // Déterminer le texte du bouton
  const getButtonText = () => {
    if (isFull) return "Plus de place disponible";
    if (isUserHost) return "C'est votre hébergement";
    if (hasUserRequested) return "Demande déjà envoyée";
    if (hasAcceptedRequestForEvent && !isAcceptedHosting) return "Déjà hébergé ailleurs";
    if (isAcceptedHosting) return "Votre hébergement actuel";
    return "Demander à être hébergé";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle>
            <User className="h-4 w-4 inline mr-1" />
            {`${hosting.host.first_name || ""} ${hosting.host.last_name || ""}`}
          </CardTitle>
          <Badge variant={isFull ? "secondary" : "outline"}>
            <BedDouble className="h-3 w-3 mr-1" />
            {hosting.available_beds_remaining ?? hosting.available_beds} lit(s)
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
          className="w-full mt-2"
          variant={isButtonDisabled ? "outline" : "default"}
          onClick={handleClick}
          disabled={isButtonDisabled}
        >
          {getButtonText()}
        </Button>
      </CardContent>
    </Card>
  );
}
