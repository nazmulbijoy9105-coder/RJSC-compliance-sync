"""use client"""

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ComplianceScoreChartProps {
  scores: any[];
}

export function ComplianceScoreChart({ scores }: ComplianceScoreChartProps) {
  if (!scores || scores.length === 0) {
    return (
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Compliance Scores</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6 text-muted-foreground text-sm">
            No companies registered yet
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Compliance Scores</CardTitle>
          <Badge variant="outline" className="text-xs">{scores.length} Companies</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-[300px] overflow-y-auto">
          {scores.map((score) => (
            <div key={score.company_id} className="space-y-1.5">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 truncate max-w-[180px]">
                  {score.company_name}
                </span>
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "font-bold",
                    score.score >= 80 ? "text-success" : score.score >= 60 ? "text-warning" : "text-danger"
                  )}>
                    {score.score}%
                  </span>
                  {score.score >= 80 ? (
                    <TrendingUp className="h-3.5 w-3.5 text-success" />
                  ) : score.score >= 60 ? (
                    <Minus className="h-3.5 w-3.5 text-warning" />
                  ) : (
                    <TrendingDown className="h-3.5 w-3.5 text-danger" />
                  )}
                </div>
              </div>
              <Progress
                value={score.score}
                max={100}
                variant={score.score >= 80 ? "success" : score.score >= 60 ? "warning" : "danger"}
                className="h-2"
              />
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                <span>{score.on_time} on time</span>
                <span>{score.late} late</span>
                <span>{score.overdue} overdue</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

import { cn } from "@/lib/utils";
