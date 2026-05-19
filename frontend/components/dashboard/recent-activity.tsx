"""use client"""

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate, daysUntil, getStatusColor } from "@/lib/utils";
import {
  Activity,
  FileCheck,
  AlertCircle,
  Clock,
} from "lucide-react";

interface RecentActivityProps {
  events: any[];
}

export function RecentActivity({ events }: RecentActivityProps) {
  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-compliance-600" />
          <CardTitle>Recent Activity</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {!events || events.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground text-sm">
            No recent activity
          </div>
        ) : (
          <div className="space-y-3">
            {events.map((event) => {
              const days = event.days_remaining ?? daysUntil(event.due_date);
              const isOverdue = days < 0;
              
              return (
                <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-all-200">
                  <div className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                    event.status === "completed"
                      ? "bg-success-light text-success"
                      : isOverdue
                      ? "bg-danger-light text-danger"
                      : "bg-compliance-50 text-compliance-600"
                  )}>
                    {event.status === "completed" ? (
                      <FileCheck className="h-4 w-4" />
                    ) : isOverdue ? (
                      <AlertCircle className="h-4 w-4" />
                    ) : (
                      <Clock className="h-4 w-4" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{event.title}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {event.description?.substring(0, 80)}...
                    </p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={cn(
                        "text-[10px] px-1.5 py-0.5 rounded-full font-medium",
                        getStatusColor(event.status)
                      )}>
                        {event.status?.replace("_", " ")}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {formatDate(event.due_date)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

import { cn } from "@/lib/utils";
