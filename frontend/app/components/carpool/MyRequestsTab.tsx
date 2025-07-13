import { Spinner } from "../ui/spinner";
import { CarpoolRequestCard } from "./CarpoolRequestCard";
import { useUpdateCarpoolRequestStatus, useSentCarpoolRequests } from "~/lib/carpool";
import { type EventType } from "~/lib/event";

interface MyRequestsTabProps {
  event: EventType;
}

export function MyRequestsTab({ event }: MyRequestsTabProps) {
  const { data: sentRequests, isLoading: isLoadingSentRequests } = useSentCarpoolRequests();
  const updateRequestStatusMutation = useUpdateCarpoolRequestStatus();

  const handleCancelRequest = (requestId: number) => {
    updateRequestStatusMutation.mutate({
      requestId,
      status: "CANCELLED",
      responseMessage: "",
    });
  };

  const filteredRequests = sentRequests?.results.filter(req => {
    if (typeof req.trip === 'object' && req.trip?.event?.id) {
      return Number(req.trip.event.id) === Number(event?.id);
    }
    return false;
  });

  if (isLoadingSentRequests) {
    return (
      <div className="flex justify-center p-8">
        <Spinner />
      </div>
    );
  }

  if (!filteredRequests || filteredRequests.length === 0) {
    return (
      <div className="text-center p-6">
        <p>Vous n'avez pas encore fait de demande de covoiturage pour cet événement</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {filteredRequests.map((request) => (
        <CarpoolRequestCard
          key={request.id}
          request={request}
          isSent={true}
          onCancelRequest={request.status === "PENDING" ? handleCancelRequest : undefined}
        />
      ))}
    </div>
  );
}
