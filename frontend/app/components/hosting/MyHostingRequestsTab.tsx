import { Spinner } from "../ui/spinner";
import { HostingRequestCard } from "./HostingRequestCard";
import { useCancelHostingRequest, useSentHostingRequests } from "~/lib/eventHosting";
import { type EventType } from "~/lib/event";

interface MyHostingRequestsTabProps {
  event: EventType;
}

export function MyHostingRequestsTab({ event }: MyHostingRequestsTabProps) {
  const { data: sentRequests, isLoading: isLoadingSentRequests } = useSentHostingRequests();
  const cancelRequestMutation = useCancelHostingRequest();

  const filteredRequests = sentRequests?.results.filter(
    req => Number(req.hosting?.event) === Number(event?.id)
  );

  const handleCancelRequest = (requestId: number) => {
    cancelRequestMutation.mutate(requestId);
  };

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
        <p>Vous n'avez pas encore fait de demande d'hébergement pour cet événement</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {filteredRequests.map((request) => (
        <HostingRequestCard
          key={request.id}
          request={request}
          isSent={true}
          onCancelRequest={request.status === "PENDING" ? handleCancelRequest : undefined}
        />
      ))}
    </div>
  );
}
