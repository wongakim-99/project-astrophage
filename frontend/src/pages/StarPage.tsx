import React from 'react';
import { useParams } from 'react-router';

export default function StarPage() {
  const { username, slug } = useParams();

  return (
    <div className="w-full h-full flex items-center justify-center bg-background text-foreground">
      <div className="max-w-2xl w-full p-8 bg-[#1A1A2E] rounded-xl border border-white/10 shadow-2xl">
        <h1 className="text-3xl font-bold mb-4">{slug}</h1>
        <p className="text-opacity-70 text-sm mb-8">@{username}의 항성</p>
        <div className="prose prose-invert">
          {/* TODO: Add React Markdown here */}
          <p>마크다운 콘텐츠가 이곳에 렌더링됩니다.</p>
        </div>
      </div>
    </div>
  );
}
