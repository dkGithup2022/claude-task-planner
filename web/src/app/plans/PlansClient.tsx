"use client";

import { useEffect, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { PlanTableRow } from "@/components/plan/PlanTableRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { Notice } from "@/components/ui/Notice";
import { PageHeading } from "@/components/ui/PageHeading";
import { Table } from "@/components/ui/Table";
import { TableHeaderCell } from "@/components/ui/TableHeaderCell";
import { showErrorToast } from "@/lib/api/error-toast";
import { fetchPlans } from "@/lib/plan-api";
import type { PlanSummary } from "@/types/data/domain/plan";
import { PlansSkeleton } from "./PlansSkeleton";

export function PlansClient() {
  const [plans, setPlans] = useState<PlanSummary[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    fetchPlans()
      .then((res) => setPlans(res.plans))
      .catch((err) => {
        setFailed(true);
        showErrorToast(err, "계획 목록을 불러오지 못했습니다");
      });
  }, []);

  return (
    <div>
      <AppHeader current="plans" />
      <main className="mx-auto flex max-w-[1120px] flex-col gap-4 px-6 pt-10 pb-16">
        <PageHeading
          title="계획"
          meta={`최근 것부터 (만든 시각 기준)${plans ? ` · ${plans.length}개` : ""}`}
        />
        {failed && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!failed && !plans && <PlansSkeleton />}
        {plans && plans.length === 0 && <EmptyState>아직 계획이 없습니다.</EmptyState>}
        {plans && plans.length > 0 && (
          <Table minWidth={760} caption="계획 목록">
            <thead>
              <tr>
                <TableHeaderCell className="w-14">계획</TableHeaderCell>
                <TableHeaderCell>제목</TableHeaderCell>
                <TableHeaderCell className="w-28">상태</TableHeaderCell>
                <TableHeaderCell className="w-30">노드</TableHeaderCell>
                <TableHeaderCell className="w-30">만든 시각</TableHeaderCell>
              </tr>
            </thead>
            <tbody>
              {plans.map((plan) => (
                <PlanTableRow key={plan.plan_id} plan={plan} />
              ))}
            </tbody>
          </Table>
        )}
        <p className="mt-2 mb-0 text-[13px] text-text-tertiary">
          상태 표시: ● 완료 · ◐ 실행 중 · ○ 검토 중·승인·만드는 중 · – 불허. 노드 열은 끝난 노드/전체 노드이고, 실패한
          노드가 있으면 &quot;6/9 (실패 1)&quot; 처럼 적는다.
        </p>
      </main>
    </div>
  );
}
