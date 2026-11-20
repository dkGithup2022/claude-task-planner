import type { EmptyStateProps } from "./EmptyState.types";

export function EmptyState({ children }: EmptyStateProps) {
  return <div className="border border-border-subtle p-5 text-text-tertiary">{children}</div>;
}
