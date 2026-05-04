import { useNavigate } from 'react-router';
import { ArrowRight, Compass, LogIn, Sparkles } from 'lucide-react';
import { usePublicStars } from '../hooks/useStars';
import { useAuthStore } from '../stores/authStore';
import { LIFECYCLE_STYLE } from '../types/api';

export default function PublicUniversePage() {
  const { data: stars = [], isLoading, isError } = usePublicStars();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();

  return (
    <div className="h-full w-full overflow-y-auto bg-[#050510] p-6 text-white custom-scrollbar">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="border-b border-white/[0.08] pb-5">
          <p className="mb-2 text-[10px] font-mono uppercase tracking-[0.24em] text-white/30">public universes</p>
          <h1 className="text-2xl font-mono font-semibold tracking-wide text-white/90">우주 탐색</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-white/45">
            공개로 열려 있는 다른 사용자의 지식 베이스를 둘러봅니다.
          </p>
        </header>

        {!isAuthenticated && (
          <div className="flex items-center justify-between gap-4 rounded-lg border border-[#A8D8FF]/20 bg-[#A8D8FF]/[0.05] px-5 py-4">
            <div className="flex items-center gap-3 min-w-0">
              <Sparkles size={15} className="shrink-0 text-[#A8D8FF]/70" />
              <p className="text-sm text-white/60 truncate">
                나만의 우주를 만들고, 지식을 항성으로 쌓아보세요.
              </p>
            </div>
            <button
              onClick={() => navigate('/auth/login')}
              className="flex shrink-0 items-center gap-2 rounded-md border border-white/[0.14] px-3 py-1.5 text-xs font-mono text-white/70 transition-colors hover:border-white/[0.28] hover:text-white"
            >
              <LogIn size={13} />
              로그인
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="py-20 text-center text-sm font-mono text-white/35">loading...</div>
        ) : isError ? (
          <EmptyPublicState
            title="공개 우주를 불러오지 못했습니다"
            description="잠시 후 다시 시도해주세요."
          />
        ) : stars.length === 0 ? (
          <EmptyPublicState
            title="아직 공개된 지식이 없습니다"
            description="누군가 공개로 설정한 지식이 생기면 이곳에 표시됩니다."
          />
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            {stars.map((star) => {
              const style = LIFECYCLE_STYLE[star.lifecycle_state];
              return (
                <button
                  key={star.id}
                  onClick={() => navigate(`/${star.username}/stars/${star.slug}`)}
                  className="group rounded-lg border border-white/[0.08] bg-white/[0.03] p-4 text-left transition-colors hover:border-white/[0.18] hover:bg-white/[0.06]"
                >
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="mb-1 text-[11px] font-mono text-white/35">@{star.username}</p>
                      <h2 className="truncate text-base font-mono font-medium" style={{ color: style.color }}>
                        {star.title}
                      </h2>
                    </div>
                    <Compass size={16} className="mt-0.5 shrink-0 text-white/25 transition-colors group-hover:text-[#A8D8FF]/70" />
                  </div>
                  <p className="line-clamp-3 min-h-16 text-sm leading-5 text-white/45">
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

function EmptyPublicState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-white/[0.03] px-6 py-16 text-center">
      <h2 className="text-base font-mono font-medium text-white/75">{title}</h2>
      <p className="mt-2 text-sm text-white/40">{description}</p>
    </div>
  );
}
