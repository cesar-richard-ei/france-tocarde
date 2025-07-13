import { Badge } from "../ui/badge";
import { HelpCircle, CheckCircle, XCircle } from "lucide-react";

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  switch (status) {
    case "PENDING":
      return (
        <Badge variant="outline" className="bg-yellow-50">
          <HelpCircle className="h-3 w-3 mr-1 text-yellow-500" />
          En attente
        </Badge>
      );
    case "ACCEPTED":
      return (
        <Badge variant="outline" className="bg-green-50">
          <CheckCircle className="h-3 w-3 mr-1 text-green-500" />
          Acceptée
        </Badge>
      );
    case "REJECTED":
      return (
        <Badge variant="outline" className="bg-red-50">
          <XCircle className="h-3 w-3 mr-1 text-red-500" />
          Refusée
        </Badge>
      );
    case "CANCELLED":
      return (
        <Badge variant="outline" className="bg-gray-100">
          <XCircle className="h-3 w-3 mr-1 text-gray-500" />
          Annulée
        </Badge>
      );
    default:
      return (
        <Badge variant="outline">
          {status}
        </Badge>
      );
  }
}
