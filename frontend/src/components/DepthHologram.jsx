import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import * as THREE from 'three'

function Hologram({ imageUrl, depthUrl, autoRotate }){
  const ref = useRef()
  const tex = useLoader(THREE.TextureLoader, imageUrl)
  const depthTex = useLoader(THREE.TextureLoader, depthUrl)

  const geometry = useMemo(()=> new THREE.PlaneGeometry(1.6, 1, 256, 256), [])

  useFrame(({clock})=>{
    const t = clock.getElapsedTime()
    if(ref.current){
      if(autoRotate){
        ref.current.rotation.y += 0.002
      } else {
        ref.current.rotation.y = 0.25 * Math.sin(t*0.2)
      }
      ref.current.position.y = 0.03 * Math.sin(t*1.2)
    }
  })

  return (
    <group>
      <mesh ref={ref} geometry={geometry}>
        <meshStandardMaterial
          map={tex}
          displacementMap={depthTex}
          displacementScale={0.35}
          color={'#7ee6ff'}
          emissive={'#00ffd5'}
          emissiveIntensity={0.6}
          transparent={true}
          opacity={0.9}
        />
      </mesh>

      <mesh geometry={geometry} renderOrder={1}>
        <meshBasicMaterial color="#00eaff" wireframe opacity={0.6} transparent />
      </mesh>
    </group>
  )
}

export default function DepthHologram({ imageUrl, depthUrl, autoRotate = true, bloom = true }){
  // Note: imageUrl and depthUrl are relative to backend (/static/...) so prefix with backend origin
  const imageFull = `http://localhost:8000${imageUrl}`
  const depthFull = `http://localhost:8000${depthUrl}`

  return (
    <div className="canvas-wrap">
      <Canvas camera={{ position: [0,0,2.5], fov: 35 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[5,5,5]} intensity={0.6} color={'#c6f7ff'} />
        <Hologram imageUrl={imageFull} depthUrl={depthFull} autoRotate={autoRotate} />
        <OrbitControls enablePan enableZoom enableRotate autoRotate={autoRotate} autoRotateSpeed={0.4} />
        {bloom && (
          <EffectComposer disableNormalPass>
            <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} height={300} intensity={0.9} />
          </EffectComposer>
        )}
      </Canvas>
    </div>
  )
}
