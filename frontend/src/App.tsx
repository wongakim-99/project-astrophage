import { Routes, Route, Navigate } from 'react-router';
import UniversePage from './pages/UniversePage';
import GalaxyPage from './pages/GalaxyPage';
import StarPage from './pages/StarPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ExplorePage from './pages/ExplorePage';
import Navbar from './components/ui/Navbar';
import Sidebar from './components/ui/Sidebar';
import CmdKMenu from './components/ui/CmdKMenu';

function App() {
  return (
    <>
      <Navbar />
      <Sidebar />
      <CmdKMenu />
      <main className="w-full h-screen pt-16">
        <Routes>
          <Route path="/" element={<Navigate to="/universe" replace />} />
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          {/* TODO: Add ProtectedRoute wrapper for logged in users */}
          <Route path="/universe" element={<UniversePage />} />
          <Route path="/galaxy/:id" element={<GalaxyPage />} />
          {/* Public Pages */}
          <Route path="/:username/stars/:slug" element={<StarPage />} />
          <Route path="/explore" element={<ExplorePage />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
