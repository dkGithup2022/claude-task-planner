import { PlansSkeleton } from "./PlansSkeleton";

export default function Loading() {
  return (
    <div className="mx-auto flex max-w-[1120px] flex-col gap-4 px-6 pt-[106px] pb-16">
      <div className="h-7 w-24 animate-pulse bg-tertiary" />
      <PlansSkeleton />
    </div>
  );
}
