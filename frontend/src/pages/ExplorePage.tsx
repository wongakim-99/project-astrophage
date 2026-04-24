import React from 'react';

export default function ExplorePage() {
  return (
    <div className="w-full h-full p-8 overflow-y-auto">
      <h1 className="text-3xl font-bold mb-8 tracking-widest text-[#A8D8FF]">EXPLORE THE UNIVERSE</h1>
      <p className="mb-8 opacity-70">공개된 모든 항성을 탐색하세요.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* TODO: Render card grid of public stars */}
        <div className="p-6 bg-[#1A1A2E] border border-white/10 rounded-xl hover:border-white/30 transition-colors cursor-pointer">
          <h2 className="text-xl font-semibold text-[#FFD580]">Sample Star</h2>
          <p className="text-sm opacity-50 mt-2">@user</p>
        </div>
      </div>
    </div>
  );
}
