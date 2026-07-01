export default function ProjectIdeas({ ideas }) {
    return (
        <div className="result-card full-width">
            <div className="card-header">
                <i className="ti ti-rocket" style={{ color: "#6366f1" }} aria-hidden="true"></i>
                <h2>Portfolio projects to boost your match</h2>
            </div>

            <div className="projects-list">
                {ideas.map((idea, i) => (
                    <div key={i} className="project-item">
                        <div className="project-top">
                            <span className="project-num">{i + 1}</span>
                            <div className="project-title-wrap">
                                <p className="project-title">{idea.title}</p>
                                <p className="project-impact">{idea.impact}</p>
                            </div>
                        </div>

                        <p className="project-desc">{idea.description}</p>

                        <div className="tech-tags">
                            {idea.tech_stack.map((tech, j) => (
                                <span key={j} className="tag tag-purple">{tech}</span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}