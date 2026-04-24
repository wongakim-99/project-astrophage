import React from 'react';

export default function LoginPage() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#050510] relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(168,216,255,0.1)_0%,transparent_70%)]"></div>
      
      <div className="z-10 p-10 bg-[#1A1A2E]/80 backdrop-blur-md rounded-2xl border border-white/10 w-full max-w-md shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-widest text-white mb-2">ASTROPHAGE</h1>
          <p className="text-sm text-white/50">지식의 성간 항해를 시작하세요</p>
        </div>

        <form className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-white/70 mb-1">EMAIL</label>
            <input 
              type="text" 
              placeholder="user@example.com"
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#A8D8FF] transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-white/70 mb-1">PASSWORD</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#A8D8FF] transition-colors"
            />
          </div>
          
          <button 
            type="submit"
            className="w-full mt-4 bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold tracking-wide py-3 px-4 rounded-lg transition-colors cursor-pointer"
          >
            LOGIN
          </button>
        </form>
      </div>
    </div>
  );
}
