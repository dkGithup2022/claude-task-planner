import Link from "next/link";
import { cn } from "@/lib/utils";
import type { TextLinkProps, TextLinkTone } from "./TextLink.types";

const toneClass: Record<TextLinkTone, string> = {
  default: "text-foreground",
  secondary: "text-text-secondary",
};

export function TextLink({ href, children, tone = "default", className }: TextLinkProps) {
  return (
    <Link href={href} className={cn("hover:text-accent-secondary hover:underline", toneClass[tone], className)}>
      {children}
    </Link>
  );
}
