import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

/**
 * 클라이언트 하이드레이션이 끝났는지. 서버 렌더와 첫 클라이언트 렌더에서는 false, 이후 true.
 * localStorage 등 브라우저 전용 값을 읽기 전에 사용한다.
 * zustand persist 스토어의 복원 완료를 기다려야 하면 스토어의 persist.onFinishHydration 을 구독하는 훅을 따로 만든다.
 */
export function useHydrated(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
}
