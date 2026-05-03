import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuthStore } from '../stores/authStore';

export default function RegisterPage() {
  const register = useAuthStore((s) => s.register);
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form.username, form.email, form.password);
      navigate('/universe');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      setError(msg ?? '회원가입에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#050510] relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(168,216,255,0.08)_0%,transparent_70%)]" />

      <div className="z-10 p-10 bg-[#1A1A2E]/80 backdrop-blur-md rounded-2xl border border-white/10 w-full max-w-md shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-widest text-white mb-2">ASTROPHAGE</h1>
          <p className="text-sm text-white/60">새로운 우주를 만드세요</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-white/75 mb-1.5">USERNAME</label>
            <input
              type="text"
              placeholder="my_universe"
              value={form.username}
              onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
              required
              minLength={3}
              maxLength={50}
              pattern="^[a-zA-Z0-9_-]+"
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-[#A8D8FF] transition-colors"
            />
            <p className="text-[11px] text-white/35 mt-1.5">영문, 숫자, _, - 만 사용 가능 (3–50자)</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-white/75 mb-1.5">EMAIL</label>
            <input
              type="email"
              placeholder="user@example.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              required
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-[#A8D8FF] transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-white/75 mb-1.5">PASSWORD</label>
            <input
              type="password"
              placeholder="8자 이상"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              required
              minLength={8}
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-[#A8D8FF] transition-colors"
            />
          </div>

          {error && (
            <p className="text-xs text-red-400/80 font-mono text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold tracking-wide py-3 px-4 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? '처리 중...' : '회원가입'}
          </button>
        </form>

        <p className="text-center text-sm text-white/45 mt-6">
          이미 계정이 있으신가요?{' '}
          <Link to="/auth/login" className="text-[#A8D8FF] hover:text-[#A8D8FF]/80 transition-colors font-medium">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
