import { I } from "../icons";
import StatsBar from "./StatsBar";

export default function Header() {
  return (
    <div className="flex items-start gap-4">
      {/* Title card */}
      <div className="glass flex-1 px-7 py-6 flex flex-col gap-5">
        <h1 className="text-[30px] leading-[1.08] font-semibold tracking-[-0.025em] text-white">
          Thema: Natur{" "}
          <span className="text-white/30 font-normal">–</span>{" "}
          Unglaubliche Geheimnisse{" "}
          <span className="text-emerald-400/90 ml-1">🌿</span>
        </h1>
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="meta-chip">
            <I.Calendar className="w-3.5 h-3.5 text-white/55" />
            Erstellt am 11.05.2025
          </span>
          <span className="meta-chip">
            <I.Grid className="w-3.5 h-3.5 text-white/55" />
            Anzahl Shorts: 30
          </span>
          <span className="meta-chip">
            <I.Plus className="w-3.5 h-3.5 text-white/55" />
            Erstellt mit: ShortFlow v1.0
          </span>
        </div>
      </div>

      <StatsBar />
    </div>
  );
}
