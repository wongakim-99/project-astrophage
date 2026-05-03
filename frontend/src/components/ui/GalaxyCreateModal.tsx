import { useState } from 'react';
import { X } from 'lucide-react';
import { GALAXY_COLOR_PALETTE } from '../../stores/galaxyStore';
import { useCreateGalaxy } from '../../hooks/useGalaxies';

interface GalaxyCreateModalProps {
  onClose: () => void;
  onCreated?: (galaxyId: string) => void;
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 100);
}

export default function GalaxyCreateModal({ onClose, onCreated }: GalaxyCreateModalProps) {
  const { mutateAsync: createGalaxy, isPending } = useCreateGalaxy();

  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [color, setColor] = useState(GALAXY_COLOR_PALETTE[0]);
  const [error, setError] = useState('');

  const handleNameChange = (value: string) => {
    setName(value);
    setSlug(slugify(value));
  };

  const handleCreate = async () => {
    if (!name.trim() || !slug.trim()) return;
    setError('');
    try {
      const galaxy = await createGalaxy({ name: name.trim(), slug, color });
      onCreated?.(galaxy.id);
      onClose();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? '은하 생성에 실패했습니다.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="relative w-full max-w-sm bg-[#0D0D20] border border-white/10 rounded-2xl shadow-2xl p-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-white/35 hover:text-white/70 hover:bg-white/[0.06] rounded transition-colors"
        >
          <X size={16} />
        </button>

        <h2 className="text-base font-mono font-medium text-white/90 mb-1 tracking-wider">새 은하 만들기</h2>
        <p className="text-xs font-mono text-white/35 mb-6">지식을 담을 새로운 은하를 생성합니다</p>

        <div className="flex flex-col gap-5">
          <div>
            <label className="block text-xs font-semibold text-white/65 mb-1.5">은하 이름</label>
            <input
              type="text"
              placeholder="Machine Learning"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              autoFocus
              className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-white/65 mb-1.5">슬러그</label>
            <input
              type="text"
              value={slug}
              onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
              className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white/70 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-white/65 mb-2">은하 색상</label>
            <div className="flex gap-2.5">
              {GALAXY_COLOR_PALETTE.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className="w-7 h-7 rounded-full transition-transform hover:scale-110"
                  style={{
                    backgroundColor: c,
                    boxShadow: color === c ? `0 0 0 2px #0D0D20, 0 0 0 4px ${c}` : 'none',
                  }}
                />
              ))}
            </div>
          </div>

          <div
            className="flex items-center gap-3 px-4 py-3 rounded-lg border"
            style={{ borderColor: `${color}30`, background: `${color}08` }}
          >
            <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }} />
            <span className="text-sm font-mono" style={{ color }}>{name || '은하 이름'}</span>
          </div>

          {error && <p className="text-xs text-red-400/80 font-mono text-center">{error}</p>}

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 rounded-lg border border-white/10 text-white/50 hover:text-white/75 hover:border-white/20 text-sm font-mono transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleCreate}
              disabled={!name.trim() || !slug.trim() || isPending}
              className="flex-1 py-2.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isPending ? '생성 중...' : '만들기'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
