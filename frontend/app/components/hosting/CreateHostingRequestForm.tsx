import { useState } from "react";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Spinner } from "../ui/spinner";
import { useCreateEventHostingRequest } from "~/lib/eventHosting";
import { type EventHosting } from "~/lib/eventHosting";

interface CreateHostingRequestFormProps {
  hosting: EventHosting;
  onCancel: () => void;
  onSuccess: () => void;
}

export function CreateHostingRequestForm({ hosting, onCancel, onSuccess }: CreateHostingRequestFormProps) {
  const [hostingRequest, setHostingRequest] = useState({
    hostingId: hosting.id,
    message: "",
  });

  const createRequestMutation = useCreateEventHostingRequest();

  const handleCreateRequest = () => {
    createRequestMutation.mutate(hostingRequest, {
      onSuccess: () => {
        onSuccess();
      }
    });
  };

  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Demande d'hébergement</h3>
      <p className="mb-2">
        <strong>Hôte:</strong>{`${hosting.host?.first_name} ${hosting.host?.last_name}`}
      </p>
      <p className="mb-4">
        <strong>Lits disponibles:</strong> {hosting.available_beds_remaining ?? hosting.available_beds}
      </p>
      <div className="space-y-4">
        <div>
          <Label htmlFor="request_message">Message (optionnel)</Label>
          <Textarea
            id="request_message"
            value={hostingRequest.message}
            onChange={(e) => setHostingRequest({ ...hostingRequest, message: e.target.value })}
            placeholder="Message à l'attention de l'hôte..."
          />
        </div>
        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={onCancel}>
            Annuler
          </Button>
          <Button
            onClick={handleCreateRequest}
            disabled={createRequestMutation.isPending}
          >
            {createRequestMutation.isPending ? <Spinner className="mr-2" /> : null}
            Envoyer la demande
          </Button>
        </div>
      </div>
    </div>
  );
}
