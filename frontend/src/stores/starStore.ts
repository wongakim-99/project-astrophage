import { create } from 'zustand';

export interface StarData {
  id: string;
  galaxyId: string;
  name: string;
  slug: string;
  color: string;
  size: number;
  position: [number, number, number];
  isPublic: boolean;
  content?: string; // Markdown content
}

interface StarState {
  stars: StarData[];
  selectedStarSlug: string | null;
  isPanelOpen: boolean;
  isCmdKOpen: boolean;
  setStars: (stars: StarData[]) => void;
  selectStar: (slug: string | null) => void;
  setPanelOpen: (isOpen: boolean) => void;
  setCmdKOpen: (isOpen: boolean) => void;
}

const dummyStars: StarData[] = [
  // Stars in Frontend Engineering (g1)
  { id: 's1', galaxyId: 'g1', name: 'React', slug: 'react', color: '#A8D8FF', size: 1.4, position: [0, 0, 0], isPublic: true, content: '# React\n\nA JavaScript library for building user interfaces.' },
  { id: 's2', galaxyId: 'g1', name: 'Zustand', slug: 'zustand', color: '#FFD580', size: 1.0, position: [5, 3, 0], isPublic: false, content: '# Zustand\n\nA small, fast and scalable bearbones state-management solution.' },
  { id: 's3', galaxyId: 'g1', name: 'Tailwind CSS', slug: 'tailwind-css', color: '#A8D8FF', size: 1.2, position: [-4, 6, 0], isPublic: true, content: '# Tailwind CSS\n\nA utility-first CSS framework.' },
  
  // Stars in Machine Learning (g2)
  { id: 's4', galaxyId: 'g2', name: 'Neural Networks', slug: 'neural-networks', color: '#FF6B35', size: 1.6, position: [0, 0, 0], isPublic: true, content: '# Neural Networks\n\nComputing systems vaguely inspired by the biological neural networks.' },
  { id: 's5', galaxyId: 'g2', name: 'Transformers', slug: 'transformers', color: '#A8D8FF', size: 1.5, position: [-8, -2, 0], isPublic: true, content: '# Transformers\n\nA deep learning architecture based on the attention mechanism.' },
];

export const useStarStore = create<StarState>((set) => ({
  stars: dummyStars,
  selectedStarSlug: null,
  isPanelOpen: false,
  isCmdKOpen: false,
  setStars: (stars) => set({ stars }),
  selectStar: (slug) => set({ selectedStarSlug: slug, isPanelOpen: !!slug }),
  setPanelOpen: (isOpen) => set({ isPanelOpen: isOpen }),
  setCmdKOpen: (isOpen) => set({ isCmdKOpen: isOpen }),
}));
