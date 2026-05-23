import { useState } from "react";
import { I } from "../icons";

export default function CopyButton({ value }) {
  const [copied, setCopied] = useState(false);

  const handleClick = (e) => {
    e.stopPropagation();
    try { navigator.clipboard?.writeText(value); } catch (_) {}
    setCopied(true);
    setTimeout(() => setCopied(false), 1100);
  };

  return (
    <button
      onClick={handleClick}
      className={"copy-btn " + (copied ? "copied" : "")}
      title="Kopieren"
    >
      {copied
        ? <I.Check className="w-3.5 h-3.5" />
        : <I.Copy className="w-3.5 h-3.5" />
      }
    </button>
  );
}
