import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { Button } from "../ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { useAuth } from "../auth/AuthContext";
import { useSentCarpoolRequests } from "~/lib/carpool";
import { type EventType } from "~/lib/event";
import { AvailableTripsTab } from "./AvailableTripsTab";
import { MyRequestsTab } from "./MyRequestsTab";
import { MyTripsTab } from "./MyTripsTab";

interface CarpoolDialogProps {
  event: EventType | null;
  isOpen: boolean;
  onClose: () => void;
}

export function CarpoolDialog({ event, isOpen, onClose }: CarpoolDialogProps) {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState("available");
  const { data: sentRequests } = useSentCarpoolRequests({ enabled: isAuthenticated });

  // Extraire les ID des trajets pour lesquels l'utilisateur a déjà envoyé une demande
  const sentRequestTripIds = (sentRequests?.results || [])
    .filter(req => ["PENDING", "ACCEPTED"].includes(req.status))
    .map(req => {
      // req.trip peut être un objet ou un ID selon le contexte
      return typeof req.trip === 'object' && req.trip !== null ? (req.trip as any).id : req.trip;
    });

  if (!event) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Covoiturages pour {event.name}</DialogTitle>
        </DialogHeader>

        {!isAuthenticated ? (
          <div className="text-center p-4">
            <p className="mb-4">Vous devez être connecté pour accéder aux covoiturages</p>
            <Button onClick={onClose}>Se connecter</Button>
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full overflow-y-auto flex-1">
            <TabsList className="grid grid-cols-3">
              <TabsTrigger value="available">Trajets disponibles</TabsTrigger>
              <TabsTrigger value="my-requests">Mes demandes</TabsTrigger>
              <TabsTrigger value="my-trips">Mes trajets</TabsTrigger>
            </TabsList>

            <TabsContent value="available">
              <AvailableTripsTab event={event} sentRequestTripIds={sentRequestTripIds} />
            </TabsContent>

            <TabsContent value="my-requests">
              <MyRequestsTab event={event} />
            </TabsContent>

            <TabsContent value="my-trips">
              <MyTripsTab event={event} />
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
