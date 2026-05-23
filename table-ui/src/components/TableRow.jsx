import CopyButton from "./CopyButton";
import StatusBadge from "./StatusBadge";
import TagChip from "./TagChip";

const GRID = "48px 64px 1.05fr 1.45fr 1.05fr 1.35fr 1.1fr 130px";

export default function TableRow({ row, selected, onToggle }) {
  return (
    <div
      className="row grid items-stretch group"
      style={{ gridTemplateColumns: GRID, minHeight: 92 }}
      data-selected={selected ? "true" : "false"}
    >
      {/* Checkbox */}
      <div className="flex items-center justify-center">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="w-3.5 h-3.5 accent-pink-500 bg-white/5 rounded"
        />
      </div>

      {/* Index */}
      <div className="px-3 flex items-center">
        <span className="font-mono text-[12.5px] tabular-nums text-white/45 group-hover:text-white/75 transition">
          {String(row.id).padStart(2, "0")}
        </span>
      </div>

      {/* Hook */}
      <div className="px-3 py-3 cell-editable rounded-md flex items-center">
        <div className="text-[14px] leading-[1.35] text-white font-medium tracking-[-0.005em] truncate-3">
          {row.hook}
        </div>
      </div>

      {/* Text */}
      <div className="px-3 py-3 cell-editable rounded-md flex items-start gap-2.5">
        <div className="min-w-0 flex-1 text-[12.5px] leading-[1.5] text-white/80 truncate-3">
          {row.text}
        </div>
        <CopyButton value={row.text} />
      </div>

      {/* Titel */}
      <div className="px-3 py-3 cell-editable rounded-md flex items-start gap-2.5">
        <div className="min-w-0 flex-1 text-[13.5px] leading-[1.35] text-white font-medium tracking-[-0.005em] truncate-3">
          {row.title}
        </div>
        <CopyButton value={row.title} />
      </div>

      {/* Beschreibung */}
      <div className="px-3 py-3 cell-editable rounded-md flex items-start gap-2.5">
        <div className="min-w-0 flex-1 text-[12.5px] leading-[1.5] text-white/[0.78] truncate-3">
          {row.desc}
        </div>
        <CopyButton value={row.desc} />
      </div>

      {/* Tags */}
      <div className="px-3 py-3 flex flex-wrap items-start content-start gap-1.5">
        {row.tags.map((tag, i) => (
          <TagChip key={tag} label={tag} tone={i % 2 === 0 ? "mag" : "cy"} />
        ))}
      </div>

      {/* Status */}
      <div className="px-3 py-3 flex items-center">
        <StatusBadge status={row.status} />
      </div>
    </div>
  );
}
