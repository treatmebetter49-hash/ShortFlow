const Ic = ({ children, className = "w-4 h-4", strokeWidth = 1.5 }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    {children}
  </svg>
);

export const I = {
  Home:     (p) => <Ic {...p}><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-4v-6h-6v6H5a1 1 0 0 1-1-1z"/></Ic>,
  Layers:   (p) => <Ic {...p}><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/></Ic>,
  Bulb:     (p) => <Ic {...p}><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3Z"/></Ic>,
  Play:     (p) => <Ic {...p}><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M11 9.5v5l4-2.5z" fill="currentColor" stroke="none"/></Ic>,
  Calendar: (p) => <Ic {...p}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M8 3v4M16 3v4"/></Ic>,
  Cog:      (p) => <Ic {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.7 1.7 0 0 0 9 4.6 1.7 1.7 0 0 0 10 3.1V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.7 1.7 0 0 0 19.4 9c.2.6.7 1 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/></Ic>,
  Doc:      (p) => <Ic {...p}><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/></Ic>,
  Download: (p) => <Ic {...p}><path d="M12 3v12m0 0-4-4m4 4 4-4M5 21h14"/></Ic>,
  ChevronR: (p) => <Ic {...p}><path d="m9 6 6 6-6 6"/></Ic>,
  ChevronL: (p) => <Ic {...p}><path d="m15 6-6 6 6 6"/></Ic>,
  ChevronD: (p) => <Ic {...p}><path d="m6 9 6 6 6-6"/></Ic>,
  Filter:   (p) => <Ic {...p}><path d="M3 5h18M6 12h12M10 19h4"/></Ic>,
  Sort:     (p) => <Ic {...p}><path d="M7 4v16m0 0-3-3m3 3 3-3M17 20V4m0 0-3 3m3-3 3 3"/></Ic>,
  Group:    (p) => <Ic {...p}><rect x="3" y="4" width="18" height="5" rx="1.5"/><rect x="3" y="11" width="11" height="3" rx="1"/><rect x="3" y="16" width="14" height="3" rx="1"/></Ic>,
  Eye:      (p) => <Ic {...p}><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></Ic>,
  Plus:     (p) => <Ic {...p}><path d="M12 5v14M5 12h14"/></Ic>,
  Copy:     (p) => <Ic {...p}><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/></Ic>,
  Check:    (p) => <Ic {...p}><path d="m4 12 5 5L20 6"/></Ic>,
  Grid:     (p) => <Ic {...p}><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></Ic>,
};
