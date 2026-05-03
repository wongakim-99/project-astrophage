import { Link, useParams } from 'react-router';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowLeft } from 'lucide-react';
import { usePublicStar } from '../hooks/useStars';
import { LIFECYCLE_STYLE } from '../types/api';

export default function StarPage() {
  const { username, slug } = useParams();
  const { data: star, isLoading } = usePublicStar(username, slug);

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-[#050510] text-sm font-mono text-white/35">
        loading...
      </div>
    );
  }

  if (!star) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-[#050510] px-6 text-center">
        <div>
          <p className="text-lg font-mono text-white/60">공개 지식을 찾을 수 없습니다</p>
          <Link to="/universes" className="mt-4 inline-flex items-center gap-2 text-sm font-mono text-[#A8D8FF] hover:text-[#A8D8FF]/80">
            <ArrowLeft size={14} />
            우주 탐색으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  const style = LIFECYCLE_STYLE[star.lifecycle_state];

  return (
    <div className="h-full w-full overflow-y-auto bg-[#050510] text-white custom-scrollbar">
      <article className="mx-auto w-full max-w-3xl px-6 py-10">
        <Link
          to="/universes"
          className="mb-8 inline-flex items-center gap-2 rounded border border-white/[0.1] bg-white/[0.04] px-3 py-1.5 text-xs font-mono text-white/50 transition-colors hover:border-white/[0.2] hover:text-white/80"
        >
          <ArrowLeft size={13} />
          우주 탐색
        </Link>

        <header className="mb-8 border-b border-white/[0.08] pb-6">
          <p className="mb-3 text-[11px] font-mono text-white/35">@{star.username}</p>
          <h1 className="text-3xl font-mono font-semibold tracking-wide" style={{ color: style.color }}>
            {star.title}
          </h1>
          <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] font-mono text-white/35">
            <span className="rounded bg-[#A8D8FF]/15 px-2 py-1 text-[#A8D8FF]">public</span>
            <span>{star.slug}</span>
          </div>
        </header>

        <div className="prose prose-invert max-w-none prose-headings:font-bold prose-a:text-[#A8D8FF]">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {star.content || '*내용 없음*'}
          </ReactMarkdown>
        </div>
      </article>
    </div>
  );
}
