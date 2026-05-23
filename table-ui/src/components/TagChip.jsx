export default function TagChip({ label, tone }) {
  const cls =
    tone === "mag" ? "chip chip-mag"
    : tone === "cy" ? "chip chip-cy"
    : "chip";
  return <span className={cls}>#{label}</span>;
}
