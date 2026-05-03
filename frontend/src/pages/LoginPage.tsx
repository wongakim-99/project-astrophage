import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuthStore } from '../stores/authStore';

export default function LoginPage() {
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate('/universe');
    } catch {
      setError('이메일 또는 비밀번호가 올바르지 않습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#050510] relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(168,216,255,0.1)_0%,transparent_70%)]" />

      <div className="z-10 p-10 bg-[#1A1A2E]/80 backdrop-blur-md rounded-2xl border border-white/10 w-full max-w-md shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-widest text-white mb-2">ASTROPHAGE</h1>
          <p className="text-sm text-white/60">지식의 성간 항해를 시작하세요</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              required
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
            {loading ? '로그인 중...' : 'LOGIN'}
          </button>
        </form>

        <p className="text-center text-sm text-white/45 mt-6">
          계정이 없으신가요?{' '}
          <Link to="/auth/register" className="text-[#A8D8FF] hover:text-[#A8D8FF]/80 transition-colors font-medium">
            회원가입
          </Link>
        </p>
      </div>
    </div>
  );
}
