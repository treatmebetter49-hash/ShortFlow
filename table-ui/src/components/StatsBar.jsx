function Stat({ label, value, accent, glow }) {
  return (
    <div className="flex flex-col items-start min-w-[68px]">
      <span className="text-[10.5px] uppercase tracking-[0.2em] text-white/40 font-semibold">
        {label}
      </span>
      <span
        className="text-[30px] leading-none font-semibold mt-2.5 tabular-nums tracking-[-0.03em]"
        style={accent ? { color: accent, textShadow: `0 0 26px ${glow}` } : undefined}
      >
        {value}
      </span>
    </div>
  );
}

export default function StatsBar() {
  return (
    <div className="glass px-6 py-5 flex items-stretch gap-7">
      <Stat label="Shorts"  value="30" />
      <span className="w-px bg-white/[0.08]" />
      <Stat label="Hooks"   value="30" />
      <span className="w-px bg-white/[0.08]" />
      <Stat label="Prompts" value="90" />
      <span className="w-px bg-white/[0.08]" />
      <Stat label="Fertig"  value="14" accent="#3ECF6E" glow="rgba(62,207,110,0.55)" />
    </div>
  );
}
