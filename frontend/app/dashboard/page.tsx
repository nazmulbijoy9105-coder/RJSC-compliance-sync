"""use client"""

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { DashboardLayout } from "@/components/dashboard/layout";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { ComplianceCalendar } from "@/components/dashboard/compliance-calendar";
import { RiskHeatmap } from "@/components/dashboard/risk-heatmap";
import { RecentActivity } from "@/components/dashboard/recent-activity";
import { ComplianceScoreChart } from "@/components/dashboard/compliance-score-chart";

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const response = await api.get("/dashboard/stats");
      return response.data;
    },
  });

  const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ["compliance-events"],
    queryFn: async () => {
      const response = await api.get("/compliance/events?status=not_started&status=in_progress");
      return response.data;
    },
  });

  const { data: scores } = useQuery({
    queryKey: ["compliance-scores"],
    queryFn: async () => {
      const response = await api.get("/dashboard/compliance-scores");
      return response.data;
    },
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Monitor your compliance status and upcoming deadlines
          </p>
        </div>

        <StatsCards stats={stats} loading={statsLoading} />

        <div className="grid gap-6 lg:grid-cols-7">
          <div className="lg:col-span-4">
            <ComplianceCalendar events={events} loading={eventsLoading} />
          </div>
          <div className="lg:col-span-3 space-y-6">
            <RiskHeatmap />
            <ComplianceScoreChart scores={scores} />
          </div>
        </div>

        <RecentActivity events={events?.slice(0, 5)} />
      </div>
    </DashboardLayout>
  );
}
