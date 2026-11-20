/** 지식 조회의 로딩 상자. 머리, 본문 문단 3개 */
export function MemoryDetailSkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-busy="true" aria-label="불러오는 중">
      <div className="h-8 w-1/2 animate-pulse bg-tertiary" />
      <div className="h-5 w-1/3 animate-pulse bg-secondary-bg" />
      {Array.from({ length: 3 }, (_, index) => (
        <div key={index} className="h-20 animate-pulse bg-secondary-bg" />
      ))}
    </div>
  );
}
