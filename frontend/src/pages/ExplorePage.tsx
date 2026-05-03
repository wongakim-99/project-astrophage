import { useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router';
import { ArrowRight, Search } from 'lucide-react';
import { useGalaxies } from '../hooks/useGalaxies';
import { useAllGalaxyStars } from '../hooks/useStars';
import { useAuthStore } from '../stores/authStore';
import { LIFECYCLE_STYLE } from '../types/api';

type VisibilityFilter = 'all' | 'public' | 'private';

export default function ExplorePage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitialized = useAuthStore((s) => s.isInitialized);
  const { data: galaxies = [], isLoading: isGalaxiesLoading } = useGalaxies();
  const { stars, isLoading: isStarsLoading } = useAllGalaxyStars(galaxies);
  const navigate = useNavigate();

  const [query, setQuery] = useState('');
  const [visibility, setVisibility] = useState<VisibilityFilter>('all');

  const filteredStars = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return stars.filter((star) => {
      const matchesVisibility =
        visibility === 'all' ||
        (visibility === 'public' && star.is_public) ||
        (visibility === 'private' && !star.is_public);

      if (!matchesVisibility) return false;
      if (!normalizedQuery) return true;

      return [
        star.title,
        star.slug,
        star.content,
        star.galaxy.name,
      ].some((value) => value.toLowerCase().includes(normalizedQuery));
    });
  }, [query, stars, visibility]);

  if (!isInitialized) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-[#050510] text-sm font-mono text-white/35">
        loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  const isLoading = isGalaxiesLoading || isStarsLoading;

  return (
    <div className="h-full w-full overflow-y-auto bg-[#050510] p-6 text-white custom-scrollbar">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-white/[0.08] pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-2 text-[10px] font-mono uppercase tracking-[0.24em] text-white/30">explore</p>
            <h1 className="text-2xl font-mono font-semibold tracking-wide text-white/90">내 지식 탐색</h1>
            <p className="mt-2 text-sm text-white/45">내 은하에 쌓인 지식을 한곳에서 훑어보고 이동합니다.</p>
          </div>

          <div className="flex rounded-lg border border-white/[0.1] bg-white/[0.03] p-1">
            {(['all', 'public', 'private'] as const).map((item) => (
              <button
                key={item}
                onClick={() => setVisibility(item)}
                className={`rounded-md px-3 py-1.5 text-xs font-mono transition-colors ${
                  visibility === item
                    ? 'bg-[#A8D8FF] text-[#050510]'
                    : 'text-white/45 hover:bg-white/[0.05] hover:text-white/75'
                }`}
              >
                {item === 'all' ? '전체' : item === 'public' ? '공개' : '비공개'}
              </button>
            ))}
          </div>
        </header>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={16} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="제목, 슬러그, 은하, 내용으로 검색"
            className="w-full rounded-lg border border-white/[0.1] bg-black/35 py-3 pl-10 pr-4 text-sm text-white outline-none transition-colors placeholder:text-white/25 focus:border-[#A8D8FF]/55"
          />
        </div>

        {isLoading ? (
          <div className="py-20 text-center text-sm font-mono text-white/35">loading...</div>
        ) : galaxies.length === 0 ? (
          <EmptyState
            title="아직 생성된 은하가 없습니다"
            description="내 지식 탐색은 은하와 항성이 생긴 뒤 사용할 수 있습니다."
            action="내 우주로 이동"
            onAction={() => navigate('/universe')}
          />
        ) : stars.length === 0 ? (
          <EmptyState
            title="아직 추가된 지식이 없습니다"
            description="은하 안에 첫 지식을 추가하면 이곳에서 모아볼 수 있습니다."
            action="내 우주로 이동"
            onAction={() => navigate('/universe')}
          />
        ) : filteredStars.length === 0 ? (
          <EmptyState
            title="검색 결과가 없습니다"
            description="검색어 또는 공개 상태 필터를 조정해보세요."
          />
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            {filteredStars.map((star) => {
              const style = LIFECYCLE_STYLE[star.lifecycle_state];
              return (
                <button
                  key={star.id}
                  onClick={() => navigate(`/galaxy/${star.galaxy_id}`)}
                  className="group rounded-lg border border-white/[0.08] bg-white/[0.03] p-4 text-left transition-colors hover:border-white/[0.18] hover:bg-white/[0.06]"
                >
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="mb-1 flex items-center gap-2 text-[11px] font-mono text-white/35">
                        <span className="h-2 w-2 rounded-full" style={{ backgroundColor: star.galaxy.color }} />
                        <span className="truncate">{star.galaxy.name}</span>
                      </p>
                      <h2 className="truncate text-base font-mono font-medium" style={{ color: style.color }}>
                        {star.title}
                      </h2>
                    </div>
                    <span className={`shrink-0 rounded px-2 py-1 text-[10px] font-mono ${
                      star.is_public ? 'bg-[#A8D8FF]/15 text-[#A8D8FF]' : 'bg-white/[0.06] text-white/45'
                    }`}>
                      {star.is_public ? 'public' : 'private'}
                    </span>
                  </div>
                  <p className="line-clamp-2 min-h-10 text-sm leading-5 text-white/45">
                    {star.content || '내용 없음'}
                  </p>
                  <div className="mt-4 flex items-center justify-between text-[11px] font-mono text-white/30">
                    <span className="truncate">{star.slug}</span>
                    <ArrowRight size={13} className="transition-transform group-hover:translate-x-0.5" />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState({
  title,
  description,
  action,
  onAction,
}: {
  title: string;
  description: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-white/[0.03] px-6 py-14 text-center">
      <h2 className="text-base font-mono font-medium text-white/75">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-white/40">{description}</p>
      {action && onAction && (
        <button
          onClick={onAction}
          className="mt-5 rounded-lg bg-[#A8D8FF] px-4 py-2 text-sm font-bold text-[#050510] transition-colors hover:bg-[#A8D8FF]/90"
        >
          {action}
        </button>
      )}
    </div>
  );
}
