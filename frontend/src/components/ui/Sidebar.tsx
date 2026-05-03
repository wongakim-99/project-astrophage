import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Compass, Search, Globe, Settings, ChevronDown, ChevronUp, Plus, Orbit } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';
import { useStarStore } from '../../stores/starStore';
import { useGalaxyStore } from '../../stores/galaxyStore';
import StarCreateModal from './StarCreateModal';
import GalaxyCreateModal from './GalaxyCreateModal';

export default function Sidebar() {
  const { isSidebarOpen, closeSidebar } = useUIStore();
  const setCmdKOpen = useStarStore((s) => s.setCmdKOpen);
  const galaxies = useGalaxyStore((s) => s.galaxies);
  const navigate = useNavigate();

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isUniversePublic, setIsUniversePublic] = useState(false);
  const [showStarCreate, setShowStarCreate] = useState(false);
  const [showGalaxyCreate, setShowGalaxyCreate] = useState(false);

  const handleNavigate = (path: string) => {
    navigate(path);
    closeSidebar();
  };

  return (
    <>
      {/* 백드롭 */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 backdrop-blur-[2px]"
          onClick={closeSidebar}
        />
      )}

      {/* 사이드바 패널 */}
      <aside
        className={`fixed top-16 left-0 h-[calc(100vh-4rem)] w-60 z-40 flex flex-col transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{
          background: 'rgba(6, 6, 20, 0.97)',
          borderRight: '1px solid rgba(255,255,255,0.07)',
          boxShadow: '8px 0 32px rgba(0,0,0,0.5)',
        }}
      >
        <nav className="flex-1 px-3 py-4 flex flex-col gap-1 overflow-y-auto custom-scrollbar">

          {/* ── 내 우주 섹션 ── */}
          <div className="mb-1">
            <p className="text-[10px] font-mono text-white/25 tracking-[0.2em] uppercase px-3 mb-2">내 우주</p>

            <button
              onClick={() => { setShowStarCreate(true); }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
            >
              <Plus size={15} className="shrink-0 text-[#A8D8FF]/70" />
              <span>새 지식 추가</span>
            </button>

            <button
              onClick={() => { setShowGalaxyCreate(true); }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
            >
              <Orbit size={15} className="shrink-0 text-white/35" />
              <span>새 은하 만들기</span>
            </button>

            {/* 은하 목록 */}
            {galaxies.length > 0 && (
              <div className="mt-1 ml-3 flex flex-col gap-0.5">
                {galaxies.map((galaxy) => (
                  <button
                    key={galaxy.id}
                    onClick={() => handleNavigate(`/galaxy/${galaxy.id}`)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-md text-white/45 hover:text-white/75 hover:bg-white/[0.04] transition-colors text-xs font-mono w-full text-left"
                  >
                    <span
                      className="w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: galaxy.color }}
                    />
                    <span className="truncate">{galaxy.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="my-1 border-t border-white/[0.05]" />

          {/* ── 탐색 섹션 ── */}
          <button
            onClick={() => handleNavigate('/explore')}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
          >
            <Compass size={16} className="shrink-0 text-white/45" />
            <span>Explore</span>
          </button>

          <button
            onClick={() => { setCmdKOpen(true); closeSidebar(); }}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
          >
            <Search size={16} className="shrink-0 text-white/45" />
            <div className="flex items-center justify-between w-full">
              <span>지식 검색</span>
              <kbd className="text-[10px] px-1.5 py-0.5 bg-white/[0.07] rounded text-white/30">⌘K</kbd>
            </div>
          </button>

          <button
            onClick={() => handleNavigate('/explore')}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
          >
            <Globe size={16} className="shrink-0 text-white/45" />
            <div className="flex items-center justify-between w-full">
              <span>우주 탐색</span>
              <span className="text-[10px] text-white/25 font-mono">beta</span>
            </div>
          </button>

          <div className="my-1 border-t border-white/[0.05]" />

          {/* ── 설정 ── */}
          <button
            onClick={() => setIsSettingsOpen((v) => !v)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/65 hover:text-white/90 hover:bg-white/[0.06] transition-colors text-sm font-mono w-full text-left"
          >
            <Settings size={16} className="shrink-0 text-white/45" />
            <div className="flex items-center justify-between w-full">
              <span>설정</span>
              {isSettingsOpen
                ? <ChevronUp size={14} className="text-white/30" />
                : <ChevronDown size={14} className="text-white/30" />}
            </div>
          </button>

          {isSettingsOpen && (
            <div className="mx-3 mb-1 px-3 py-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <p className="text-[10px] font-mono text-white/35 tracking-[0.2em] uppercase mb-3">내 우주 공개 범위</p>
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => setIsUniversePublic(false)}
                  className={`flex items-start gap-2.5 px-2.5 py-2 rounded-md transition-colors text-left ${
                    !isUniversePublic ? 'bg-white/[0.06] border border-white/[0.1]' : 'hover:bg-white/[0.03]'
                  }`}
                >
                  <span className={`mt-0.5 w-3 h-3 rounded-full border shrink-0 flex items-center justify-center ${
                    !isUniversePublic ? 'border-white/60 bg-white/20' : 'border-white/20'
                  }`}>
                    {!isUniversePublic && <span className="w-1.5 h-1.5 rounded-full bg-white/80" />}
                  </span>
                  <div>
                    <p className="text-xs font-mono text-white/75">비공개</p>
                    <p className="text-[10px] font-mono text-white/35 mt-0.5">나만 볼 수 있음</p>
                  </div>
                </button>
                <button
                  onClick={() => setIsUniversePublic(true)}
                  className={`flex items-start gap-2.5 px-2.5 py-2 rounded-md transition-colors text-left ${
                    isUniversePublic ? 'bg-brand-active/10 border border-brand-active/25' : 'hover:bg-white/[0.03]'
                  }`}
                >
                  <span className={`mt-0.5 w-3 h-3 rounded-full border shrink-0 flex items-center justify-center ${
                    isUniversePublic ? 'border-brand-active bg-brand-active/30' : 'border-white/20'
                  }`}>
                    {isUniversePublic && <span className="w-1.5 h-1.5 rounded-full bg-brand-active" />}
                  </span>
                  <div>
                    <p className={`text-xs font-mono ${isUniversePublic ? 'text-brand-active' : 'text-white/75'}`}>공개</p>
                    <p className="text-[10px] font-mono text-white/35 mt-0.5">explore에 내 항성 노출</p>
                  </div>
                </button>
              </div>
            </div>
          )}
        </nav>

        <div className="px-4 py-3 border-t border-white/[0.05] text-[10px] font-mono text-white/20 tracking-widest">
          ✦ project astrophage
        </div>
      </aside>

      {/* 모달들 — 사이드바 외부에 렌더링 */}
      {showStarCreate && (
        <StarCreateModal onClose={() => setShowStarCreate(false)} />
      )}
      {showGalaxyCreate && (
        <GalaxyCreateModal onClose={() => setShowGalaxyCreate(false)} />
      )}
    </>
  );
}
