import { create } from 'zustand';

export interface GalaxyData {
  id: string;
  name: string;
  color: string;
  position: [number, number, number];
}

interface GalaxyState {
  galaxies: GalaxyData[];
  selectedGalaxyId: string | null;
  setGalaxies: (galaxies: GalaxyData[]) => void;
  selectGalaxy: (id: string | null) => void;
}

const dummyGalaxies: GalaxyData[] = [
  { id: 'g1', name: 'Frontend Engineering', color: '#A8D8FF', position: [-20, 10, 0] },
  { id: 'g2', name: 'Machine Learning', color: '#FFD580', position: [30, -15, 0] },
  { id: 'g3', name: 'Backend Architecture', color: '#FF6B35', position: [5, 25, -10] },
];

export const useGalaxyStore = create<GalaxyState>((set) => ({
  galaxies: dummyGalaxies,
  selectedGalaxyId: null,
  setGalaxies: (galaxies) => set({ galaxies }),
  selectGalaxy: (id) => set({ selectedGalaxyId: id }),
}));
