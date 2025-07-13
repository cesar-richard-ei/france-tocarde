import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Calendar, Check, HelpCircle, MapPin, X, Car, BedDouble } from "lucide-react";
import { useAuth } from "./auth/AuthContext";
import { EventSubscriptionDialog } from "./EventSubscriptionDialog";
import { EventHostingDialog } from "./EventHostingDialog";
import { CarpoolDialog } from "./CarpoolDialog";
import { useUserSubscriptions, getUserSubscriptionForEvent } from "~/lib/eventSubscription";
import type { EventType, SubscriptionStats } from "~/lib/event";

interface EventDetailDialogProps {
  event: EventType | null;
  isOpen: boolean;
  onClose: () => void;
}

export function EventDetailDialog({ event, isOpen, onClose }: EventDetailDialogProps) {
  const { isAuthenticated } = useAuth();
  const { data: userSubscriptions } = useUserSubscriptions();
  const [showSubscriptionDialog, setShowSubscriptionDialog] = useState(false);
  const [showCarpoolDialog, setShowCarpoolDialog] = useState(false);
  const [showHostingDialog, setShowHostingDialog] = useState(false);
  const [eventSubscription, setEventSubscription] = useState<any>(undefined);

  useEffect(() => {
    if (userSubscriptions?.results && event) {
      const sub = getUserSubscriptionForEvent(userSubscriptions.results, event.id);
      setEventSubscription(sub);
    }
  }, [userSubscriptions, event]);

  if (!event) return null;

  const subscriptionStats: SubscriptionStats = typeof event.subscriptions_count === "number"
    ? { YES: event.subscriptions_count, NO: 0, MAYBE: 0 }
    : event.subscriptions_count || { YES: 0, NO: 0, MAYBE: 0 };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{event.name}</DialogTitle>
        </DialogHeader>
        <div className="md:flex md:gap-6 overflow-y-auto flex-1">
          <div className="md:w-1/3 space-y-4">
            <div className="flex items-center text-sm text-royal-blue-700">
              <Calendar className="h-4 w-4 mr-1" />
              {new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(event.start_date))}
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <MapPin className="h-4 w-4 mr-1" />
              {event.location}
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-center">
              <div className="flex items-center justify-center gap-1">
                <Check className="h-3 w-3 text-green-600" />
                <span className="whitespace-nowrap">{subscriptionStats.YES} participant{subscriptionStats.YES > 1 ? 's' : ''}</span>
              </div>
              <div className="flex items-center justify-center gap-1">
                <HelpCircle className="h-3 w-3 text-amber-600" />
                <span className="whitespace-nowrap">{subscriptionStats.MAYBE} peut-être</span>
              </div>
              <div className="flex items-center justify-center gap-1">
                <X className="h-3 w-3 text-red-600" />
                <span className="whitespace-nowrap">{subscriptionStats.NO} non</span>
              </div>
            </div>
            <div className="space-y-2">
              <Button
                size="sm"
                className="w-full bg-royal-blue-600 hover:bg-royal-blue-700"
                onClick={() => setShowSubscriptionDialog(true)}
              >
                {isAuthenticated ? "S'inscrire" : "Se connecter pour s'inscrire"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setShowCarpoolDialog(true)}
              >
                <Car className="h-4 w-4 mr-1" /> Covoiturage
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setShowHostingDialog(true)}
              >
                <BedDouble className="h-4 w-4 mr-1" /> Hébergements
              </Button>
            </div>
          </div>
          <div className="md:w-2/3 space-y-4 mt-4 md:mt-0 prose">
            {event.description ? <ReactMarkdown>{event.description}</ReactMarkdown> : null}
            {event.prices ? <ReactMarkdown>{event.prices}</ReactMarkdown> : null}
          </div>
        </div>
        <EventSubscriptionDialog
          event={event}
          isOpen={showSubscriptionDialog}
          onClose={() => setShowSubscriptionDialog(false)}
          existingSubscription={eventSubscription}
        />
        <CarpoolDialog
          event={event}
          isOpen={showCarpoolDialog}
          onClose={() => setShowCarpoolDialog(false)}
        />
        <EventHostingDialog
          event={event}
          isOpen={showHostingDialog}
          onClose={() => setShowHostingDialog(false)}
        />
      </DialogContent>
    </Dialog>
  );
}
