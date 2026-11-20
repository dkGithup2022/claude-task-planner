import type { ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "outline" | "subtle";
export type ButtonSize = "sm" | "md";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}
