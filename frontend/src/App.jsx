import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import DepthHologram from './components/DepthHologram'

export default function App(){
  const [imageUrl, setImageUrl] = useState(null)
  const [depthUrl, setDepthUrl] = useState(null)
  const [autoRotate, setAutoRotate] = useState(true)
  const [bloom, setBloom] = useState(true)

  return (
    <div className="app">
      <h1>Hologram MVP</h1>
      <UploadForm onResult={(res)=>{ setImageUrl(res.image_url); setDepthUrl(res.depth_url); }} />

      <div style={{marginBottom:12}}>
        <label style={{marginRight:12}}><input type="checkbox" checked={autoRotate} onChange={e=>setAutoRotate(e.target.checked)} /> Auto-rotate</label>
        <label><input type="checkbox" checked={bloom} onChange={e=>setBloom(e.target.checked)} /> Bloom</label>
      </div>

      {imageUrl && depthUrl ? (
        <div className="viewer">
          <DepthHologram imageUrl={imageUrl} depthUrl={depthUrl} autoRotate={autoRotate} bloom={bloom} />
        </div>
      ) : (
        <div className="placeholder">Upload an image to see the hologram</div>
      )}
    </div>
  )
}
