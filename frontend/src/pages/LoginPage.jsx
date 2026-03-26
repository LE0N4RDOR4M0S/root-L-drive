import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login, register } from "../api/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "register") {
        await register(email, password);
      }
      await login(email, password);
      navigate("/");
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page login-page">
      <section className="auth-grid">
        <article className="auth-panel card">
          <p className="eyebrow">PRIVATE STORAGE PLATFORM</p>
          <h1>Root L Drive</h1>
          <p>
            Centralizando documentos, organização de estruturas hierarquicas e manter o controle
            operacional em uma interface preparada para uso pessoal.
          </p>
        </article>

        <section className="card auth-card">
          <h2>{mode === "login" ? "Acessar conta" : "Criar conta"}</h2>

          <form onSubmit={handleSubmit} className="form">
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </label>

            {error && <p className="error">{error}</p>}

            <button type="submit" disabled={loading}>
              {loading ? "Aguarde..." : mode === "login" ? "Entrar" : "Registrar"}
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
