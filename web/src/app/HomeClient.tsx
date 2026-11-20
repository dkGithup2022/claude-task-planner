"use client";

import { useEffect, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { RecentMemoryRow } from "@/components/memory/RecentMemoryRow";
import { PlanListRow } from "@/components/plan/PlanListRow";
import type { PlanListRowShow } from "@/components/plan/PlanListRow.types";
import { EmptyState } from "@/components/ui/EmptyState";
import { Notice } from "@/components/ui/Notice";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { TextLink } from "@/components/ui/TextLink";
import { showErrorToast } from "@/lib/api/error-toast";
import { fetchMemories } from "@/lib/memory-api";
import { fetchPlans } from "@/lib/plan-api";
import type { PlanSummary } from "@/types/data/domain/plan";
import type { HomeData } from "./home.types";
import { HomeSkeleton } from "./HomeSkeleton";

async function loadHome(): Promise<HomeData> {
  const [running, reviewing, recent, memories, knowledge, attitude, plan] = await Promise.all([
    fetchPlans({ status: "running" }),
    fetchPlans({ status: "reviewing" }),
    fetchPlans({ limit: 5 }),
    fetchMemories({ limit: 5 }),
    fetchMemories({ kind: "knowledge", limit: 1 }),
    fetchMemories({ kind: "attitude", limit: 1 }),
    fetchMemories({ kind: "plan", limit: 1 }),
  ]);
  return {
    running: running.plans,
    reviewing: reviewing.plans,
    recentPlans: recent.plans,
    recentMemories: memories.items,
    memoryTotal: memories.total,
    kindCounts: { knowledge: knowledge.total, attitude: attitude.total, plan: plan.total },
  };
}

function PlanSection({
  title,
  plans,
  show,
  empty,
  action,
}: {
  title: string;
  plans: PlanSummary[];
  show: PlanListRowShow;
  empty: string;
  action?: React.ReactNode;
}) {
  return (
    <section className="flex flex-col gap-3">
      <SectionHeader title={title} action={action} />
      {plans.length === 0 ? (
        <EmptyState>{empty}</EmptyState>
      ) : (
        <div className="border-t border-border">
          {plans.map((plan) => (
            <PlanListRow key={plan.plan_id} plan={plan} show={show} />
          ))}
        </div>
      )}
    </section>
  );
}

export function HomeClient() {
  const [data, setData] = useState<HomeData | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    loadHome()
      .then(setData)
      .catch((err) => {
        setFailed(true);
        showErrorToast(err, "메인 화면을 불러오지 못했습니다");
      });
  }, []);

  return (
    <div>
      <AppHeader />
      <main className="mx-auto flex max-w-[1120px] flex-col gap-10 px-6 pt-10 pb-16">
        {failed && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!failed && !data && <HomeSkeleton />}
        {data && (
          <>
            <PlanSection title="실행 중인 계획" plans={data.running} show="progress" empty="실행 중인 계획이 없습니다." />
            <PlanSection
              title="확정을 기다리는 계획"
              plans={data.reviewing}
              show="node_total"
              empty="검토 중인 계획이 없습니다."
            />
            <PlanSection
              title="최근 계획"
              plans={data.recentPlans}
              show="created"
              empty="아직 계획이 없습니다."
              action={<TextLink href="/plans" tone="secondary">전체 보기 →</TextLink>}
            />
            <section className="flex flex-col gap-3">
              <SectionHeader
                title="최근 지식"
                action={<TextLink href="/memories" tone="secondary">전체 보기 →</TextLink>}
              />
              {data.recentMemories.length === 0 ? (
                <EmptyState>아직 지식이 없습니다.</EmptyState>
              ) : (
                <div className="border-t border-border">
                  {data.recentMemories.map((memory) => (
                    <RecentMemoryRow key={memory.memory_id} memory={memory} />
                  ))}
                </div>
              )}
            </section>
            <section className="flex flex-wrap items-baseline gap-x-6 gap-y-2 border-t border-border-subtle pt-2">
              <span className="text-[13px] text-text-secondary">지식</span>
              <span className="text-[20px] font-bold tabular-nums">전체 {data.memoryTotal}개</span>
              <span className="text-text-secondary">
                지식 {data.kindCounts.knowledge} · 태도 {data.kindCounts.attitude} · 계획 {data.kindCounts.plan}
              </span>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
