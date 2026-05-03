import { create } from 'zustand';

export interface GalaxyData {
  id: string;
  name: string;
  color: string;
  position: [number, number, number];
}

export const GALAXY_COLOR_PALETTE = [
  '#A8D8FF', // 청백
  '#FFD580', // 황금
  '#FF6B35', // 주황
  '#B8A8FF', // 보라
  '#A8FFD8', // 민트
  '#FF8FA8', // 핑크
];

interface GalaxyState {
  galaxies: GalaxyData[];
  selectedGalaxyId: string | null;
  setGalaxies: (galaxies: GalaxyData[]) => void;
  selectGalaxy: (id: string | null) => void;
  createGalaxy: (name: string, color: string) => GalaxyData;
}

const dummyGalaxies: GalaxyData[] = [
  { id: 'g1', name: 'Frontend Engineering', color: '#A8D8FF', position: [-20, 10, 0] },
  { id: 'g2', name: 'Machine Learning', color: '#FFD580', position: [30, -15, 0] },
  { id: 'g3', name: 'Backend Architecture', color: '#FF6B35', position: [5, 25, -10] },
];

export const useGalaxyStore = create<GalaxyState>((set, get) => ({
  galaxies: dummyGalaxies,
  selectedGalaxyId: null,
  setGalaxies: (galaxies) => set({ galaxies }),
  selectGalaxy: (id) => set({ selectedGalaxyId: id }),
  createGalaxy: (name, color) => {
    const newGalaxy: GalaxyData = {
      id: `g${Date.now()}`,
      name,
      color,
      position: [
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 60,
        0,
      ],
    };
    set({ galaxies: [...get().galaxies, newGalaxy] });
    return newGalaxy;
  },
}));
