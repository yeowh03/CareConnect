import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../../httpClient";
import logo from "../../assets/logo.png";
import "../../styles/Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  // ✅ Validation rules
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
      setErr(
        "Password must be at least 8 characters long and include at least one letter and one number."
      );
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
    <div className="login-page">
      <div className="login-card">
        {/* Logo */}
        <img src={logo} alt="CareConnect Logo" className="login-logo" />

        <h2 className="login-title">Welcome to CareConnect</h2>

        {/* Form */}
        <form onSubmit={onEmailLogin} className="login-form">
          <input
            required
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="login-input"
          />
          <input
            required
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login-input"
          />
          {err && <p className="error-message">{err}</p>}

          <button type="submit" className="login-btn">
            Log In
          </button>
        </form>

        <div className="login-divider">
          <span>or</span>
        </div>

        {/* Google Login */}
        <button onClick={startGoogleLogin} className="google-btn">
          <img
            src="https://developers.google.com/identity/images/g-logo.png"
            alt="Google logo"
            className="google-icon"
          />
          Continue with Google
        </button>

        <p className="login-footer">
          Don’t have an account?{" "}
          <Link to="/register" className="login-link">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}