import { HomeSkeleton } from "./HomeSkeleton";

export default function Loading() {
  return (
    <div className="mx-auto max-w-[1120px] px-6 pt-[106px] pb-16">
      <HomeSkeleton />
    </div>
  );
}
