import type { TableProps } from "./Table.types";

export function Table({ children, minWidth = 680, caption }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left tabular-nums" style={{ minWidth }}>
        {caption && <caption className="sr-only">{caption}</caption>}
        {children}
      </table>
    </div>
  );
}
