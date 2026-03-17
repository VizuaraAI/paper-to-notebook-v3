import { useState } from 'react'

function App() {
  const [apiKey, setApiKey] = useState('')
  const [arxivUrl, setArxivUrl] = useState('')
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')

  const canSubmit = apiKey.trim() && (file || arxivUrl.trim())

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

  const handleSubmit = (e) => {
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
    // API integration will be added in Task 8
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-lg p-8">
        <h1
          data-testid="title"
          className="text-2xl font-bold text-gray-800 text-center mb-6"
        >
          Paper to Notebook
        </h1>
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
            Generate Notebook
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
