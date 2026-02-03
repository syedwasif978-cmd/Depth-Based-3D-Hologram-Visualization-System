import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import DepthHologram from './components/DepthHologram'

export default function App(){
  const [imageUrl, setImageUrl] = useState(null)
  const [depthUrl, setDepthUrl] = useState(null)

  return (
    <div className="app">
      <h1>Hologram MVP</h1>
      <UploadForm onResult={(res)=>{ setImageUrl(res.image_url); setDepthUrl(res.depth_url); }} />
      {imageUrl && depthUrl ? (
        <div className="viewer">
          <DepthHologram imageUrl={imageUrl} depthUrl={depthUrl} />
        </div>
      ) : (
        <div className="placeholder">Upload an image to see the hologram</div>
      )}
    </div>
  )
}
