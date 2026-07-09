"use client";

import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { Loader } from "@/components/ui/Loader";

export default function RootPage() {
  const { auth } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (auth.authHydrated) {
      if (auth.isAuthenticated) {
        router.push("/dashboard");
      } else {
        router.push("/auth");
      }
    }
  }, [auth.authHydrated, auth.isAuthenticated, router]);

  return <Loader />;
}
