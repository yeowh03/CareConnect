import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../httpClient";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  // ✅ Validation rules
  // Must contain '@' and NOT end with '.'
  const emailRegex = /^(?=.*@)(?!.*\.$).+$/;
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]{8,}$/;

  const onEmailLogin = async (e) => {
    e.preventDefault();
    setErr("");

    // Step 1: Frontend validation
    if (!emailRegex.test(email)) {
      setErr("Please enter a valid email.");
      return;
    }

    if (!passwordRegex.test(password)) {
      setErr("Password must be at least 8 characters long and include at least one letter and one number.");
      return;
    }

    // Step 2: Send login request
    try {
      const resp = await httpClient.post("/api/login_password", { email, password });
      if (resp.data.role === "M") {
        navigate("/managerhome");
      } else {
        navigate("/clienthome");
      }
    } catch (error) {
      if (error.response?.status === 401) {
        setErr("Invalid credentials. Please check your email or password.");
      } else {
        setErr(`Error: ${error.message}`);
      }
    }
  };

  function startGoogleLogin() {
    const base = import.meta.env.VITE_API_BASE || "http://localhost:5000";
    window.location.href = `${base}/api/login`;
  }

  return (
    <div>
      <h1>Sign in</h1>

      {err && <p style={{ color: "red" }}>{err}</p>}

      <button onClick={startGoogleLogin}>
        Continue with Google
      </button>

      <div style={{ margin: "16px 0", textAlign: "center", color: "#888" }}>or</div>

      <form onSubmit={onEmailLogin} style={{ display: "grid", gap: 10 }}>
        <input
          required
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          required
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Sign in with Email</button>
      </form>

      <p style={{ marginTop: 16 }}>
        Don’t have an account? <Link to="/register">Create one</Link>
      </p>
    </div>
  );
}