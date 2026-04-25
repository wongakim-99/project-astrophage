
import { useNavigate } from 'react-router';
import { useStarStore } from '../stores/starStore';

export default function ExplorePage() {
  const stars = useStarStore((state) => state.stars);
  const publicStars = stars.filter(s => s.isPublic);
  const navigate = useNavigate();

  return (
    <div className="w-full h-full p-8 overflow-y-auto custom-scrollbar relative bg-background">
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-active/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-fading/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-brand-active to-brand-normal drop-shadow-sm">
            EXPLORE THE UNIVERSE
          </h1>
          <p className="text-lg opacity-70">Discover knowledge across all public stars.</p>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {publicStars.map((star) => (
            <div 
              key={star.id}
              onClick={() => navigate(`/user/stars/${star.slug}`)} // dummy user
              className="group p-6 bg-[#0A0A15]/60 backdrop-blur-md border border-white/10 rounded-2xl hover:border-white/30 transition-all duration-300 cursor-pointer hover:shadow-[0_0_30px_rgba(255,255,255,0.05)] hover:-translate-y-1"
            >
              <div className="flex items-start justify-between mb-4">
                <div 
                  className="w-3 h-3 rounded-full mt-1.5 transition-transform duration-300 group-hover:scale-150 group-hover:shadow-[0_0_15px_rgba(255,255,255,0.8)]" 
                  style={{ backgroundColor: star.color, boxShadow: `0 0 8px ${star.color}` }}
                />
                <span className="text-xs px-2 py-1 bg-white/5 rounded-full text-white/50 group-hover:text-white/80 transition-colors">
                  Energy: {Math.floor(star.size * 100)}
                </span>
              </div>
              <h2 className="text-xl font-bold mb-2 group-hover:text-brand-active transition-colors line-clamp-1" style={{ color: star.color }}>
                {star.name}
              </h2>
              <p className="text-sm opacity-50 mb-4">@user</p>
              
              <div className="text-sm text-foreground/70 line-clamp-2">
                {star.content?.replace(/^#.*$/m, '') || 'No description provided.'}
              </div>
            </div>
          ))}

          {publicStars.length === 0 && (
            <div className="col-span-full py-20 text-center text-white/40">
              No public stars found in the universe yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
