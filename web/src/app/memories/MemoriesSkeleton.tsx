/** 지식 목록의 로딩 상자. 표 줄 5개 */
export function MemoriesSkeleton() {
  return (
    <div className="flex flex-col gap-2" aria-busy="true" aria-label="불러오는 중">
      {Array.from({ length: 5 }, (_, row) => (
        <div key={row} className="h-11 animate-pulse bg-secondary-bg" />
      ))}
    </div>
  );
}
