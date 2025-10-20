import { useEffect, useState } from "react";
import httpClient from "../httpClient";
import { useLocation, useNavigate } from "react-router-dom";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        console.log("abcdfeff");
        console.log(location.state.user_email);
        let pf;
        if (resp.data.role == "C"){
          pf = await httpClient.get(`/api/get_ClientProfile/${location.state.user_email}`);
        } else {
          pf = await httpClient.get(`/api/get_ManagerProfile/${location.state.user_email}`);
        }
        setProfile(pf.data);     
      } catch (error) {
        alert("Not authenticated");
        navigate("/login");
      }
    };
    fetchData();
  }, []);

  const handlelogout = async () => {
    try {
        const resp = await httpClient.post("/api/logout");
        navigate("/");
    } catch (error) {
        if (error.response?.status === 401) {
        alert("Invalid credentials");
        }else{
        alert(error.message);
        }
    }
  }

  const handleEdit = async() => {
    navigate("/register", {state:{profile:profile}} )
  }

  if (!profile) return <div>Loading profile...</div>;

  return (
    <>
      <div>
        {!profile.profile_complete && (
          <div style={{ background: "#fff8e1", padding: 12, borderRadius: 10, marginBottom: 12 }}>
            Your profile is incomplete. Please fill it in on the <button onClick={handleEdit}>registration</button> page.
          </div>
        )}
        <div>
          <div><p>{profile.account_status}</p></div>
          <div>
            <h1 style={{ margin: 0 }}>{profile.name || "Unnamed user"}</h1>
            <div>{profile.email}</div>
          </div>
        </div>
        <div style={{ height: 16 }} />
        <div><b>Contact:</b> {profile.contact_number || "-"}</div>
        {profile.role=="C" &&
          <div><b>Monthly income:</b> {profile.monthly_income != null ? profile.monthly_income : "-"}</div>
        }
        <div style={{ height: 16 }} />
        {profile.role=="M" && 
          <div><b>CC:</b> {profile.cc}</div>
        }
        {profile.role=="C" && 
          <div>
            <button onClick={handleEdit}>Edit Profile</button>
          </div>
        }
        <button onClick={handlelogout}>
          Log out
        </button>
      </div>
    </>
  );
}

