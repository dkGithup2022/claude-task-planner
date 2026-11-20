import { Suspense } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { fetchMemory } from "@/lib/memory-api";
import { MemoryDetailClient } from "./MemoryDetailClient";

export async function generateMetadata({ params }: PageProps<"/memories/[id]">): Promise<Metadata> {
  const { id } = await params;
  try {
    const memory = await fetchMemory(Number(id));
    return { title: `지식 #${memory.memory_id} ${memory.theme}` };
  } catch {
    return { title: `지식 #${id}` };
  }
}

export default async function Page({ params }: PageProps<"/memories/[id]">) {
  const { id } = await params;
  const memoryId = Number(id);
  if (!Number.isInteger(memoryId) || memoryId <= 0) notFound();
  return (
    <Suspense>
      <MemoryDetailClient memoryId={memoryId} />
    </Suspense>
  );
}
