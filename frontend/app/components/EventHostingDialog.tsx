import { EventHostingDialog as RefactoredEventHostingDialog } from "./hosting/EventHostingDialog";
import { type EventType } from "~/lib/event";

interface EventHostingDialogProps {
  event: EventType | null;
  isOpen: boolean;
  onClose: () => void;
}

// Composant utilisant la version refactorisée
export function EventHostingDialog(props: EventHostingDialogProps) {
  return <RefactoredEventHostingDialog {...props} />;
}
