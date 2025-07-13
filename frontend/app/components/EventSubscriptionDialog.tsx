import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import type { EventType } from "~/lib/event";
import { AnswerEnum, useCreateSubscription, type EventSubscription } from "~/lib/eventSubscription";
import { Spinner } from "./ui/spinner";
import type { z } from "zod";

interface EventSubscriptionDialogProps {
  event: EventType;
  isOpen: boolean;
  onClose: () => void;
  existingSubscription?: EventSubscription;
}

export function EventSubscriptionDialog({
  event,
  isOpen,
  onClose,
  existingSubscription
}: EventSubscriptionDialogProps) {
  // Initialiser les valeurs par défaut en fonction de l'inscription existante
  const [answer, setAnswer] = useState<z.infer<typeof AnswerEnum>>(
    existingSubscription?.answer || "YES"
  );
  const [canInvite, setCanInvite] = useState<boolean>(
    existingSubscription?.can_invite || false
  );
  const mutation = useCreateSubscription();

  // Mettre à jour les valeurs quand l'inscription existante change ou quand le dialogue s'ouvre
  useEffect(() => {
    if (isOpen) {
      if (existingSubscription) {
        setAnswer(existingSubscription.answer);
        setCanInvite(existingSubscription.can_invite);
      } else {
        // Réinitialiser à des valeurs par défaut si pas d'inscription existante
        setAnswer("YES");
        setCanInvite(false);
      }
    }
  }, [existingSubscription, isOpen]);

  const handleSubmit = () => {
    mutation.mutate({
      eventId: event.id,
      data: {
        answer,
        can_invite: canInvite,
      },
    });
    onClose(); // Fermer la boîte de dialogue après soumission
  };

  const isEditing = Boolean(existingSubscription);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Modifier ma réponse" : `S'inscrire à ${event.name}`}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="answer">Votre réponse</Label>
            <div className="flex gap-2">
              <Button
                id="answer-yes"
                type="button"
                variant={answer === "YES" ? "default" : "outline"}
                onClick={() => setAnswer("YES")}
              >
                Je participe
              </Button>
              <Button
                id="answer-maybe"
                type="button"
                variant={answer === "MAYBE" ? "default" : "outline"}
                onClick={() => setAnswer("MAYBE")}
              >
                Peut-être
              </Button>
              <Button
                id="answer-no"
                type="button"
                variant={answer === "NO" ? "default" : "outline"}
                onClick={() => setAnswer("NO")}
              >
                Je ne participe pas
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="can-invite"
              checked={canInvite}
              onChange={(e) => setCanInvite(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-royal-blue-600 focus:ring-royal-blue-500"
            />
            <Label htmlFor="can-invite">
              Je peux inviter d'autres personnes
            </Label>
          </div>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={mutation.isPending}
            className="bg-royal-blue-600 hover:bg-royal-blue-700"
          >
            {mutation.isPending ? <Spinner className="mr-2" /> : null}
            {isEditing ? "Mettre à jour" : "Confirmer"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
