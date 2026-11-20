import type { ReactNode } from "react";

export type TextLinkTone = "default" | "secondary";

export interface TextLinkProps {
  href: string;
  children: ReactNode;
  tone?: TextLinkTone;
  className?: string;
}
