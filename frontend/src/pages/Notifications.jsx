import { useEffect, useState } from "react";
import httpClient from "../httpClient";

export default function Notifications() {
    const [cc, setCc] = useState("");
    const [subs, setSubs] = useState([]);
    const [notes, setNotes] = useState([]);

    async function load() {
        try {
            const s = await httpClient.get("/api/broadcast/subscriptions");
            setSubs(s.data.subscriptions || []);
            const n = await httpClient.get("/api/notifications");
            setNotes(n.data.notifications || []);
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
    }, []);


    async function subscribe() {
        if (!cc) { alert("Enter a CC name first"); return; }
        await httpClient.post("/api/broadcast/subscribe", { cc });
        setCc("");
        load();
    }

    async function unsubscribe(name) {
        await httpClient.post("/api/broadcast/unsubscribe", { cc: name });
        load();
    }

    return (
        <div className="max-w-xl mx-auto p-4 space-y-6">
            <h2 className="text-2xl font-semibold">CC Broadcasts</h2>

            <div className="flex gap-2">
                <input
                    className="border rounded px-3 py-2 grow"
                    placeholder="Type Community Club name (e.g., Ang Mo Kio CC)"
                    value={cc}
                    onChange={(e) => setCc(e.target.value)}
                />
                <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={subscribe}>
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
                        <li key={n.id} className="border rounded p-3">
                            <div className="text-sm text-gray-500">{new Date(n.created_at).toLocaleString()}</div>
                            <div className="mt-1">{n.message}</div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )            
}