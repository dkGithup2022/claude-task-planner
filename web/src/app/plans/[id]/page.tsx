import { Suspense } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { fetchPlan } from "@/lib/plan-api";
import { PlanGraphClient } from "./PlanGraphClient";

export async function generateMetadata({ params }: PageProps<"/plans/[id]">): Promise<Metadata> {
  const { id } = await params;
  try {
    const plan = await fetchPlan(Number(id));
    return { title: `계획 ${plan.plan_id}`, description: plan.title };
  } catch {
    return { title: `계획 ${id}` };
  }
}

export default async function Page({ params }: PageProps<"/plans/[id]">) {
  const { id } = await params;
  const planId = Number(id);
  if (!Number.isInteger(planId) || planId <= 0) notFound();
  return (
    <Suspense>
      <PlanGraphClient planId={planId} />
    </Suspense>
  );
}
