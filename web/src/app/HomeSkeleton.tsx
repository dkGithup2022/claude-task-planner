/** 메인의 로딩 상자. 구역 5개, 구역마다 줄 2개. loading.tsx 와 HomeClient 가 같이 쓴다 */
export function HomeSkeleton() {
  return (
    <div className="flex flex-col gap-10" aria-busy="true" aria-label="불러오는 중">
      {Array.from({ length: 5 }, (_, section) => (
        <div key={section} className="flex flex-col gap-3">
          <div className="h-4 w-32 animate-pulse bg-tertiary" />
          <div className="h-11 animate-pulse bg-secondary-bg" />
          <div className="h-11 animate-pulse bg-secondary-bg" />
        </div>
      ))}
    </div>
  );
}
