import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Spinner } from "../ui/spinner";
import { useCreateEventHosting } from "~/lib/eventHosting";
import { type EventType } from "~/lib/event";

interface CreateHostingFormProps {
  event: EventType;
  onCancel: () => void;
  onSuccess: () => void;
}

export function CreateHostingForm({ event, onCancel, onSuccess }: CreateHostingFormProps) {
  const [newHosting, setNewHosting] = useState({
    event: event.id,
    available_beds: 1,
    custom_rules: "",
    address_override: "",
    city_override: "",
    zip_code_override: "",
    country_override: "",
    is_active: true,
  });

  const createHostingMutation = useCreateEventHosting();

  const handleCreateHosting = () => {
    // Convertir les valeurs numériques
    const hostingData = {
      ...newHosting,
      event: Number(event.id),
      available_beds: Number(newHosting.available_beds)
    };

    createHostingMutation.mutate(hostingData, {
      onSuccess: () => {
        onSuccess();
      }
    });
  };

  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Proposer un hébergement</h3>
      <div className="space-y-4">
        <div>
          <Label htmlFor="available_beds">Nombre de lits disponibles</Label>
          <Input
            id="available_beds"
            type="number"
            min="1"
            value={newHosting.available_beds}
            onChange={(e) => setNewHosting({ ...newHosting, available_beds: parseInt(e.target.value) })}
          />
        </div>
        <div>
          <Label htmlFor="custom_rules">Règles spécifiques (optionnel)</Label>
          <Textarea
            id="custom_rules"
            value={newHosting.custom_rules}
            onChange={(e) => setNewHosting({ ...newHosting, custom_rules: e.target.value })}
            placeholder="Règles spécifiques pour cet hébergement..."
          />
        </div>
        <div>
          <Label htmlFor="address_override">Adresse (optionnel)</Label>
          <Input
            id="address_override"
            value={newHosting.address_override}
            onChange={(e) => setNewHosting({ ...newHosting, address_override: e.target.value })}
            placeholder="Adresse spécifique pour cet hébergement..."
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="city_override">Ville (optionnel)</Label>
            <Input
              id="city_override"
              value={newHosting.city_override}
              onChange={(e) => setNewHosting({ ...newHosting, city_override: e.target.value })}
              placeholder="Ville spécifique..."
            />
          </div>
          <div>
            <Label htmlFor="zip_code_override">Code postal (optionnel)</Label>
            <Input
              id="zip_code_override"
              value={newHosting.zip_code_override}
              onChange={(e) => setNewHosting({ ...newHosting, zip_code_override: e.target.value })}
              placeholder="Code postal..."
            />
          </div>
        </div>
        <div>
          <Label htmlFor="country_override">Pays (optionnel)</Label>
          <Input
            id="country_override"
            value={newHosting.country_override}
            onChange={(e) => setNewHosting({ ...newHosting, country_override: e.target.value })}
            placeholder="Pays spécifique..."
          />
        </div>
        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={onCancel}>Annuler</Button>
          <Button
            onClick={handleCreateHosting}
            disabled={createHostingMutation.isPending || newHosting.available_beds < 1}
          >
            {createHostingMutation.isPending ? <Spinner className="mr-2" /> : null}
            Proposer l'hébergement
          </Button>
        </div>
      </div>
    </div>
  );
}
