import { useState } from "react"
import UploadStep from "./components/UploadStep"
import ResultsView from "./components/ResultsView"
import "./App.css"

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleReset = () => {
    setResult(null)
    setError("")
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <i className="ti ti-file-check" aria-hidden="true"></i>
            <span>ResumeAI</span>
          </div>
          <p className="tagline">Match your resume to any job in seconds</p>
        </div>
      </header>

      <main className="app-main">
        {!result ? (
          <UploadStep
            loading={loading}
            error={error}
            setLoading={setLoading}
            setError={setError}
            setResult={setResult}
          />
        ) : (
          <ResultsView result={result} onReset={handleReset} />
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by Gemini + LangChain</p>
      </footer>
    </div>
  )
}