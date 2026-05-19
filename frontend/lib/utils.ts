import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function daysUntil(date: string | Date): number {
  const target = new Date(date);
  const now = new Date();
  const diff = target.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case "urgent":
      return "bg-danger text-white";
    case "high":
      return "bg-warning text-white";
    case "medium":
      return "bg-compliance-100 text-compliance-800";
    default:
      return "bg-muted text-muted-foreground";
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "completed":
      return "text-success bg-success-light";
    case "in_progress":
      return "text-compliance-600 bg-compliance-50";
    case "overdue":
      return "text-danger bg-danger-light";
    case "not_started":
      return "text-muted-foreground bg-muted";
    default:
      return "text-muted-foreground bg-muted";
  }
}
