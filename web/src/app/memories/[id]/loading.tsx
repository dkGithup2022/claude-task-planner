import { MemoryDetailSkeleton } from "./MemoryDetailSkeleton";

export default function Loading() {
  return (
    <div className="mx-auto max-w-[880px] px-6 pt-[130px] pb-16">
      <MemoryDetailSkeleton />
    </div>
  );
}
