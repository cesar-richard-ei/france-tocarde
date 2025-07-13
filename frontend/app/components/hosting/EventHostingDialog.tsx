import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { Button } from "../ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { useAuth } from "../auth/AuthContext";
import { type EventType } from "~/lib/event";
import { AvailableHostingsTab } from "./AvailableHostingsTab";
import { MyHostingRequestsTab } from "./MyHostingRequestsTab";
import { MyHostingsTab } from "./MyHostingsTab";
import { useSentHostingRequests } from "~/lib/eventHosting";

interface EventHostingDialogProps {
  event: EventType | null;
  isOpen: boolean;
  onClose: () => void;
}

export function EventHostingDialog({ event, isOpen, onClose }: EventHostingDialogProps) {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState("available");
  const { data: sentRequests } = useSentHostingRequests({
    enabled: isAuthenticated
  });

  // Extraire les ID des hébergements pour lesquels l'utilisateur a déjà des demandes acceptées
  const acceptedRequestHostingIds = (sentRequests?.results || [])
    .filter(req => req.status === "ACCEPTED")
    .map(req => typeof req.hosting === 'object' && req.hosting !== null ? req.hosting.id : Number(req.hosting));

  if (!event) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Hébergements pour {event.name}</DialogTitle>
        </DialogHeader>

        {!isAuthenticated ? (
          <div className="text-center p-4">
            <p className="mb-4">Vous devez être connecté pour accéder aux hébergements</p>
            <Button onClick={onClose}>Se connecter</Button>
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full overflow-y-auto flex-1">
            <TabsList className="grid grid-cols-3">
              <TabsTrigger value="available">Hébergements disponibles</TabsTrigger>
              <TabsTrigger value="my-requests">Mes demandes</TabsTrigger>
              <TabsTrigger value="my-hostings">Mes hébergements</TabsTrigger>
            </TabsList>

            <TabsContent value="available">
              <AvailableHostingsTab
                event={event}
                acceptedRequestHostingIds={acceptedRequestHostingIds}
              />
            </TabsContent>

            <TabsContent value="my-requests">
              <MyHostingRequestsTab event={event} />
            </TabsContent>

            <TabsContent value="my-hostings">
              <MyHostingsTab event={event} />
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
