
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";

import Login from "./pages/MainUI/Login.jsx";
import Register from "./pages/ClientUI/RegisterForm.jsx";
import Profile from "./pages/MainUI/Profile.jsx";
import ManagerHome from "./pages/ManagerUI/ManagerHome.jsx";
import ClientHome from "./pages/ClientUI/ClientHome.jsx";
import ManagerAction from "./pages/ManagerUI/ManagerAction.jsx";
import ManageRegistrations from "./pages/ManagerUI/ManageRegistrations.jsx";
import RequestsList from "./pages/ClientUI/RequestsList.jsx";
import RequestForm from "./pages/ClientUI/RequestForm.jsx";
import DonationsList from "./pages/ClientUI/DonationsList.jsx";
import DonationForm from "./pages/ClientUI/DonationForm.jsx";
import ManageDonations from "./pages/ManagerUI/ManageDonations.jsx";
import CompleteRequest from "./pages/ManagerUI/CompleteRequest.jsx";
import Notifications from "./pages/MainUI/Notifications.jsx";
import ManagerDashboard from "./pages/ManagerUI/ManagerDashboard.jsx";
import ClientDashboard from "./pages/ClientUI/ClientDashboard.jsx";
import Subscriptions from "./pages/MainUI/Subscriptions.jsx";

export default function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />}/>
        <Route path="/managerhome" element={<ManagerHome/>} />
        <Route path="/clienthome" element={<ClientHome/>} />
        <Route path="/managerAction" element={<ManagerAction/>} />
        <Route path="/manageRegistrations" element={<ManageRegistrations/>} />
        <Route path="/manageDonations" element={<ManageDonations/>} />
        <Route path="/myRequests" element={<RequestsList/>} />
        <Route path="/requestForm" element={<RequestForm/>} />
        {/* edit mode uses :id */}
        <Route path="/requests/:id/edit" element={<RequestForm />} />
        <Route path="/myDonations" element={<DonationsList/>} />
        <Route path="/donationForm" element={<DonationForm/>} />
        {/* edit mode uses :id */}
        <Route path="/donations/:id/edit" element={<DonationForm />} />
        <Route path="/completeRequests" element={<CompleteRequest/>} />
        <Route path="/notification" element={<Notifications/>} />
        <Route path="/managerDashboard" element={<ManagerDashboard/>}/>
        <Route path="/clientDashboard" element={<ClientDashboard/>}/>
        <Route path="/subscriptions" element={<Subscriptions/>}/>
      </Routes>
    </BrowserRouter>
  );
};
