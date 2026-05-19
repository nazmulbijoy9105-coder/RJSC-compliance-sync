"""use client"""

import { useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { usePathname, useRouter } from "next/navigation";

const publicPaths = ["/login", "/register", "/"];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated && !publicPaths.includes(pathname)) {
      router.push("/login");
    }
    if (isAuthenticated && pathname === "/login") {
      router.push("/dashboard");
    }
  }, [isAuthenticated, pathname, router]);

  return <>{children}</>;
}
