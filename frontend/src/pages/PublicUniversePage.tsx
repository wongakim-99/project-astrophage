import { useNavigate } from 'react-router';
import { ArrowRight, Compass, LogIn, Orbit, Sparkles, Clock } from 'lucide-react';
import { usePublicStars } from '../hooks/useStars';
import { useAuthStore } from '../stores/authStore';
import { LIFECYCLE_STYLE } from '../types/api';

export default function PublicUniversePage() {
  const { data: stars = [], isLoading, isError } = usePublicStars();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();

  return (
    <div className="h-full w-full overflow-y-auto bg-[#050510] text-white custom-scrollbar">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-8">

        {/* ── 히어로 섹션 (비로그인 전용) ── */}
        {!isAuthenticated && (
          <section className="flex flex-col gap-8 border-b border-white/[0.07] pb-10">
            <div className="flex flex-col gap-4">
              <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-white/25">
                project astrophage
              </p>
              <h1 className="text-3xl font-mono font-semibold leading-snug tracking-wide text-white/90">
                잊혀진 지식은<br />
                <span style={{ color: '#A8D8FF' }}>암흑 물질</span>이 된다
              </h1>
              <p className="max-w-xl text-sm leading-7 text-white/45">
                인간의 뉴런 구조와 우주 구조는 닮아있다. 지식을 항성으로 쌓고, 복습할수록 빛난다. 방치하면 서서히 어두워지고, 결국 암흑 물질이 된다.
              </p>
            </div>

            {/* 개념 카드 3개 */}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-white/[0.08] bg-white/[0.03] p-4">
                <Orbit size={18} className="mb-3 text-[#A8D8FF]/60" />
                <h3 className="mb-1 text-sm font-mono font-medium text-white/80">은하 = 도메인</h3>
                <p className="text-xs font-mono leading-5 text-white/35">연관된 개념들이 하나의 은하를 이룬다</p>
              </div>
              <div className="rounded-lg border border-white/[0.08] bg-white/[0.03] p-4">
                <Sparkles size={18} className="mb-3 text-[#FFD580]/60" />
                <h3 className="mb-1 text-sm font-mono font-medium text-white/80">항성 = 개념</h3>
                <p className="text-xs font-mono leading-5 text-white/35">하나의 지식 단위가 하나의 항성으로 빛난다</p>
              </div>
              <div className="rounded-lg border border-white/[0.08] bg-white/[0.03] p-4">
                <Clock size={18} className="mb-3 text-[#FF6B35]/60" />
                <h3 className="mb-1 text-sm font-mono font-medium text-white/80">생애주기 = 망각</h3>
                <p className="text-xs font-mono leading-5 text-white/35">복습하지 않으면 서서히 어두워져 사라진다</p>
              </div>
            </div>

            {/* CTA */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/auth/register')}
                className="flex items-center gap-2 rounded-lg bg-[#A8D8FF] px-5 py-2.5 text-sm font-mono font-bold text-[#050510] transition-colors hover:bg-[#A8D8FF]/90"
              >
                나만의 우주 만들기
                <ArrowRight size={15} />
              </button>
              <button
                onClick={() => navigate('/auth/login')}
                className="flex items-center gap-2 rounded-lg border border-white/[0.14] px-5 py-2.5 text-sm font-mono text-white/60 transition-colors hover:border-white/[0.28] hover:text-white/90"
              >
                <LogIn size={14} />
                로그인
              </button>
            </div>
          </section>
        )}

        {/* ── 공개 항성 피드 ── */}
        <section className="flex flex-col gap-6">
          <header className="border-b border-white/[0.08] pb-5">
            <p className="mb-2 text-[10px] font-mono uppercase tracking-[0.24em] text-white/30">public universes</p>
            <h2 className="text-xl font-mono font-semibold tracking-wide text-white/90">우주 탐색</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-white/40">
              공개로 열려 있는 다른 사람들의 지식을 둘러봅니다.
            </p>
          </header>

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
                        <h3 className="truncate text-base font-mono font-medium" style={{ color: style.color }}>
                          {star.title}
                        </h3>
                      </div>
                      <Compass size={16} className="mt-0.5 shrink-0 text-white/25 transition-colors group-hover:text-[#A8D8FF]/70" />
                    </div>
                    <p className="line-clamp-3 min-h-16 text-sm leading-5 text-white/45">
                      {star.content
                        ? star.content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim() || '내용 없음'
                        : '내용 없음'}
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
        </section>

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
