import React from "react";
import { Loader2 } from "lucide-react";

interface LoaderProps {
  size?: number;
  className?: string;
  fullScreen?: boolean;
}

export const Loader: React.FC<LoaderProps> = ({ size = 26, className = "", fullScreen = true }) => {
  const containerClass = fullScreen
    ? "flex h-screen items-center justify-center bg-[#08090d] text-white"
    : "flex items-center justify-center";

  return (
    <div className={containerClass}>
      <Loader2 size={size} className={`animate-spin text-sky-300 ${className}`} />
    </div>
  );
};
