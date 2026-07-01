import { useState } from "react"

export default function TailoredResume({ content }) {
    const [copied, setCopied] = useState(false)

    const handleCopy = () => {
        navigator.clipboard.writeText(content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="result-card full-width">
            <div className="card-header">
                <i className="ti ti-file-text" style={{ color: "#6366f1" }} aria-hidden="true"></i>
                <h2>Your ATS-optimized resume</h2>
                <button className="copy-btn" onClick={handleCopy}>
                    <i className={`ti ${copied ? "ti-check" : "ti-copy"}`} aria-hidden="true"></i>
                    {copied ? "Copied!" : "Copy"}
                </button>
            </div>

            <div className="resume-notice">
                <i className="ti ti-info-circle" aria-hidden="true"></i>
                <p>
                    Tailored to match this job description with ATS-friendly keywords.
                    Review carefully — only use experience you actually have.
                </p>
            </div>

            <pre className="resume-content">{content}</pre>
        </div>
    )
}