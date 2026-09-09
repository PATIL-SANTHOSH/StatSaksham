import React, { useState, useEffect } from 'react';
import { employeeAPI } from '../services/api';
import { 
  Users, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  ChevronDown 
} from 'lucide-react';

const AdminEmployees = () => {
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('All');
  const [loading, setLoading] = useState(true);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const res = await employeeAPI.list({
        page,
        page_size: pageSize,
        department: department === 'All' ? null : department,
        search: search.trim() || null
      });
      setEmployees(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Error fetching employee directory:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [page, department]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchEmployees();
  };

  const departments = [
    'All',
    'National Accounts Division',
    'Price Statistics Division',
    'Field Operations Division',
    'Survey Design & Research Division',
    'Social Statistics Division',
    'Economic Statistics Division',
    'Data Informatics & Innovation Division',
    'Coordination and Publication Division'
  ];

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Statistical Cadre Directory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Total of {total} synthetic statistical officers and administrators across MoSPI divisions.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or ID..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200/90 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 shadow-2xs transition"
          />
        </form>
      </div>

      {/* Division Selector Filter */}
      <div className="flex items-center space-x-2 text-xs">
        <span className="text-slate-400 font-bold uppercase text-[10px]">Division:</span>
        <select
          value={department}
          onChange={(e) => {
            setDepartment(e.target.value);
            setPage(1);
          }}
          className="px-3 py-1.5 bg-white border border-slate-200/90 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-600 focus:outline-none shadow-2xs"
        >
          {departments.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Employee Table Card */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-2xs overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[300px]">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-xs text-slate-500 mt-2 font-semibold">Loading Employee Records...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200/90 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                  <th className="py-3.5 px-5">Employee ID</th>
                  <th className="py-3.5 px-5">Officer Name</th>
                  <th className="py-3.5 px-5">Department / Division</th>
                  <th className="py-3.5 px-5">Designation & Role</th>
                  <th className="py-3.5 px-5">Operational Focus</th>
                  <th className="py-3.5 px-5 text-center">Exp</th>
                  <th className="py-3.5 px-5 text-right">Cadre</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {employees.map((emp) => (
                  <tr key={emp.employee_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-5 font-mono font-bold text-slate-900">
                      {emp.employee_id}
                    </td>
                    <td className="py-3.5 px-5 font-bold text-slate-900">
                      <div>{emp.name}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{emp.email}</div>
                    </td>
                    <td className="py-3.5 px-5 text-slate-700 font-medium">
                      {emp.department}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="font-bold text-slate-800">{emp.designation}</div>
                      <div className="text-[10px] text-blue-700 font-bold">{emp.job_role}</div>
                    </td>
                    <td className="py-3.5 px-5 text-slate-600 max-w-xs truncate font-medium">
                      {emp.current_assignment}
                    </td>
                    <td className="py-3.5 px-5 text-center font-black text-slate-700">
                      {emp.years_of_experience}y
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                        emp.role === 'ADMIN' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {emp.role}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span className="font-medium">
            Page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total} total personnel)
          </span>

          <div className="flex space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 rounded-xl font-bold flex items-center space-x-1"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 rounded-xl font-bold flex items-center space-x-1"
            >
              <span>Next</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminEmployees;
