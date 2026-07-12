export default function TagChip({ label, tone }) {
  const cls =
    tone === "gold" ? "chip chip-gold"
    : tone === "silver" ? "chip chip-silver"
    : "chip";
  return <span className={cls}>#{label}</span>;
}
