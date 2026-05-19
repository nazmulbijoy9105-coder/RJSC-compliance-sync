"""use client"""

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { DashboardLayout } from "@/components/dashboard/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { formatDate, daysUntil, getPriorityColor, getStatusColor } from "@/lib/utils";
import { CalendarDays, CheckCircle2, Clock, AlertTriangle, Filter } from "lucide-react";

export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState("all");
  
  const { data: events, isLoading } = useQuery({
    queryKey: ["compliance-events", activeTab],
    queryFn: async () => {
      const params = activeTab !== "all" ? `?status=${activeTab}` : "";
      const response = await api.get(`/compliance/events${params}`);
      return response.data;
    },
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Compliance Events</h1>
            <p className="text-muted-foreground mt-1">
              Track and manage all your compliance deadlines
            </p>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-white border">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="not_started">Not Started</TabsTrigger>
            <TabsTrigger value="in_progress">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="overdue">Overdue</TabsTrigger>
          </TabsList>
        </Tabs>

        <Card className="border-0 shadow-sm">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            ) : !events || events.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <CalendarDays className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No events found</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {events.map((event: any) => {
                  const days = event.days_remaining ?? daysUntil(event.due_date);
                  const isOverdue = days < 0;
                  
                  return (
                    <div
                      key={event.id}
                      className="flex items-start gap-4 p-4 hover:bg-gray-50 transition-all-200"
                    >
                      <div className={cn(
                        "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                        event.status === "completed"
                          ? "bg-success-light text-success"
                          : isOverdue
                          ? "bg-danger-light text-danger"
                          : days <= 7
                          ? "bg-warning-light text-warning"
                          : "bg-compliance-50 text-compliance-600"
                      )}>
                        {event.status === "completed" ? (
                          <CheckCircle2 className="h-5 w-5" />
                        ) : isOverdue ? (
                          <AlertTriangle className="h-5 w-5" />
                        ) : (
                          <Clock className="h-5 w-5" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="font-medium text-gray-900">{event.title}</p>
                            <p className="text-sm text-muted-foreground mt-0.5">
                              {event.description}
                            </p>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <Badge
                              variant={isOverdue ? "destructive" : days <= 7 ? "warning" : "default"}
                            >
                              {isOverdue ? `${Math.abs(days)}d overdue` : `${days}d left`}
                            </Badge>
                            <span className={cn(
                              "text-xs px-2 py-0.5 rounded-full",
                              getStatusColor(event.status)
                            )}>
                              {event.status?.replace("_", " ")}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-xs text-muted-foreground">
                            Due: {formatDate(event.due_date)}
                          </span>
                          {event.form && (
                            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                              {event.form}
                            </span>
                          )}
                          {event.fiscal_year && (
                            <span className="text-xs text-muted-foreground">
                              FY {event.fiscal_year}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {event.status !== "completed" && (
                          <Button size="sm" variant="outline">
                            Mark Done
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

import { cn } from "@/lib/utils";
