"""use client"""

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Building2,
  CalendarClock,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Clock,
} from "lucide-react";

interface StatsCardsProps {
  stats: any;
  loading: boolean;
}

export function StatsCards({ stats, loading }: StatsCardsProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 w-24 bg-gray-200 rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-16 bg-gray-200 rounded mb-2" />
              <div className="h-3 w-32 bg-gray-200 rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Total Companies",
      value: stats?.total_companies || 0,
      description: "Active entities",
      icon: Building2,
      color: "text-compliance-600",
      bgColor: "bg-compliance-50",
    },
    {
      title: "Upcoming Events",
      value: stats?.upcoming_events || 0,
      description: "Next 30 days",
      icon: CalendarClock,
      color: "text-warning",
      bgColor: "bg-warning-light",
    },
    {
      title: "Overdue",
      value: stats?.overdue_events || 0,
      description: "Requires immediate action",
      icon: AlertTriangle,
      color: "text-danger",
      bgColor: "bg-danger-light",
    },
    {
      title: "Completed This Month",
      value: stats?.completed_this_month || 0,
      description: "On-time filings",
      icon: CheckCircle2,
      color: "text-success",
      bgColor: "bg-success-light",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title} className="border-0 shadow-sm hover:shadow-md transition-all-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <div className={cn("p-2 rounded-lg", card.bgColor)}>
              <card.icon className={cn("h-4 w-4", card.color)} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
            {card.title === "Total Companies" && stats?.average_compliance_score > 0 && (
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Avg Compliance Score</span>
                  <span className="font-medium">{stats.average_compliance_score}%</span>
                </div>
                <Progress
                  value={stats.average_compliance_score}
                  max={100}
                  variant={stats.average_compliance_score >= 80 ? "success" : stats.average_compliance_score >= 60 ? "warning" : "danger"}
                  className="h-1.5"
                />
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Need cn import
import { cn } from "@/lib/utils";
