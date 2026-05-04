import { create } from 'zustand';

export const GALAXY_COLOR_PALETTE = [
  '#A8D8FF',
  '#FFD580',
  '#FF6B35',
  '#B8A8FF',
  '#A8FFD8',
  '#FF8FA8',
];

// 은하 ID(index)로 우주 뷰 3D 위치를 결정적으로 생성 (백엔드엔 없는 값)
export function galaxyPosition(index: number, total: number): [number, number, number] {
  const angle = (index / Math.max(total, 1)) * Math.PI * 2;
  const radius = 22 + (index % 3) * 10;
  return [
    parseFloat((Math.cos(angle) * radius).toFixed(2)),
    parseFloat((Math.sin(angle) * radius).toFixed(2)),
    0,
  ];
}

interface UIState {
  selectedGalaxyId: string | null;
  selectGalaxy: (id: string | null) => void;
}

export const useGalaxyStore = create<UIState>((set) => ({
  selectedGalaxyId: null,
  selectGalaxy: (id) => set({ selectedGalaxyId: id }),
}));
