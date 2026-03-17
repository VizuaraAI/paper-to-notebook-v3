import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE !== undefined ? import.meta.env.VITE_API_BASE : 'http://localhost:8000'

function App() {
  const [apiKey, setApiKey] = useState('')
  const [arxivUrl, setArxivUrl] = useState('')
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const canSubmit = apiKey.trim() && (file || arxivUrl.trim()) && !loading

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0]
    if (selected && !selected.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file')
      setFile(null)
      return
    }
    setError('')
    setFile(selected || null)
  }

  const downloadNotebook = (notebook) => {
    const confirmed = window.confirm(
      '⚠️ This notebook contains AI-generated code. Please review all code cells carefully before running them in Google Colab. Do you want to download?'
    )
    if (!confirmed) return

    const blob = new Blob([JSON.stringify(notebook, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'notebook.ipynb'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!apiKey.trim()) {
      setError('Please enter your Gemini API key')
      return
    }
    if (!file && !arxivUrl.trim()) {
      setError('Please upload a PDF or enter an arXiv URL')
      return
    }

    setError('')
    setLoading(true)

    try {
      let response

      if (file) {
        const formData = new FormData()
        formData.append('file', file)
        response = await fetch(`${API_BASE}/api/upload-pdf`, {
          method: 'POST',
          headers: { 'X-Api-Key': apiKey },
          body: formData,
        })
      } else {
        response = await fetch(`${API_BASE}/api/arxiv-url`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Api-Key': apiKey,
          },
          body: JSON.stringify({ url: arxivUrl }),
        })
      }

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || `Server error (${response.status})`)
      }

      const notebook = await response.json()
      downloadNotebook(notebook)
      setApiKey('')
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center justify-center gap-3 mb-6">
          <img src="/vizuara-logo.png" alt="Vizuara" className="h-10 w-10 rounded" />
          <h1
            data-testid="title"
            className="text-2xl font-bold text-gray-800"
          >
            Paper to Notebook
          </h1>
        </div>
        <p className="text-gray-500 text-center mb-8 text-sm">
          Convert research papers into runnable Google Colab notebooks
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* API Key */}
          <div>
            <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-1">
              Gemini API Key
            </label>
            <input
              id="api-key"
              data-testid="api-key-input"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Gemini API key"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400">Upload PDF or enter arXiv URL</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          {/* PDF Upload */}
          <div>
            <label htmlFor="pdf-upload" className="block text-sm font-medium text-gray-700 mb-1">
              PDF File
            </label>
            <input
              id="pdf-upload"
              data-testid="pdf-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {/* ArXiv URL */}
          <div>
            <label htmlFor="arxiv-url" className="block text-sm font-medium text-gray-700 mb-1">
              arXiv URL
            </label>
            <input
              id="arxiv-url"
              data-testid="arxiv-url-input"
              type="text"
              value={arxivUrl}
              onChange={(e) => setArxivUrl(e.target.value)}
              placeholder="https://arxiv.org/abs/2401.12345"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Error */}
          {error && (
            <p data-testid="error-message" className="text-red-600 text-sm">
              {error}
            </p>
          )}

          {/* Submit */}
          <button
            type="submit"
            data-testid="generate-btn"
            disabled={!canSubmit}
            className="w-full py-2.5 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm"
          >
            {loading ? (
              <span data-testid="loading-spinner" className="inline-flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </span>
            ) : (
              'Generate Notebook'
            )}
          </button>

          {/* Safety Notice */}
          <p data-testid="safety-notice" className="text-xs text-gray-400 text-center mt-2">
            Generated notebooks contain AI-written code. Always review before executing.
          </p>
        </form>
      </div>
    </div>
  )
}

export default App
