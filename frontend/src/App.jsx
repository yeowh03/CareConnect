
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";

import Home from "./pages/ManagerHome.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/RegisterForm.jsx";
import Profile from "./pages/Profile.jsx";
import ManagerHome from "./pages/ManagerHome.jsx";
import ClientHome from "./pages/ClientHome.jsx";
import ManagerAction from "./pages/ManagerAction.jsx";
import ManageRegistrations from "./pages/ManageRegistrations.jsx";
import RequestsList from "./pages/RequestsList.jsx";
import RequestForm from "./pages/RequestForm.jsx";
import DonationsList from "./pages/DonationsList.jsx";
import DonationForm from "./pages/DonationForm.jsx";
import ManageDonations from "./pages/ManageDonations.jsx";
import CompleteRequest from "./pages/CompleteRequest.jsx";
import Notifications from "./pages/Notifications.jsx";
import ManagerDashboard from "./pages/ManagerDashboard.jsx";
import ClientDashboard from "./pages/ClientDashboard.jsx";
import Subscriptions from "./pages/Subscriptions.jsx";

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
        {/* ⬇ same component, edit mode uses :id */}
        <Route path="/requests/:id/edit" element={<RequestForm />} />
        <Route path="/myDonations" element={<DonationsList/>} />
        <Route path="/donationForm" element={<DonationForm/>} />
        {/* ⬇ same component, edit mode uses :id */}
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
