import React, { useState } from 'react'
import axios from 'axios'

export default function UploadForm({ onResult }){
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [edgeSharpen, setEdgeSharpen] = useState(false)
  const [backgroundBlur, setBackgroundBlur] = useState(false)

  function handleFileChange(e){
    const selected = Array.from(e.target.files).slice(0,2)
    setFiles(selected)
  }

  async function submit(e){
    e.preventDefault()
    if(files.length === 0) return alert('Select 1 or 2 images')
    setLoading(true)
    const fd = new FormData()
    files.forEach(f=> fd.append('files', f))
    fd.append('edge_sharpen', edgeSharpen ? 'true' : 'false')
    fd.append('background_blur', backgroundBlur ? 'true' : 'false')

    try{
      const res = await axios.post('http://localhost:8000/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      onResult(res.data)
    }catch(err){
      alert('Upload failed: '+(err?.response?.data?.detail || err.message))
    }finally{
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="upload-form">
      <input type="file" accept="image/*" multiple onChange={handleFileChange} />
      <div style={{marginTop:8}}>
        <label><input type="checkbox" checked={edgeSharpen} onChange={e=>setEdgeSharpen(e.target.checked)} /> Edge sharpen (enhance contours)</label>
        <br />
        <label><input type="checkbox" checked={backgroundBlur} onChange={e=>setBackgroundBlur(e.target.checked)} /> Background blur</label>
      </div>
      <button type="submit" disabled={loading}>{loading? 'Processing...' : 'Upload & Create Hologram'}</button>
    </form>
  )
}
