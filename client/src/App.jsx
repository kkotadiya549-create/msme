import React, { useState, useEffect } from 'react';

function App() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({ openTickets: 0, highPriority: 0, messagesProcessed: 0 });
  const [loading, setLoading] = useState(true);

  // In production, the API and client run on the same origin
  const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch Tickets
      const ticketsRes = await fetch(`${API_BASE}/tickets`);
      const ticketsData = await ticketsRes.json();
      setTickets(ticketsData);

      // Calculate simple stats from tickets
      const openCount = ticketsData.filter(t => t.status === 'open' || t.status === 'in_progress').length;
      const highCount = ticketsData.filter(t => t.priority === 'high' && t.status !== 'resolved').length;

      setStats({
        openTickets: openCount,
        highPriority: highCount,
        messagesProcessed: 'N/A (Check DB or Digest)'
      });

    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const markResolved = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/tickets/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'resolved' })
      });
      if (res.ok) {
        fetchData(); // Refresh list
      }
    } catch (error) {
      console.error("Error updating ticket:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Factory Monitoring Dashboard</h1>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
            <h3 className="text-gray-500 text-sm font-semibold uppercase">Open Tickets</h3>
            <p className="text-3xl font-bold text-gray-800">{stats.openTickets}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-red-500">
            <h3 className="text-gray-500 text-sm font-semibold uppercase">High Priority (Open)</h3>
            <p className="text-3xl font-bold text-gray-800">{stats.highPriority}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
            <h3 className="text-gray-500 text-sm font-semibold uppercase">System Status</h3>
            <p className="text-xl font-bold text-gray-800 mt-2">Online</p>
          </div>
        </div>

        {/* Tickets Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-800">Recent Tickets</h2>
            <button onClick={fetchData} className="text-sm text-blue-600 hover:text-blue-800">Refresh</button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Machine</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type / Priority</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr><td colSpan="5" className="px-6 py-4 text-center text-gray-500">Loading tickets...</td></tr>
                ) : tickets.length === 0 ? (
                  <tr><td colSpan="5" className="px-6 py-4 text-center text-gray-500">No tickets found.</td></tr>
                ) : (
                  tickets.map((ticket) => (
                    <tr key={ticket._id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        Machine {ticket.machineId}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="capitalize">{ticket.actionType.replace('_', ' ')}</div>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mt-1 ${ticket.priority === 'high' ? 'bg-red-100 text-red-800' : ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                          {ticket.priority}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${ticket.status === 'resolved' ? 'bg-gray-100 text-gray-800' : 'bg-blue-100 text-blue-800'}`}>
                          {ticket.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(ticket.createdAt).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {ticket.status !== 'resolved' && (
                          <button
                            onClick={() => markResolved(ticket._id)}
                            className="text-white bg-indigo-600 hover:bg-indigo-700 px-3 py-1 rounded shadow-sm text-xs transition-colors"
                          >
                            Mark Resolved
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
