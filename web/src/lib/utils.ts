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

/**
 * 서버의 UTC 문자열(2026-11-20T04:16:15Z)을 브라우저 시간대의 "MM-DD HH:mm" 으로. 예: "11-20 13:16" (한국)
 * withYear 면 "YYYY-MM-DD HH:mm".
 */
export function formatShortDateTime(iso: string, withYear = false, timeZone?: string): string {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-CA", {
      timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
    })
      .formatToParts(new Date(iso))
      .map((part) => [part.type, part.value]),
  );
  const date = `${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
  return withYear ? `${parts.year}-${date}` : date;
}
