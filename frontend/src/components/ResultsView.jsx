export default function ResultsView({ result, onReset }) {
    const { match_score, summary, strengths, missing_keywords, improvement_tip } = result

    const scoreLevel = match_score >= 70 ? "high" : match_score >= 40 ? "medium" : "low"
    const scoreLabel = match_score >= 70 ? "Strong match" : match_score >= 40 ? "Partial match" : "Weak match"
    const scoreColor = match_score >= 70 ? "#22c55e" : match_score >= 40 ? "#f59e0b" : "#ef4444"

    const circumference = 2 * Math.PI * 54
    const offset = circumference - (match_score / 100) * circumference

    return (
        <div className="results-page">
            <div className="results-container">

                {/* Score Hero */}
                <div className="score-hero">
                    <div className="score-ring-wrap">
                        <svg width="140" height="140" viewBox="0 0 140 140" aria-hidden="true">
                            <circle cx="70" cy="70" r="54" fill="none" stroke="var(--border)" strokeWidth="10" />
                            <circle
                                cx="70" cy="70" r="54"
                                fill="none"
                                stroke={scoreColor}
                                strokeWidth="10"
                                strokeLinecap="round"
                                strokeDasharray={circumference}
                                strokeDashoffset={offset}
                                transform="rotate(-90 70 70)"
                                style={{ transition: "stroke-dashoffset 1s ease" }}
                            />
                        </svg>
                        <div className="score-center">
                            <span className="score-number" style={{ color: scoreColor }}>{match_score}</span>
                            <span className="score-denom">/100</span>
                        </div>
                    </div>
                    <div className="score-meta">
                        <p className={`score-label ${scoreLevel}`}>{scoreLabel}</p>
                        <p className="score-summary">{summary}</p>
                    </div>
                </div>

                <div className="results-grid">

                    {/* Strengths */}
                    <div className="result-card">
                        <div className="card-header">
                            <i className="ti ti-circle-check" style={{ color: "#22c55e" }} aria-hidden="true"></i>
                            <h2>What matches</h2>
                        </div>
                        {strengths.length > 0 ? (
                            <div className="tag-list">
                                {strengths.map((s, i) => (
                                    <span key={i} className="tag tag-green">{s}</span>
                                ))}
                            </div>
                        ) : (
                            <p className="empty-note">No strong matches found.</p>
                        )}
                    </div>

                    {/* Missing */}
                    <div className="result-card">
                        <div className="card-header">
                            <i className="ti ti-circle-x" style={{ color: "#ef4444" }} aria-hidden="true"></i>
                            <h2>What's missing</h2>
                        </div>
                        {missing_keywords.length > 0 ? (
                            <div className="tag-list">
                                {missing_keywords.map((k, i) => (
                                    <span key={i} className="tag tag-red">{k}</span>
                                ))}
                            </div>
                        ) : (
                            <span className="tag tag-green">No gaps found</span>
                        )}
                    </div>
                </div>

                {/* Improvement Tip */}
                <div className="tip-card">
                    <div className="card-header">
                        <i className="ti ti-bulb" style={{ color: "#f59e0b" }} aria-hidden="true"></i>
                        <h2>Improvement tip</h2>
                    </div>
                    <p className="tip-text">{improvement_tip}</p>
                </div>

                {/* Actions */}
                <div className="actions">
                    <button className="reset-btn" onClick={onReset}>
                        <i className="ti ti-refresh" aria-hidden="true"></i>
                        Analyze another resume
                    </button>
                </div>

            </div>
        </div>
    )
}