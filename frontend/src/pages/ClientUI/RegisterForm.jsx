import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import httpClient from "../../httpClient";
import { FaArrowLeft } from "react-icons/fa";
import logo from "../../assets/logo.png";
import "../../styles/RegisterForm.css";

export default function Register() {
  const navigate = useNavigate();
  const location = useLocation();
  const registering = location?.state?.profile?.email == null;
  const updating = !!location.state?.profile?.profile_complete; 

  const [useGmail, setUseGmail] = useState(location.state?.profile?.gmail_acc || false);

  const [err, setErr] = useState("");

  const [name, setName] = useState(location.state?.profile?.name || "");
  const [contactNumber, setContactNumber] = useState(location.state?.profile?.contact_number || "");
  const [monthlyIncome, setMonthlyIncome] = useState(location.state?.profile?.monthly_income || "");
  const [email, setEmail] = useState(location.state?.profile?.email || "");
  const [password, setPassword] = useState("");
  
  // ✅ Validation regex
  const phoneRegex = /^(?:\+65)?[89]\d{7}$/; // +65 optional, starts with 8 or 9
  const passwordRegex =
    /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]{8,}$/; // ≥8 chars, at least 1 letter + 1 number

  // ✅ Reusable validation check
  const validateInputs = () => {
    if (name.trim() === "" || contactNumber.trim() === "" || monthlyIncome === "") {
      setErr("All fields are required.");
      return false;
    }

    // Phone validation
    const normalizedPhone = contactNumber.replace(/[\s-]/g, "");
    if (!phoneRegex.test(normalizedPhone)) {
      setErr("Invalid Singapore phone number. Must start with 8 or 9 and have 8 digits (optional +65).");
      return false;
    }

    if (!useGmail) {
      if (email.trim() === "" || password.trim() === "") {
        setErr("Email and password are required.");
        return false;
      }

      if (!/^(?=.*@)(?!.*\.$).+$/.test(email)) {
        setErr("Invalid email format. Must contain '@' and not end with '.'.");
        return false;
      }

      if (!passwordRegex.test(password)) {
        setErr("Password must be at least 8 characters long and include at least one letter and one number.");
        return false;
      }
    }

    const incomeValue = parseFloat(monthlyIncome);
    if (isNaN(incomeValue) || incomeValue < 0) {
      setErr("Monthly income must be a non-negative number.");
      return false;
    }

    setErr(""); // clear error if valid
    return true;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!validateInputs()) return;

    try {
      const resp = await httpClient.post("/api/register", {
        name,
        email,
        password,
        contactNumber,
        monthlyIncome,
      });
      if (resp.data.authenticated) {
        alert("Registration successful! Please wait for manager approval.");
        navigate("/clienthome");
      }
    } catch (error) {
      const backendError = error.response?.data?.error;
      setErr(backendError || "Registration failed. Please try again.");
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!validateInputs()) return;

    try {
      const resp = await httpClient.put("/api/update_profile", {
        name,
        email,
        password,
        contactNumber,
        monthlyIncome,
      });
      alert("Profile updated successfully!");
      navigate("/profile", {state:{user_email:email}});
    } catch (error) {
      const backendError = error.response?.data?.error;
      setErr(backendError || "Update failed. Please try again.");
    }
  };

return (
  <div className="register-page">
    <button className="icon-btn back-btn" onClick={() => navigate(-1)}>
      <FaArrowLeft />
    </button>

    <div className="register-card">
      <img src={logo} alt="CareConnect Logo" className="register-logo" />
        <h2 className="register-title">
          {registering
            ? "Join CareConnect"
            : (updating ? "Edit Profile" : "Complete Profile")}    
        </h2>
        <p className="register-subtitle">
          {registering
            ? "Create your account to start connecting, giving, and receiving care."
            : ""}       
        </p>
      {err && <p className="error-message">{err}</p>}

      <form
        onSubmit={registering ? handleRegister : handleUpdate}
        className="register-form"
      >
        <input
          required
          type="text"
          placeholder="Full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="register-input"
        />
        <input
          required
          type="text"
          placeholder="Contact number"
          value={contactNumber}
          onChange={(e) => setContactNumber(e.target.value)}
          className="register-input"
        />
        <input
          required
          type="number"
          min="0"
          step="0.01"
          placeholder="Monthly income"
          value={monthlyIncome}
          onChange={(e) => setMonthlyIncome(e.target.value)}
          className="register-input"
        />

        {!useGmail && (
          <>
            <input
              required
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="register-input"
            />
            <input
              required
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="register-input"
            />
          </>
        )}

        <button
          type="submit"
          className={`register-btn ${
            registering ? "register-btn-primary" : "register-btn-secondary"
          }`}
        >
          {registering ? "Create account" : "Save profile"}
        </button>
      </form>
    </div>
  </div>
  )
}

