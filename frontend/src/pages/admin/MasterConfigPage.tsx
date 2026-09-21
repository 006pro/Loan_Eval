import { useState } from "react";
import { DurationRulesTab } from "./master/DurationRulesTab";
import { ApprovalFeeRulesTab } from "./master/ApprovalFeeRulesTab";
import { LoanTypesTab } from "./master/LoanTypesTab";
import { RepaymentFrequenciesTab } from "./master/RepaymentFrequenciesTab";
import { PenaltyRulesTab } from "./master/PenaltyRulesTab";

const TABS = [
  { key: "loan-types", label: "Loan Types" },
  { key: "duration", label: "Duration Rules" },
  { key: "fees", label: "Approval Fee Rules" },
  { key: "frequencies", label: "Repayment Frequencies" },
  { key: "penalties", label: "Penalty Rules" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export function MasterConfigPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("loan-types");

  return (
    <div>
      <div className="page-header">
        <h1>Master Configuration</h1>
        <p>Configurable business rules. Changes apply to new applications and approvals only.</p>
      </div>

      <div className="panel">
        <div className="panel-header" style={{ gap: "0.4rem" }}>
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              className={activeTab === tab.key ? "btn btn-small" : "btn btn-secondary btn-small"}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "loan-types" && <LoanTypesTab />}
        {activeTab === "duration" && <DurationRulesTab />}
        {activeTab === "fees" && <ApprovalFeeRulesTab />}
        {activeTab === "frequencies" && <RepaymentFrequenciesTab />}
        {activeTab === "penalties" && <PenaltyRulesTab />}
      </div>
    </div>
  );
}
