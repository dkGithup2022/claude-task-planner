import Link from "next/link";
import { cn } from "@/lib/utils";
import type { AppHeaderProps, AppSection } from "./AppHeader.types";

const MENU: { section: AppSection; href: string; label: string }[] = [
  { section: "plans", href: "/plans", label: "계획" },
  { section: "memories", href: "/memories", label: "지식" },
  { section: "personas", href: "/personas", label: "페르소나" },
];

export function AppHeader({ current, wide }: AppHeaderProps) {
  return (
    <header className="border-b border-border-subtle">
      <nav
        aria-label="주 메뉴"
        className={cn("mx-auto flex flex-wrap items-center gap-7 px-6 py-[18px]", wide ? "max-w-[1232px]" : "max-w-[1120px]")}
      >
        <Link href="/" className="grow text-[15px] font-bold hover:underline">
          task plan manager
        </Link>
        {MENU.map((item) => {
          const active = item.section === current;
          return (
            <Link
              key={item.section}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "hover:text-foreground hover:underline",
                active ? "border-b-2 border-border font-bold text-foreground" : "text-text-secondary",
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
