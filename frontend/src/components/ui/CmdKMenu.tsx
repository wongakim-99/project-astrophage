import { useEffect } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router';
import { useStarStore } from '../../stores/starStore';

export default function CmdKMenu() {
  const { stars, isCmdKOpen, setCmdKOpen, selectStar } = useStarStore();
  const navigate = useNavigate();

  // Toggle the menu when ⌘K is pressed
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
      {/* Click outside to close */}
      <div className="absolute inset-0" onClick={() => setCmdKOpen(false)} />
      
      <div className="relative w-full max-w-lg bg-[#1A1A2E] rounded-xl border border-white/20 shadow-2xl overflow-hidden">
        <Command
          className="flex flex-col"
          shouldFilter={true}
        >
          <Command.Input
            autoFocus
            placeholder="Search for a star (concept)..."
            className="w-full px-4 py-4 bg-transparent text-white border-b border-white/10 outline-none text-lg placeholder:text-white/30"
          />
          <Command.List className="max-h-[300px] overflow-y-auto p-2 custom-scrollbar">
            <Command.Empty className="py-6 text-center text-white/50 text-sm">
              No stars found.
            </Command.Empty>

            <Command.Group heading="Your Universe">
              {stars.map((star) => (
                <Command.Item
                  key={star.id}
                  value={star.name}
                  onSelect={() => {
                    setCmdKOpen(false);
                    // Navigate to the galaxy if not already there, then select star
                    navigate(`/galaxy/${star.galaxyId}`);
                    selectStar(star.slug);
                  }}
                  className="flex items-center px-4 py-3 rounded-lg cursor-pointer aria-selected:bg-white/10 text-white/80 aria-selected:text-white transition-colors"
                >
                  <div 
                    className="w-3 h-3 rounded-full mr-3 shadow-[0_0_8px_rgba(255,255,255,0.5)]" 
                    style={{ backgroundColor: star.color, boxShadow: `0 0 10px ${star.color}` }}
                  />
                  <span>{star.name}</span>
                  <span className="ml-auto text-xs text-white/30">{star.isPublic ? 'Public' : 'Private'}</span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
