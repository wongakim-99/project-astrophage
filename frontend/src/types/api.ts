export type LifecycleState =
  | 'main_sequence'
  | 'yellow_dwarf'
  | 'red_giant'
  | 'white_dwarf'
  | 'dark_matter';

export interface GalaxyResponse {
  id: string;
  name: string;
  slug: string;
  color: string;
  star_count: number;
}

export interface StarResponse {
  id: string;
  user_id: string;
  galaxy_id: string;
  title: string;
  slug: string;
  content: string;
  pos_x: number;
  pos_y: number;
  is_public: boolean;
  lifecycle_state: LifecycleState;
  energy_score: number;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
}

// lifecycle 상태 → 3D 시각 스타일 매핑
export const LIFECYCLE_STYLE: Record<LifecycleState, { color: string; size: number }> = {
  main_sequence: { color: '#A8D8FF', size: 1.4 },
  yellow_dwarf:  { color: '#FFD580', size: 1.0 },
  red_giant:     { color: '#FF6B35', size: 1.6 },
  white_dwarf:   { color: '#E8E8E8', size: 0.6 },
  dark_matter:   { color: '#1A1A2E', size: 0.3 },
};
