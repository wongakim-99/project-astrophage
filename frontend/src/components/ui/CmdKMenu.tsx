import { useEffect } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router';
import { useStarStore } from '../../stores/starStore';
import { useAuthStore } from '../../stores/authStore';

export default function CmdKMenu() {
  const { isCmdKOpen, setCmdKOpen } = useStarStore();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCmdKOpen(!isCmdKOpen);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [isCmdKOpen, setCmdKOpen]);

  if (!isCmdKOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-black/60 backdrop-blur-sm">
      <div className="absolute inset-0" onClick={() => setCmdKOpen(false)} />
      <div className="relative w-full max-w-lg bg-[#1A1A2E] rounded-xl border border-white/20 shadow-2xl overflow-hidden">
        <Command className="flex flex-col" shouldFilter={true}>
          <Command.Input
            autoFocus
            placeholder="Search for a star (concept)..."
            className="w-full px-4 py-4 bg-transparent text-white border-b border-white/10 outline-none text-lg placeholder:text-white/30"
          />
          <Command.List className="max-h-[300px] overflow-y-auto p-2 custom-scrollbar">
            <Command.Empty className="py-6 text-center text-white/50 text-sm">
              No stars found.
            </Command.Empty>
            <Command.Group heading="검색">
              <Command.Item
                value="explore"
                onSelect={() => {
                  setCmdKOpen(false);
                  navigate(isAuthenticated ? '/explore' : '/auth/login');
                }}
                className="flex items-center px-4 py-3 rounded-lg cursor-pointer aria-selected:bg-white/10 text-white/80 aria-selected:text-white transition-colors"
              >
                <span>Explore 내 지식 탐색</span>
              </Command.Item>
              <Command.Item
                value="universes"
                onSelect={() => { setCmdKOpen(false); navigate('/universes'); }}
                className="flex items-center px-4 py-3 rounded-lg cursor-pointer aria-selected:bg-white/10 text-white/80 aria-selected:text-white transition-colors"
              >
                <span>우주 탐색 공개 지식</span>
              </Command.Item>
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
