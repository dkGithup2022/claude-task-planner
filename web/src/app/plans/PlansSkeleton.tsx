/** 계획 목록의 로딩 상자. 표 줄 4개 */
export function PlansSkeleton() {
  return (
    <div className="flex flex-col gap-2" aria-busy="true" aria-label="불러오는 중">
      {Array.from({ length: 4 }, (_, row) => (
        <div key={row} className="h-11 animate-pulse bg-secondary-bg" />
      ))}
    </div>
  );
}
