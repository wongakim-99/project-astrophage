import { Link } from 'react-router';
import { LogIn, LogOut, Menu } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';
import { useAuthStore } from '../../stores/authStore';

export default function Navbar() {
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const logout = useAuthStore((s) => s.logout);

  return (
    <nav className="fixed top-0 left-0 w-full h-16 z-40 bg-[#050510]/90 backdrop-blur-xl border-b border-white/[0.08] flex items-center justify-between px-5">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg text-white/55 hover:text-white/90 hover:bg-white/[0.06] transition-colors"
          aria-label="메뉴 열기"
        >
          <Menu size={20} />
        </button>

        <Link
          to="/universe"
          className="text-lg font-mono font-bold tracking-[0.18em] text-white/85 hover:text-white transition-colors"
        >
          ASTROPHAGE
        </Link>
      </div>

      {isAuthenticated ? (
        <button
          onClick={() => { void logout(); }}
          className="flex items-center gap-1.5 rounded border border-white/[0.15] bg-white/[0.07] px-3 py-1.5 text-sm font-mono text-white/75 transition-colors hover:border-white/[0.30] hover:bg-white/[0.12] hover:text-white"
        >
          <LogOut size={14} />
          <span>로그아웃</span>
        </button>
      ) : (
        <div className="flex items-center gap-3 text-sm font-mono">
          <Link
            to="/auth/register"
            className="text-white/55 hover:text-white/85 px-3 py-1.5 rounded border border-white/[0.12] hover:border-white/[0.25] transition-colors"
          >
            회원가입
          </Link>
          <Link
            to="/auth/login"
            className="flex items-center gap-1.5 bg-white/[0.07] hover:bg-white/[0.12] text-white/75 hover:text-white px-3 py-1.5 rounded border border-white/[0.15] hover:border-white/[0.30] transition-colors"
          >
            <LogIn size={14} />
            <span>로그인</span>
          </Link>
        </div>
      )}
    </nav>
  );
}
