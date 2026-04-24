
import { Link } from 'react-router';
import { Search, Compass, LogIn } from 'lucide-react';
import { useStarStore } from '../../stores/starStore';

export default function Navbar() {
  const setCmdKOpen = useStarStore((state) => state.setCmdKOpen);


  return (
    <nav className="fixed top-0 left-0 w-full h-16 z-40 bg-background/50 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6">
      <div className="flex items-center gap-6">
        <Link to="/universe" className="text-xl font-bold tracking-widest text-brand-active hover:text-white transition-colors">
          ASTROPHAGE
        </Link>
        <button
          onClick={() => setCmdKOpen(true)}
          className="flex items-center gap-2 text-sm text-foreground/50 hover:text-foreground transition-colors bg-white/5 px-3 py-1.5 rounded-md border border-white/5 hover:border-white/20"
        >
          <Search size={16} />
          <span>Search stars...</span>
          <kbd className="ml-2 px-1.5 py-0.5 bg-white/10 rounded text-xs">⌘K</kbd>
        </button>
      </div>

      <div className="flex items-center gap-4 text-sm font-medium">
        <Link to="/explore" className="flex items-center gap-2 text-foreground/70 hover:text-white transition-colors">
          <Compass size={18} />
          <span>Explore</span>
        </Link>
        <Link to="/auth/login" className="flex items-center gap-2 bg-brand-active/20 text-brand-active hover:bg-brand-active/30 px-4 py-2 rounded-full transition-colors">
          <LogIn size={18} />
          <span>Login</span>
        </Link>
      </div>
    </nav>
  );
}
