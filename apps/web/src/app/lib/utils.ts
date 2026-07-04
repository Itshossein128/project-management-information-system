import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

// Function to manage cn
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
