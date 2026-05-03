
import { Link } from 'react-router';
import { Search, Compass, LogIn } from 'lucide-react';
import { useStarStore } from '../../stores/starStore';

export default function Navbar() {
  const setCmdKOpen = useStarStore((state) => state.setCmdKOpen);

  return (
    <nav className="fixed top-0 left-0 w-full h-16 z-40 bg-[#050510]/90 backdrop-blur-xl border-b border-white/[0.08] flex items-center justify-between px-6">
      <div className="flex items-center gap-5">
        <Link
          to="/universe"
          className="text-lg font-mono font-bold tracking-[0.18em] text-white/85 hover:text-white transition-colors"
        >
          ASTROPHAGE
        </Link>
        <button
          onClick={() => setCmdKOpen(true)}
          className="flex items-center gap-2 text-sm font-mono text-white/55 hover:text-white/80 transition-colors bg-white/[0.05] hover:bg-white/[0.09] px-3 py-1.5 rounded border border-white/[0.12] hover:border-white/[0.22]"
        >
          <Search size={13} />
          <span>Search stars...</span>
          <kbd className="ml-1 px-1.5 py-0.5 bg-white/[0.08] rounded text-[10px] text-white/50">⌘K</kbd>
        </button>
      </div>

      <div className="flex items-center gap-3 text-sm font-mono">
        <Link
          to="/explore"
          className="flex items-center gap-1.5 text-white/60 hover:text-white/90 transition-colors"
        >
          <Compass size={14} />
          <span>explore</span>
        </Link>
        <Link
          to="/auth/register"
          className="flex items-center gap-1.5 text-white/55 hover:text-white/85 px-3 py-1.5 rounded border border-white/[0.12] hover:border-white/[0.25] transition-colors"
        >
          <span>회원가입</span>
        </Link>
        <Link
          to="/auth/login"
          className="flex items-center gap-1.5 bg-white/[0.07] hover:bg-white/[0.12] text-white/70 hover:text-white/95 px-3 py-1.5 rounded border border-white/[0.15] hover:border-white/[0.30] transition-colors"
        >
          <LogIn size={13} />
          <span>login</span>
        </Link>
      </div>
    </nav>
  );
}
