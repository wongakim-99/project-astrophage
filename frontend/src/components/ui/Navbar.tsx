
import { Link } from 'react-router';
import { Search, Compass, LogIn } from 'lucide-react';
import { useStarStore } from '../../stores/starStore';

export default function Navbar() {
  const setCmdKOpen = useStarStore((state) => state.setCmdKOpen);


  return (
    <nav className="fixed top-0 left-0 w-full h-16 z-40 bg-[#050510]/90 backdrop-blur-xl border-b border-white/[0.04] flex items-center justify-between px-6">
      <div className="flex items-center gap-5">
        <Link
          to="/universe"
          className="text-sm font-mono font-medium tracking-[0.18em] text-white/60 hover:text-white/90 transition-colors"
        >
          ASTROPHAGE
        </Link>
        <button
          onClick={() => setCmdKOpen(true)}
          className="flex items-center gap-2 text-[11px] font-mono text-white/25 hover:text-white/55 transition-colors bg-white/[0.03] hover:bg-white/[0.05] px-3 py-1.5 rounded border border-white/[0.06] hover:border-white/[0.12]"
        >
          <Search size={13} />
          <span>Search stars...</span>
          <kbd className="ml-1 px-1.5 py-0.5 bg-white/[0.06] rounded text-[9px]">⌘K</kbd>
        </button>
      </div>

      <div className="flex items-center gap-3 text-[11px] font-mono">
        <Link
          to="/explore"
          className="flex items-center gap-1.5 text-white/30 hover:text-white/60 transition-colors"
        >
          <Compass size={14} />
          <span>explore</span>
        </Link>
        <Link
          to="/auth/login"
          className="flex items-center gap-1.5 text-white/35 hover:text-white/65 px-3 py-1.5 rounded border border-white/[0.08] hover:border-white/[0.18] transition-colors"
        >
          <LogIn size={13} />
          <span>login</span>
        </Link>
      </div>
    </nav>
  );
}
