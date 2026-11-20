"use client";

import type { ReactNode } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { NodeStatusMark } from "@/components/plan/NodeStatusMark";
import { PlanStatusMark } from "@/components/plan/PlanStatusMark";
import { Button } from "@/components/ui/Button";
import { Checkbox } from "@/components/ui/Checkbox";
import { EmptyState } from "@/components/ui/EmptyState";
import { LabeledDivider } from "@/components/ui/LabeledDivider";
import { Notice } from "@/components/ui/Notice";
import { PageHeading } from "@/components/ui/PageHeading";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { SelectField } from "@/components/ui/SelectField";
import { Table } from "@/components/ui/Table";
import { TableCell } from "@/components/ui/TableCell";
import { TableHeaderCell } from "@/components/ui/TableHeaderCell";
import { TableRow } from "@/components/ui/TableRow";
import { TextAreaField } from "@/components/ui/TextAreaField";
import { TextField } from "@/components/ui/TextField";
import { TextLink } from "@/components/ui/TextLink";

function Item({ name, children }: { name: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3 border-t border-border-subtle pt-4">
      <h2 className="m-0 font-mono text-[12px] text-text-tertiary">{name}</h2>
      <div className="flex flex-wrap items-center gap-3">{children}</div>
    </section>
  );
}

export function UiGalleryClient() {
  return (
    <div>
      <AppHeader current="memories" />
      <div className="mx-auto flex max-w-[1120px] flex-col gap-8 px-6 py-10">
        <PageHeading title="공용 컴포넌트" meta="docs/components-plan.md 순서" />

        <Item name="Button primary · outline · subtle / md · sm">
          <Button variant="primary">수정</Button>
          <Button variant="outline">삭제</Button>
          <Button variant="subtle">취소</Button>
          <Button variant="primary" size="sm">+ 새 페르소나</Button>
          <Button variant="outline" size="sm">명령서 보기 ▾</Button>
          <Button variant="primary" disabled>저장</Button>
        </Item>

        <Item name="TextLink default · secondary">
          <TextLink href="/plans/11">계획 11 →</TextLink>
          <TextLink href="/memories" tone="secondary">← 지식 목록</TextLink>
        </Item>

        <Item name="PageHeading">
          <div className="w-full">
            <PageHeading title="페르소나" meta="2개" actions={<Button variant="primary">+ 새 페르소나</Button>} />
          </div>
        </Item>

        <Item name="SectionHeader">
          <div className="w-full">
            <SectionHeader title="최근 계획" action={<TextLink href="/plans" tone="secondary">전체 보기 →</TextLink>} />
          </div>
        </Item>

        <Item name="EmptyState">
          <div className="w-full">
            <EmptyState>실행 중인 계획이 없습니다.</EmptyState>
          </div>
        </Item>

        <Item name="Notice">
          <div className="w-full">
            <Notice>지울 수 없습니다. 지식 7개, 계획 1개가 이 페르소나를 씁니다.</Notice>
          </div>
        </Item>

        <Item name="LabeledDivider">
          <div className="w-full">
            <LabeledDivider label="덧붙임 1" />
          </div>
        </Item>

        <Item name="TextField · SelectField · Checkbox">
          <TextField label="검색어 (작업 이름·본문)" placeholder="예: 테이블 설계" className="min-w-80 grow" />
          <SelectField label="종류" className="min-w-36">
            <option>전체</option>
            <option>지식</option>
            <option>태도</option>
            <option>계획</option>
          </SelectField>
          <Checkbox label="dankim-persona" defaultChecked />
          <Checkbox label="be-developer" />
        </Item>

        <Item name="TextAreaField">
          <TextAreaField
            label="본문 (덧붙임 머리는 그대로 둔다)"
            rows={4}
            className="w-full"
            defaultValue={"최소 스펙부터, 꼭 필요한 스펙만 나열한다.\n\n****** KNOWLEDGE APPENDED 1 ********\n원격 회고는 …"}
          />
        </Item>

        <Item name="Table · TableHeaderCell · TableRow(selected) · TableCell(tone)">
          <div className="w-full">
            <Table caption="페르소나 목록 예시">
              <thead>
                <tr>
                  <TableHeaderCell className="w-12">#</TableHeaderCell>
                  <TableHeaderCell className="w-52">이름</TableHeaderCell>
                  <TableHeaderCell>설명</TableHeaderCell>
                  <TableHeaderCell className="w-20">지식 수</TableHeaderCell>
                </tr>
              </thead>
              <tbody>
                <TableRow selected>
                  <TableCell tone="tertiary">1</TableCell>
                  <TableCell className="font-bold">dankim-persona</TableCell>
                  <TableCell tone="secondary">사용자의 기본 작업 역할</TableCell>
                  <TableCell>7</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell tone="tertiary">2</TableCell>
                  <TableCell>be-developer</TableCell>
                  <TableCell tone="secondary">백엔드 개발 역할</TableCell>
                  <TableCell>1</TableCell>
                </TableRow>
              </tbody>
            </Table>
          </div>
        </Item>

        <Item name="NodeStatusMark">
          <NodeStatusMark status="done" />
          <NodeStatusMark status="running" />
          <NodeStatusMark status="todo" />
          <NodeStatusMark status="failed" />
          <NodeStatusMark status="skipped" />
        </Item>

        <Item name="PlanStatusMark">
          <PlanStatusMark status="done" />
          <PlanStatusMark status="running" />
          <PlanStatusMark status="reviewing" />
          <PlanStatusMark status="approved" />
          <PlanStatusMark status="drafting" />
          <PlanStatusMark status="rejected" />
        </Item>
      </div>
    </div>
  );
}
