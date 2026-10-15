// CacheGuard dashboard skeleton.
// Every number below is a PLACEHOLDER. Replace with real measurements later.

const sampleMetrics = [
  { name: "Cache references", value: "1,200,000" },
  { name: "Cache misses", value: "84,000" },
  { name: "Instructions", value: "9,500,000" },
  { name: "CPU cycles", value: "6,100,000" },
];

const models = ["Logistic Regression", "Decision Tree", "Random Forest"];

export default function App() {
  return (
    <main className="page">
      <header className="top">
        <h1>CacheGuard</h1>
        <p className="sub">
          Research prototype: detecting a controlled cache-based covert channel from CPU performance counters.
        </p>
        <p className="notice" role="note">
          This page shows placeholder values only. Nothing here is a live CPU measurement or a trained model result.
        </p>
      </header>

      <section aria-labelledby="metrics-h">
        <h2 id="metrics-h">CPU metrics <span className="badge">Sample data</span></h2>
        <div className="tiles">
          {sampleMetrics.map((m) => (
            <div className="tile" key={m.name}>
              <div className="tile-value">{m.value}</div>
              <div className="tile-name">{m.name}</div>
            </div>
          ))}
        </div>
        <p className="hint">Real counters will appear here once data collection works.</p>
      </section>

      <section aria-labelledby="pred-h">
        <h2 id="pred-h">Prediction <span className="badge">No model yet</span></h2>
        <div className="prediction">
          <div className="prediction-label">Waiting for a trained model</div>
          <p className="hint">
            After training, this will show whether a run looks normal or suspicious. A high cache-miss count alone does
            not prove an attack.
          </p>
        </div>
      </section>

      <section aria-labelledby="eval-h">
        <h2 id="eval-h">Model evaluation <span className="badge">Not evaluated</span></h2>
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-score</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m}>
                  <td>{m}</td>
                  <td>–</td>
                  <td>–</td>
                  <td>–</td>
                  <td>–</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="hint">Scores will be added only after a valid experiment and a documented train/test split.</p>
      </section>
    </main>
  );
}
