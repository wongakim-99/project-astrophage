import { create } from 'zustand';

interface StarUIState {
  selectedStarSlug: string | null;
  isPanelOpen: boolean;
  isCmdKOpen: boolean;
  selectStar: (slug: string | null) => void;
  setPanelOpen: (isOpen: boolean) => void;
  setCmdKOpen: (isOpen: boolean) => void;
}

export const useStarStore = create<StarUIState>((set) => ({
  selectedStarSlug: null,
  isPanelOpen: false,
  isCmdKOpen: false,
  selectStar: (slug) => set({ selectedStarSlug: slug, isPanelOpen: !!slug }),
  setPanelOpen: (isOpen) => set({ isPanelOpen: isOpen }),
  setCmdKOpen: (isOpen) => set({ isCmdKOpen: isOpen }),
}));
