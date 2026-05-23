import { useState } from "react";
import { ROWS } from "../data/rows";
import { I } from "../icons";
import TableRow from "./TableRow";

const GRID = "48px 64px 1.05fr 1.45fr 1.05fr 1.35fr 1.1fr 130px";

function ColHeader({ label }) {
  return (
    <div className="px-3 text-[11px] uppercase tracking-[0.18em] font-semibold text-white/45">
      {label}
    </div>
  );
}

function TableHeader() {
  return (
    <div className="thead-bg sticky top-0 z-10">
      <div className="grid items-center h-11" style={{ gridTemplateColumns: GRID }}>
        <div className="flex items-center justify-center">
          <input type="checkbox" className="w-3.5 h-3.5 accent-white/40 bg-white/5 rounded" />
        </div>
        <ColHeader label="#" />
        <ColHeader label="Hook" />
        <ColHeader label="Text (für ElevenLabs)" />
        <ColHeader label="Titel" />
        <ColHeader label="Beschreibung" />
        <ColHeader label="Tags" />
        <ColHeader label="Status" />
      </div>
    </div>
  );
}

function Toolbar() {
  return (
    <div className="flex items-center justify-between px-1 py-1">
      <div className="flex items-center gap-2">
        <button className="tbtn">
          <I.Filter className="w-3.5 h-3.5 text-white/55" />
          <span>Filter</span>
        </button>
        <button className="tbtn">
          <I.Sort className="w-3.5 h-3.5 text-white/55" />
          <span>Sortieren</span>
        </button>
        <button className="tbtn">
          <I.Group className="w-3.5 h-3.5 text-white/55" />
          <span>Gruppieren</span>
        </button>
        <button className="tbtn">
          <I.Eye className="w-3.5 h-3.5 text-white/55" />
          <span>Ansicht</span>
        </button>
      </div>
      <div className="flex items-center gap-2">
        <button className="tbtn">
          <I.Download className="w-3.5 h-3.5 text-white/65" />
          <span>Export</span>
        </button>
        <div className="flex">
          <button
            className="tbtn tbtn-primary"
            style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0, paddingRight: 14 }}
          >
            <I.Plus className="w-3.5 h-3.5" />
            <span>Neuer Short</span>
          </button>
          <button
            className="tbtn tbtn-primary tbtn-icon"
            style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0, borderLeft: "1px solid rgba(255,255,255,0.18)" }}
          >
            <I.ChevronD className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

function Pagination({ count }) {
  return (
    <div
      className="grid grid-cols-3 items-center px-4 h-14 border-t border-white/[0.08]"
      style={{ background: "linear-gradient(180deg, rgba(255,255,255,0.018), transparent)" }}
    >
      <div className="flex items-center gap-3 text-[12.5px] text-white/55">
        <span>{count} Zeilen</span>
        <span className="text-white/20">·</span>
        <button className="tbtn" style={{ height: 30, padding: "0 10px" }}>
          20 pro Seite
          <I.ChevronD className="w-3 h-3 ml-1 text-white/40" />
        </button>
      </div>

      <div className="flex items-center justify-center gap-1">
        <button className="page-chip" title="Erste Seite">
          <I.ChevronL className="w-3.5 h-3.5" />
          <I.ChevronL className="w-3.5 h-3.5 -ml-2" />
        </button>
        <button className="page-chip">
          <I.ChevronL className="w-3.5 h-3.5" />
        </button>
        <button className="page-chip" aria-current="page">1</button>
        <button className="page-chip">
          <I.ChevronR className="w-3.5 h-3.5" />
        </button>
        <button className="page-chip" title="Letzte Seite">
          <I.ChevronR className="w-3.5 h-3.5" />
          <I.ChevronR className="w-3.5 h-3.5 -ml-2" />
        </button>
      </div>

      <div className="flex items-center justify-end gap-4 text-[12.5px] text-white/55">
        <span className="flex items-center gap-1.5">
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: "#3CDB8C", boxShadow: "0 0 8px rgba(60,219,140,0.7)" }}
          />
          Live
        </span>
        <span className="flex items-center gap-1.5 text-white/45">
          <I.Check className="w-3 h-3" />
          Auto-Save aktiv
        </span>
      </div>
    </div>
  );
}

export default function ContentTable() {
  const [selected, setSelected] = useState(new Set([3]));

  const toggle = (id) =>
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  return (
    <section className="glass flex-1 flex flex-col overflow-hidden">
      <div className="px-3 pt-3">
        <Toolbar />
      </div>

      <div className="mt-3 border-t border-white/[0.08]">
        <div className="overflow-x-auto">
          <div style={{ minWidth: 1100 }}>
            <TableHeader />
            <div>
              {ROWS.map((row) => (
                <TableRow
                  key={row.id}
                  row={row}
                  selected={selected.has(row.id)}
                  onToggle={() => toggle(row.id)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <Pagination count={ROWS.length} />
    </section>
  );
}
