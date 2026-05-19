"""use client"""

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { formatDate, daysUntil, getPriorityColor, getStatusColor } from "@/lib/utils";
import {
  CalendarDays,
  Clock,
  AlertCircle,
  ChevronRight,
  Filter,
} from "lucide-react";
import { useState } from "react";

interface ComplianceCalendarProps {
  events: any[];
  loading: boolean;
}

export function ComplianceCalendar({ events, loading }: ComplianceCalendarProps) {
  const [filter, setFilter] = useState("all");

  const filteredEvents = events?.filter((event) => {
    if (filter === "all") return true;
    if (filter === "urgent") return event.priority === "urgent" || event.days_remaining <= 7;
    if (filter === "high") return event.priority === "high";
    if (filter === "completed") return event.status === "completed";
    return true;
  }) || [];

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarDays className="h-5 w-5 text-compliance-600" />
            <CardTitle>Compliance Calendar</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <select
              className="text-xs border rounded-md px-2 py-1 bg-white"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All Events</option>
              <option value="urgent">Urgent</option>
              <option value="high">High Priority</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <CalendarDays className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No upcoming compliance events</p>
            <p className="text-sm">All caught up!</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {filteredEvents.map((event) => {
              const days = event.days_remaining ?? daysUntil(event.due_date);
              const isOverdue = days < 0;
              const isUrgent = days <= 7 && days >= 0;
              
              return (
                <div
                  key={event.id}
                  className={cn(
                    "group flex items-start gap-3 p-3 rounded-lg border transition-all-200 hover:shadow-sm cursor-pointer",
                    isOverdue
                      ? "bg-danger-light border-danger/20"
                      : isUrgent
                      ? "bg-warning-light border-warning/20"
                      : "bg-white border-gray-100 hover:border-compliance-200"
                  )}
                >
                  <div className={cn(
                    "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                    isOverdue
                      ? "bg-danger text-white"
                      : isUrgent
                      ? "bg-warning text-white"
                      : "bg-compliance-50 text-compliance-600"
                  )}>
                    {isOverdue ? (
                      <AlertCircle className="h-5 w-5" />
                    ) : (
                      <Clock className="h-5 w-5" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-medium text-sm text-gray-900 truncate">
                          {event.title}
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                          {event.description}
                        </p>
                      </div>
                      <Badge
                        variant={isOverdue ? "destructive" : isUrgent ? "warning" : "default"}
                        className="shrink-0 text-[10px]"
                      >
                        {isOverdue ? `${Math.abs(days)}d overdue` : `${days}d left`}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-muted-foreground">
                        Due: {formatDate(event.due_date)}
                      </span>
                      {event.form && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                          {event.form}
                        </span>
                      )}
                      <span className={cn(
                        "text-xs px-2 py-0.5 rounded-full font-medium",
                        getStatusColor(event.status)
                      )}>
                        {event.status?.replace("_", " ")}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 shrink-0 mt-3" />
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
