import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Tailwind 클래스 조합. 충돌 시 뒤의 클래스가 이긴다. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * ISO 날짜 또는 epoch ms 를 한국어 상대 시간으로.
 * 1분 미만 "방금", 1시간 미만 "N분 전", 24시간 미만 "N시간 전", 30일 미만 "N일 전", 그 외 "YYYY.MM.DD"
 */
export function formatRelativeDate(createdAt: string | number, now: number = Date.now()): string {
  const created = typeof createdAt === "number" ? createdAt : new Date(createdAt).getTime();
  const minutes = Math.floor((now - created) / 60_000);
  if (minutes < 1) return "방금";
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}일 전`;
  const d = new Date(created);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}
