import { useState, useRef } from "react"
import axios from "axios"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function UploadStep({ loading, error, setLoading, setError, setResult }) {
    const [file, setFile] = useState(null)
    const [jobDesc, setJobDesc] = useState("")
    const [dragging, setDragging] = useState(false)
    const fileInputRef = useRef(null)

    const handleFile = (f) => {
        if (!f) return
        if (!f.name.endsWith(".pdf")) {
            setError("Only PDF files are accepted.")
            return
        }
        if (f.size > 5 * 1024 * 1024) {
            setError("File size must be under 5MB.")
            return
        }
        setError("")
        setFile(f)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setDragging(false)
        handleFile(e.dataTransfer.files[0])
    }

    const handleSubmit = async () => {
        if (!file || !jobDesc.trim()) {
            setError("Please upload a resume and paste a job description.")
            return
        }
        if (jobDesc.trim().length < 50) {
            setError("Job description is too short. Please paste the full description.")
            return
        }
        setError("")
        setLoading(true)

        const formData = new FormData()
        formData.append("resume", file)
        formData.append("job_description", jobDesc)

        try {
            const res = await axios.post(`${API_URL}/api/v1/analyze`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            })
            setResult(res.data)
        } catch (err) {
            const detail = err.response?.data?.detail
            if (err.response?.status === 429) {
                setError("AI service rate limit reached. Please wait a moment and try again.")
            } else if (err.response?.status === 503) {
                setError("AI service is temporarily unavailable. Please try again shortly.")
            } else {
                setError(detail || "Something went wrong. Please try again.")
            }
        } finally {
            setLoading(false)
        }
    }

    const canSubmit = file && jobDesc.trim().length >= 50 && !loading

    return (
        <div className="upload-page">
            <div className="steps-container">

                {/* Step 1 — Upload */}
                <div className="step-card">
                    <div className="step-label">
                        <span className="step-num">1</span>
                        <span>Upload your resume</span>
                    </div>

                    <div
                        className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
                        onClick={() => fileInputRef.current.click()}
                        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                        onDragLeave={() => setDragging(false)}
                        onDrop={handleDrop}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf"
                            style={{ display: "none" }}
                            onChange={(e) => handleFile(e.target.files[0])}
                        />
                        {file ? (
                            <div className="file-selected">
                                <i className="ti ti-file-type-pdf" aria-hidden="true"></i>
                                <div>
                                    <p className="file-name">{file.name}</p>
                                    <p className="file-size">{(file.size / 1024).toFixed(0)} KB</p>
                                </div>
                                <button
                                    className="remove-file"
                                    onClick={(e) => { e.stopPropagation(); setFile(null) }}
                                    aria-label="Remove file"
                                >
                                    <i className="ti ti-x"></i>
                                </button>
                            </div>
                        ) : (
                            <div className="drop-prompt">
                                <i className="ti ti-upload" aria-hidden="true"></i>
                                <p>Drop your PDF here or <span className="link-text">browse</span></p>
                                <p className="hint">PDF only · Max 5MB</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Step 2 — Job Description */}
                <div className="step-card">
                    <div className="step-label">
                        <span className="step-num">2</span>
                        <span>Paste the job description</span>
                    </div>

                    <div className="jd-wrapper">
                        <textarea
                            className="jd-input"
                            placeholder="Paste the full job description here — including responsibilities, requirements, and skills..."
                            value={jobDesc}
                            onChange={(e) => setJobDesc(e.target.value)}
                            rows={10}
                        />
                        <div className="jd-meta">
                            <span className={`char-count ${jobDesc.length > 5000 ? "over-limit" : ""}`}>
                                {jobDesc.length} / 5000
                            </span>
                            {jobDesc.length >= 50 && (
                                <span className="jd-ok">
                                    <i className="ti ti-check"></i> Ready
                                </span>
                            )}
                        </div>
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div className="error-banner" role="alert">
                        <i className="ti ti-alert-circle" aria-hidden="true"></i>
                        <span>{error}</span>
                    </div>
                )}

                {/* Submit */}
                <button
                    className={`analyze-btn ${canSubmit ? "active" : ""}`}
                    onClick={handleSubmit}
                    disabled={!canSubmit}
                >
                    {loading ? (
                        <span className="btn-loading">
                            <span className="spinner"></span>
                            Analyzing your resume...
                        </span>
                    ) : (
                        <span>
                            Analyze match
                            <i className="ti ti-arrow-right" aria-hidden="true"></i>
                        </span>
                    )}
                </button>

                {loading && (
                    <p className="loading-hint">
                        This takes 10–15 seconds. The AI is reading your resume carefully.
                    </p>
                )}
            </div>
        </div>
    )
}