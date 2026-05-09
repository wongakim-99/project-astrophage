import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router';
import UniversePage from './pages/UniversePage';
import GalaxyPage from './pages/GalaxyPage';
import StarPage from './pages/StarPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ExplorePage from './pages/ExplorePage';
import PublicUniversePage from './pages/PublicUniversePage';
import StarCreatePage from './pages/StarCreatePage';
import StarEditPage from './pages/StarEditPage';
import Navbar from './components/ui/Navbar';
import Sidebar from './components/ui/Sidebar';
import CmdKMenu from './components/ui/CmdKMenu';
import { useAuthStore } from './stores/authStore';

function RootRedirect() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitialized = useAuthStore((s) => s.isInitialized);

  if (!isInitialized) return null;
  return <Navigate to={isAuthenticated ? '/universe' : '/universes'} replace />;
}

function App() {
  const init = useAuthStore((s) => s.init);

  useEffect(() => {
    init();
  }, [init]);

  return (
    <>
      <Navbar />
      <Sidebar />
      <CmdKMenu />
      <main className="w-full h-screen pt-16">
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/universe" element={<UniversePage />} />
          <Route path="/galaxy/:id" element={<GalaxyPage />} />
          <Route path="/galaxy/:id/new" element={<StarCreatePage />} />
          <Route path="/galaxy/:id/edit/:starId" element={<StarEditPage />} />
          <Route path="/:username/stars/:slug" element={<StarPage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/universes" element={<PublicUniversePage />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
