import { I } from "../icons";

const NAV_ITEMS = [
  { icon: I.Home,     label: "Übersicht",    active: true },
  { icon: I.Layers,   label: "Themen" },
  { icon: I.Bulb,     label: "Ideen" },
  { icon: I.Play,     label: "Shorts" },
  { icon: I.Calendar, label: "Calendar" },
];

const MORE_ITEMS = [
  { icon: I.Cog,      label: "Einstellungen" },
  { icon: I.Doc,      label: "Vorlagen" },
  { icon: I.Download, label: "Exports" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar-plate w-[232px] shrink-0 flex flex-col py-2 pr-2 pl-2">
      {/* Brand */}
      <div className="flex flex-col items-center text-center pt-2 pb-5">
        <div
          className="w-[72px] h-[72px] rounded-[20px] flex items-center justify-center text-[32px] font-bold"
          style={{
            background: "radial-gradient(120% 80% at 30% 20%, rgba(255,61,138,0.7), transparent 55%), radial-gradient(120% 80% at 70% 90%, rgba(38,215,244,0.7), transparent 55%), linear-gradient(160deg, #18181f, #08080c)",
            border: "1px solid rgba(255,255,255,0.14)",
            boxShadow: "inset 0 1px 0 rgba(255,255,255,0.18), 0 8px 24px -10px rgba(255,61,138,0.5), 0 8px 24px -10px rgba(38,215,244,0.5)",
          }}
        >
          <span style={{ background: "linear-gradient(180deg,#FFB0CC,#9BEAF7)", WebkitBackgroundClip: "text", backgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            S
          </span>
        </div>
        <div className="mt-3 text-[18px] font-semibold tracking-[-0.02em]">ShortFlow</div>
        <div className="mt-1 text-[11.5px] text-white/45 tracking-[0.02em]">Ideen. Inhalte. Shorts. Fertig.</div>
      </div>

      <div className="h-px bg-white/[0.08] mx-2 mb-3" />

      <nav className="flex flex-col gap-1 px-1">
        {NAV_ITEMS.map((item) => (
          <a
            key={item.label}
            className="nav-item"
            aria-current={item.active ? "page" : undefined}
          >
            <item.icon className="w-[18px] h-[18px]" />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <div className="h-px bg-white/[0.08] mx-2 my-3" />

      <nav className="flex flex-col gap-1 px-1">
        {MORE_ITEMS.map((item) => (
          <a key={item.label} className="nav-item">
            <item.icon className="w-[18px] h-[18px]" />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <div className="mt-auto" />

      {/* Plan card */}
      <div className="glass mx-1 px-3 py-3 mt-3 flex items-center gap-3" style={{ borderRadius: 14 }}>
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-[15px] font-bold shrink-0"
          style={{
            background: "radial-gradient(120% 80% at 30% 20%, rgba(255,61,138,0.6), transparent 55%), radial-gradient(120% 80% at 70% 90%, rgba(38,215,244,0.6), transparent 55%), linear-gradient(160deg, #18181f, #08080c)",
            border: "1px solid rgba(255,255,255,0.12)",
          }}
        >
          <span style={{ background: "linear-gradient(180deg,#FFB0CC,#9BEAF7)", WebkitBackgroundClip: "text", backgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            S
          </span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[13.5px] font-semibold leading-tight">ShortFlow</div>
          <div className="text-[11px] text-white/55 mt-0.5 flex items-center gap-1.5">
            Pro Plan
            <span className="inline-block w-1 h-1 rounded-full bg-white/30" />
            Aktiv
          </div>
        </div>
        <button className="w-7 h-7 rounded-md hover:bg-white/5 flex items-center justify-center text-white/55">
          <I.ChevronR className="w-3.5 h-3.5" />
        </button>
      </div>
    </aside>
  );
}
