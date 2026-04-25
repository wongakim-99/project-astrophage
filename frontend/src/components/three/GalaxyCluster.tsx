

interface GalaxyClusterProps {
  position: [number, number, number];
  color: string;
  name: string;
  onClick?: () => void;
}

// In the Universe View, a GalaxyCluster represents one entire domain/galaxy
export default function GalaxyCluster({ position, color, onClick }: GalaxyClusterProps) {
  return (
    <group position={position} onClick={onClick}>
      {/* Nebula Fog Effect Placeholder */}
      <mesh>
        <sphereGeometry args={[10, 32, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.1} />
      </mesh>
      
      {/* Core bright spot */}
      <mesh>
        <sphereGeometry args={[2, 32, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.5} />
      </mesh>
    </group>
  );
}
