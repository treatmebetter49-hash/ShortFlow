import { STATUS_META } from "../data/rows";
import { I } from "../icons";

export default function StatusBadge({ status }) {
  const m = STATUS_META[status] || STATUS_META.idea;
  return (
    <span className="pill" style={{ color: "rgba(255,255,255,0.9)" }}>
      <I.Check className="w-3 h-3" style={{ color: m.color }} />
      <span>{m.label}</span>
    </span>
  );
}
