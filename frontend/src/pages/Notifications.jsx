import { useEffect, useState } from "react";
import httpClient from "../httpClient";
import { useNavigate } from "react-router-dom";

export default function Notifications() {
  const navigate = useNavigate(); // ✅ you were using navigate but hadn't created it

  const [cc, setCc] = useState("");
  const [subs, setSubs] = useState([]);
  const [notes, setNotes] = useState([]);
  const [names, setNames] = useState([]);

  async function load() {
    try {
      const s = await httpClient.get("/api/broadcast/subscriptions");
      setSubs(s.data.subscriptions || []);

      const n = await httpClient.get("/api/notifications");
      setNotes(n.data.notifications || []);

      const c = await httpClient.get("/api/community-clubs");
      const markers = c.data?.markers || [];

      // ✅ collect names from marker objects, dedupe, sort
      const collected = Array.from(
        new Set(
          markers
            .map((m) => m?.name)
            .filter(Boolean) // remove null/undefined/empty
        )
      ).sort((a, b) => a.localeCompare(b));

      setNames(collected);
    } catch (e) {
      console.error(e);
      alert("Please log in to see notifications");
    }
  }

  useEffect(() => {
    const run = async () => {
      try {
        await httpClient.get("/api/@me");
      } catch {
        alert("Not authenticated");
        navigate("/login");
        return;
      }
      load();
    };

    run();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, [navigate]);

  async function subscribe() {
    if (!cc) { alert("Choose a CC first"); return; }
    await httpClient.post("/api/broadcast/subscribe", { cc });
    setCc("");
    load();
  }

  async function unsubscribe(name) {
    await httpClient.post("/api/broadcast/unsubscribe", { cc: name });
    load();
  }

  async function deleteNote(id) {
    try {
      await httpClient.delete(`/api/notifications/${id}`);
      setNotes((curr) => curr.filter((n) => n.id !== id));
    } catch (e) {
      console.error(e);
      alert("Failed to delete notification");
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 space-y-6">
      <h2 className="text-2xl font-semibold">CC Broadcasts</h2>
      
      <div className="flex gap-2">
        <select
          className="border rounded px-3 py-2 grow"
          value={cc}
          onChange={(e) => setCc(e.target.value)}
        >
          <option value="">{names.length ? "Select a Community Club…" : "Loading CC names…"}</option>
          {names.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>

        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={subscribe}
          disabled={!cc}
          title={cc ? "Subscribe" : "Choose a CC first"}
        >
          Subscribe
        </button>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-2">Your Subscriptions</h3>
        {subs.length === 0 && <p className="text-sm text-gray-600">None yet.</p>}
        <ul className="space-y-2">
          {subs.map((s) => (
            <li key={s.id} className="border rounded p-3 flex items-center justify-between">
              <span className="font-medium">{s.cc}</span>
              <button className="text-red-600" onClick={() => unsubscribe(s.cc)}>
                Unsubscribe
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-2">Notifications</h3>
        {notes.length === 0 && <p className="text-sm text-gray-600">No notification yet.</p>}
        <ul className="space-y-2">
          {notes.map((n) => (
            <li key={n.id} className="border rounded p-3 relative">
              <button
                onClick={() => deleteNote(n.id)}
                className="absolute right-2 top-2 px-2 leading-none text-gray-500 hover:text-red-600"
                aria-label="Delete notification"
                title="Delete"
              >
                ×
              </button>

              <div className="text-sm text-gray-500">
                {new Date(n.created_at).toLocaleString()}
              </div>
              <div className="mt-1">{n.message}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
