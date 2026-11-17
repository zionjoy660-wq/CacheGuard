import { useEffect, useState } from "react";

// CacheGuard dashboard. Talks to the FastAPI backend.
// Start the backend first:  uvicorn main:app --reload --app-dir src/api
const API = "http://127.0.0.1:8000";

// Averages taken from the lab dataset (60 runs, 1,800 one-second rows). They are averages, not single rows.
const EXAMPLES = {
  normal: { cache_references: 505969400, cache_misses: 3025, instructions: 4795373000, cpu_cycles: 3770873000 },
  suspicious: { cache_references: 299217500, cache_misses: 83573500, instructions: 1517615000, cpu_cycles: 3763499000 },
};

const FIELDS = [
  ["cache_references", "Cache references"],
  ["cache_misses", "Cache misses"],
  ["instructions", "Instructions"],
  ["cpu_cycles", "CPU cycles"],
];

const MODEL_ORDER = ["Logistic Regression", "Decision Tree", "Random Forest"];
const SET_ORDER = ["all", "cache_only", "miss_rate_only", "instructions_only", "cycles_only"];
const SET_NOTE = { cycles_only: "control: cycles were almost equal for both labels" };

const pct = (x) => (x * 100).toFixed(3) + "%";

function errorText(body) {
  if (!body) return "Request failed.";
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg || JSON.stringify(d)).join(" | ");
  return "Request failed.";
}

export default function App() {
  const [health, setHealth] = useState({ state: "checking" });
  const [form, setForm] = useState({ cache_references: "", cache_misses: "", instructions: "", cpu_cycles: "" });
  const [model, setModel] = useState("Random Forest");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState({ state: "loading", rows: [] });

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => r.json())
      .then((j) => setHealth({ state: "up", modelLoaded: j.model_loaded }))
      .catch(() => setHealth({ state: "down" }));
    fetch(`${API}/results`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((j) => setResults({ state: "ok", rows: j.rows }))
      .catch(() => setResults({ state: "error", rows: [] }));
  }, []);

  const setField = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const load = (key) => { setForm(Object.fromEntries(Object.entries(EXAMPLES[key]).map(([k, v]) => [k, String(v)]))); setResult(null); setError(""); };

  async function submit() {
    setError(""); setResult(null);
    const body = {};
    for (const [k] of FIELDS) {
      if (form[k].trim() === "" || Number.isNaN(Number(form[k]))) { setError("Enter a number in every box."); return; }
      body[k] = Number(form[k]);
    }
    setBusy(true);
    try {
      const r = await fetch(`${API}/predict?model=${encodeURIComponent(model)}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      });
      const j = await r.json().catch(() => null);
      if (!r.ok) setError(errorText(j)); else setResult(j);
    } catch {
      setError("Cannot reach the backend. Start it with: uvicorn main:app --reload --app-dir src/api");
    } finally { setBusy(false); }
  }

  const table = {};
  results.rows.forEach((r) => { (table[r.feature_set] ||= {})[r.model] = r; });

  return (
    <main className="page">
      <header className="top">
        <h1>CacheGuard</h1>
        <p className="sub">Research prototype: classifying a controlled cache-pattern workload from CPU performance counters.</p>
        <p className="notice" role="note">
          CacheGuard classifies controlled cache-pattern simulations. It does not detect or confirm real covert-channel attacks.
        </p>
      </header>

      <section aria-labelledby="status-h">
        <h2 id="status-h">Backend status</h2>
        {health.state === "checking" && <p className="hint">Checking...</p>}
        {health.state === "up" && <p><span className="dot ok" /> Running. Model {health.modelLoaded ? "loaded" : "NOT loaded (check models/real_models.joblib)"}.</p>}
        {health.state === "down" && <p><span className="dot bad" /> Not reachable. Start it with <code>uvicorn main:app --reload --app-dir src/api</code>, then reload this page.</p>}
      </section>

      <section aria-labelledby="pred-h">
        <h2 id="pred-h">Try a prediction <span className="badge">one second of counters</span></h2>
        <div className="row-buttons">
          <button className="ghost" onClick={() => load("normal")}>Fill with the average normal second</button>
          <button className="ghost" onClick={() => load("suspicious")}>Fill with the average suspicious second</button>
        </div>
        <div className="grid">
          {FIELDS.map(([k, label]) => (
            <label key={k}>{label}
              <input inputMode="numeric" value={form[k]} onChange={setField(k)} placeholder="e.g. 300000000" />
            </label>
          ))}
          <label>Model
            <select value={model} onChange={(e) => setModel(e.target.value)}>
              {MODEL_ORDER.map((m) => <option key={m}>{m}</option>)}
            </select>
          </label>
        </div>
        <button onClick={submit} disabled={busy}>{busy ? "Working..." : "Predict"}</button>
        {error && <p className="error" role="alert">{error}</p>}
        {result && (
          <div className="result">
            <div className="result-main">{result.message}</div>
            <p className="hint">
              Miss rate {pct(result.miss_rate)}. {result.model}: probability of the suspicious class {pct(result.probability_suspicious)}.
              This is a model output, not proof of an attack.
            </p>
            <ul className="all">
              {result.all_models.map((m) => <li key={m.model}>{m.model}: {m.label_name} ({pct(m.probability_suspicious)})</li>)}
            </ul>
            <p className="hint">{result.scope_note}</p>
          </div>
        )}
      </section>

      <section aria-labelledby="eval-h">
        <h2 id="eval-h">Real results <span className="badge">5-fold cross-validation, split by run</span></h2>
        {results.state === "loading" && <p className="hint">Loading...</p>}
        {results.state === "error" && <p className="error">Results not available. Is the backend running, and does results/real_cv_results.csv exist?</p>}
        {results.state === "ok" && (
          <div className="scroll">
            <table>
              <thead><tr><th>Features</th>{MODEL_ORDER.map((m) => <th key={m}>{m}</th>)}</tr></thead>
              <tbody>
                {SET_ORDER.filter((s) => table[s]).map((s) => (
                  <tr key={s}>
                    <td>{s}{SET_NOTE[s] ? <div className="hint">{SET_NOTE[s]}</div> : null}</td>
                    {MODEL_ORDER.map((m) => <td key={m}>{table[s][m] ? `${pct(table[s][m].accuracy_mean)} (±${pct(table[s][m].accuracy_std)})` : "-"}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="hint">Accuracy, mean over 5 folds (± standard deviation). 60 runs, 30 normal and 30 suspicious, from one lab session.</p>
        {results.state === "ok" && (
          <div className="figs">
            <img alt="Accuracy by feature set" src={`${API}/results/image/real_accuracy_by_features.png`} />
            <img alt="Confusion matrices, all features" src={`${API}/results/image/real_confusion_matrices.png`} />
          </div>
        )}
      </section>

      <section aria-labelledby="lim-h">
        <h2 id="lim-h">What these results do and do not show</h2>
        <ul className="limits">
          <li>The two classes were built to be far apart: a small buffer that fits in the L3 cache against a large buffer that does not. So near-perfect scores show that the pipeline works on a clear case.</li>
          <li>Cache-miss features alone, and instruction counts alone, each separate the classes perfectly. The experiment cannot show which signal the all-feature models rely on.</li>
          <li>The cycles-only control scores about 54 to 55%, close to chance, so the pipeline does give a poor result when a feature carries no information.</li>
          <li>One machine, one session, 60 runs, no background noise. This is a simplified stand-in, not a real covert-channel attack.</li>
        </ul>
      </section>
    </main>
  );
}
