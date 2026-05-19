"""use client"""

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  ShieldAlert,
  ShieldCheck,
  Shield,
  AlertTriangle,
} from "lucide-react";

export function RiskHeatmap() {
  const { data: heatmap, isLoading } = useQuery({
    queryKey: ["risk-heatmap"],
    queryFn: async () => {
      const response = await api.get("/compliance/risk-heatmap");
      return response.data;
    },
  });

  const total = heatmap?.total || 0;
  const green = heatmap?.green || 0;
  const yellow = heatmap?.yellow || 0;
  const red = heatmap?.red || 0;

  const greenPct = total > 0 ? (green / total) * 100 : 0;
  const yellowPct = total > 0 ? (yellow / total) * 100 : 0;
  const redPct = total > 0 ? (red / total) * 100 : 0;

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-compliance-600" />
          <CardTitle>Risk Heatmap</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-40 bg-gray-100 rounded-lg animate-pulse" />
        ) : (
          <div className="space-y-4">
            {/* Green */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-success" />
                  <span className="text-gray-700">On Track</span>
                </div>
                <span className="font-medium text-success">{green}</span>
              </div>
              <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full bg-success transition-all duration-500"
                  style={{ width: `${greenPct}%` }}
                />
              </div>
            </div>

            {/* Yellow */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span className="text-gray-700">Approaching</span>
                </div>
                <span className="font-medium text-warning">{yellow}</span>
              </div>
              <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full bg-warning transition-all duration-500"
                  style={{ width: `${yellowPct}%` }}
                />
              </div>
            </div>

            {/* Red */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-danger" />
                  <span className="text-gray-700">Overdue / Urgent</span>
                </div>
                <span className="font-medium text-danger">{red}</span>
              </div>
              <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full bg-danger transition-all duration-500"
                  style={{ width: `${redPct}%` }}
                />
              </div>
            </div>

            {/* Summary */}
            <div className="pt-3 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Total Events</span>
                <span className="font-bold text-lg">{total}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
