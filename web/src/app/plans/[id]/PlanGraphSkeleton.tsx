/** 계획 그래프의 로딩 상자. 요약 세 줄, 그래프, 패널 */
export function PlanGraphSkeleton() {
  return (
    <div className="flex flex-col gap-5" aria-busy="true" aria-label="불러오는 중">
      <div className="flex flex-col gap-2">
        <div className="h-7 w-2/3 animate-pulse bg-tertiary" />
        <div className="h-5 w-1/3 animate-pulse bg-secondary-bg" />
        <div className="h-5 w-1/4 animate-pulse bg-secondary-bg" />
      </div>
      <div className="flex flex-wrap gap-6">
        <div className="h-[720px] flex-[999_1_560px] animate-pulse bg-secondary-bg" />
        <div className="h-96 flex-[1_1_360px] animate-pulse bg-secondary-bg" />
      </div>
    </div>
  );
}
