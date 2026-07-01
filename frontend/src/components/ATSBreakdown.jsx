export default function ATSBreakdown({ criteria }) {
    const passed = criteria.filter(c => c.passed).length
    const total = criteria.length

    return (
        <div className="result-card full-width">
            <div className="card-header">
                <i className="ti ti-checklist" style={{ color: "#6366f1" }} aria-hidden="true"></i>
                <h2>ATS compatibility breakdown</h2>
                <span className="ats-score-badge">
                    {passed}/{total} passed
                </span>
            </div>

            <div className="ats-list">
                {criteria.map((item, i) => (
                    <div key={i} className={`ats-item ${item.passed ? "pass" : "fail"}`}>
                        <div className="ats-icon">
                            <i className={`ti ${item.passed ? "ti-circle-check" : "ti-circle-x"}`}
                                aria-hidden="true">
                            </i>
                        </div>
                        <div className="ats-content">
                            <p className="ats-criterion">{item.criterion}</p>
                            <p className="ats-note">{item.note}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}