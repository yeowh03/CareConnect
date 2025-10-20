import httpClient from "../httpClient";
import { useNavigate } from "react-router-dom";

function TopNav({role}) {
    const navigate = useNavigate();

    const handleProfile = async () => {
        try {
            const resp = await httpClient.get("/api/@me");
            navigate('/profile', { state: { user_email: resp.data.email } });
        } catch (error) {
            if (error.response?.status === 401) {
            alert("Invalid credentials");
            }else{
            alert(error.message);
            }
        }
    }

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

    if (role === "Manager"){
        return (
            <nav className="top-nav">
                <div className="nav-buttons">
                    <button onClick={() => navigate('/home')}>Home</button>
                    <button onClick={() => handleProfile()}>Profile</button>
                    <button onClick={() => navigate('/notification')}>Notification</button>
                    <button onClick={() => navigate('/managerAction')}>Action</button>
                    <button onClick={() => handlelogout()}>Log Out</button>
                </div>
            </nav>
        );
    } else {
        return (
            <nav className="top-nav">
                <div className="nav-buttons">
                    <button onClick={() => navigate('/home')}>Home</button>
                    <button onClick={() => handleProfile()}>Profile</button>
                    <button onClick={() => navigate('/notification')}>Notification</button>
                    <button onClick={() => navigate('/myRequests')}>Requests</button>
                    <button onClick={() => navigate('/myDonations')}>Donations</button>
                    <button onClick={() => navigate('/inventory')}>Inventory</button>
                    <button onClick={() => handlelogout()}>Log Out</button>
                </div>
            </nav>
        )
    }
}

export default TopNav;