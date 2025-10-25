// import { useEffect, useState } from "react";
// import httpClient from "../httpClient";
// import { useLocation, useNavigate } from "react-router-dom";

// export default function Profile() {
//   const [profile, setProfile] = useState(null);
//   const navigate = useNavigate();
//   const location = useLocation();

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const resp = await httpClient.get("/api/@me");
//         console.log("abcdfeff");
//         console.log(location.state.user_email);
//         let pf;
//         if (resp.data.role == "C"){
//           pf = await httpClient.get(`/api/get_ClientProfile/${location.state.user_email}`);
//         } else {
//           pf = await httpClient.get(`/api/get_ManagerProfile/${location.state.user_email}`);
//         }
//         setProfile(pf.data);     
//       } catch (error) {
//         alert("Not authenticated");
//         navigate("/login");
//       }
//     };
//     fetchData();
//   }, []);

//   const handlelogout = async () => {
//     try {
//         const resp = await httpClient.post("/api/logout");
//         navigate("/");
//     } catch (error) {
//         if (error.response?.status === 401) {
//         alert("Invalid credentials");
//         }else{
//         alert(error.message);
//         }
//     }
//   }

//   const handleEdit = async() => {
//     navigate("/register", {state:{profile:profile}} )
//   }

//   if (!profile) return <div>Loading profile...</div>;

//   return (
//     <>
//       <div>
//         {!profile.profile_complete && (
//           <div style={{ background: "#fff8e1", padding: 12, borderRadius: 10, marginBottom: 12 }}>
//             Your profile is incomplete. Please fill it in on the <button onClick={handleEdit}>registration</button> page.
//           </div>
//         )}
//         <div>
//           <div><p>{profile.account_status}</p></div>
//           <div>
//             <h1 style={{ margin: 0 }}>{profile.name || "Unnamed user"}</h1>
//             <div>{profile.email}</div>
//           </div>
//         </div>
//         <div style={{ height: 16 }} />
//         <div><b>Contact:</b> {profile.contact_number || "-"}</div>
//         {profile.role=="C" &&
//           <div><b>Monthly income:</b> {profile.monthly_income != null ? profile.monthly_income : "-"}</div>
//         }
//         <div style={{ height: 16 }} />
//         {profile.role=="M" && 
//           <div><b>CC:</b> {profile.cc}</div>
//         }
//         {profile.role=="C" && 
//           <div>
//             <button onClick={handleEdit}>Edit Profile</button>
//           </div>
//         }
//         <button onClick={handlelogout}>
//           Log out
//         </button>
//       </div>
//     </>
//   );
// }

// src/pages/Profile.jsx
import { useEffect, useState } from "react";
import httpClient from "../httpClient";
import { useLocation, useNavigate } from "react-router-dom";
import TopNav from "./TopNav";
import "../styles/Profile.css";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [role, setRole] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("/api/@me");
        console.log("abcdfeff");
        console.log(location.state.user_email);
        setRole(resp.data.role);
        let pf;
        if (resp.data.role == "C") {
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
      } else {
        alert(error.message);
      }
    }
  };

  const handleEdit = async () => {
    navigate("/register", { state: { profile: profile } });
  };

  if (!profile) return <div className="profile-loading">Loading profile...</div>;

  // Small helper for avatar initial (UI-only)
  const initial = profile?.name ? profile.name.charAt(0).toUpperCase() : "U";

  return (
    <>
      {role && <TopNav role={role == "M" ? "Manager" : "Client"} />}

      <div className="profile-page">
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar" aria-hidden>
              {initial}
            </div>
            <div className="profile-info">
              <div className="profile-status">{profile.account_status}</div>
              <h1 className="profile-name">{profile.name || "Unnamed user"}</h1>
              <div className="profile-email">{profile.email}</div>
            </div>
            <div className="profile-actions">
              {profile.role === "C" && (
                <button className="btn btn-edit" onClick={handleEdit}>
                  Edit Profile
                </button>
              )}
              <button className="btn btn-logout" onClick={handlelogout}>
                Log out
              </button>
            </div>
          </div>

          <div className="profile-body">
            <div className="profile-row">
              <div className="profile-label">Contact</div>
              <div className="profile-value">{profile.contact_number || "-"}</div>
            </div>

            {profile.role == "C" && (
              <div className="profile-row">
                <div className="profile-label">Monthly income</div>
                <div className="profile-value">
                  {profile.monthly_income != null ? profile.monthly_income : "-"}
                </div>
              </div>
            )}

            {profile.role == "M" && (
              <div className="profile-row">
                <div className="profile-label">CC</div>
                <div className="profile-value">{profile.cc}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}