import { CarpoolDialog as RefactoredCarpoolDialog } from "./carpool/CarpoolDialog";
import { type EventType } from "~/lib/event";

interface CarpoolDialogProps {
  event: EventType | null;
  isOpen: boolean;
  onClose: () => void;
}

// Composant utilisant la version refactorisée
export function CarpoolDialog(props: CarpoolDialogProps) {
  return <RefactoredCarpoolDialog {...props} />;
}
