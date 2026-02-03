import React, { useState } from 'react'
import axios from 'axios'

export default function UploadForm({ onResult }){
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)

  async function submit(e){
    e.preventDefault()
    if(!file) return
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
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
      <input type="file" accept="image/*" onChange={e=>setFile(e.target.files[0])} />
      <button type="submit" disabled={loading}>{loading? 'Processing...' : 'Upload & Create Hologram'}</button>
    </form>
  )
}
