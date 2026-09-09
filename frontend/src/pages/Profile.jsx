import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { employeeAPI } from '../services/api';
import { 
  User, 
  Edit3, 
  Save, 
  CheckCircle2, 
  Camera, 
  Briefcase, 
  Building2, 
  Mail, 
  Phone, 
  Award,
  ShieldCheck
} from 'lucide-react';

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingInterests, setIsEditingInterests] = useState(false);
  const [interests, setInterests] = useState(['Data Analysis', 'Machine Learning', 'Survey Design', 'National Accounts']);
  const [newInterestInput, setNewInterestInput] = useState('');
  
  const [formData, setFormData] = useState({
    current_assignment: '',
    education: '',
    previous_trainings: '',
    competency_domain: ''
  });
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (!user) return;
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const res = await employeeAPI.getById(user.employee_id);
        setProfile(res.data);
        setFormData({
          current_assignment: res.data.current_assignment || '',
          education: res.data.education || '',
          previous_trainings: res.data.previous_trainings || '',
          competency_domain: res.data.competency_domain || 'Statistical'
        });
      } catch (err) {
        console.error('Error fetching employee profile:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [user]);

  const handleSave = async (e) => {
    if (e) e.preventDefault();
    try {
      const res = await employeeAPI.update(user.employee_id, formData);
      setProfile(res.data);
      setIsEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert('Error updating profile information.');
    }
  };

  const handleAddInterest = () => {
    if (newInterestInput.trim() && !interests.includes(newInterestInput.trim())) {
      setInterests([...interests, newInterestInput.trim()]);
      setNewInterestInput('');
    }
  };

  const handleRemoveInterest = (item) => {
    setInterests(interests.filter(i => i !== item));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Profile Record...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">My Profile</h1>
        <p className="text-xs text-slate-500 mt-0.5">View and manage your profile information.</p>
      </div>

      {saveSuccess && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold rounded-2xl flex items-center space-x-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
          <span>Profile information successfully updated and synced with competency matrix.</span>
        </div>
      )}

      {/* Main 2-Column Grid: Avatar Card + Employee Details Card */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Column: Avatar Card */}
        <div className="md:col-span-4 bg-white rounded-3xl p-8 border border-slate-200/90 shadow-2xs flex flex-col items-center justify-center text-center space-y-4">
          <div className="relative">
            <div className="h-28 w-28 rounded-full bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-800 text-white font-black text-3xl flex items-center justify-center shadow-lg border-4 border-white">
              {profile?.name ? profile.name.charAt(0) : 'R'}
            </div>
            <button
              onClick={() => alert('Photo upload enabled for MoSPI SSO profiles.')}
              className="absolute bottom-0 right-0 p-2 bg-white rounded-full shadow-md border border-slate-200 text-slate-600 hover:text-blue-600 transition"
              title="Change Photo"
            >
              <Camera className="h-4 w-4" />
            </button>
          </div>

          <div>
            <h2 className="text-lg font-black text-slate-900">{profile?.name}</h2>
            <p className="text-xs font-bold text-slate-600 mt-0.5">{profile?.designation}</p>
            <p className="text-[11px] text-slate-500">{profile?.department}</p>
            <p className="text-[10px] text-slate-400 font-medium">MoSPI, Government of India</p>
          </div>

          <button
            onClick={() => alert('Photo upload active via SSO.')}
            className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl border border-slate-200 shadow-2xs transition"
          >
            Change Photo
          </button>
        </div>

        {/* Right Column: Employee Details Card */}
        <div className="md:col-span-8 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="font-extrabold text-sm text-slate-900">Employee Details</h3>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="inline-flex items-center space-x-1.5 px-3 py-1 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-lg border border-slate-200 transition shadow-2xs"
              >
                <Edit3 className="h-3 w-3 text-slate-500" />
                <span>{isEditing ? 'Cancel' : 'Edit'}</span>
              </button>
            </div>

            {/* Grid of Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-6 pt-5 text-xs">
              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Employee ID</span>
                <span className="font-bold text-slate-900">{profile?.employee_id}</span>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Email</span>
                <span className="font-bold text-slate-900">{profile?.email}</span>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Mobile</span>
                <span className="font-bold text-slate-900">+91 98765 43210</span>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Department</span>
                <span className="font-bold text-slate-900">{profile?.department}</span>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Designation</span>
                <span className="font-bold text-slate-900">{profile?.designation}</span>
              </div>

              <div>
                <span className="text-slate-400 font-semibold block text-[11px]">Role</span>
                <span className="font-bold text-blue-700">{profile?.role === 'ADMIN' ? 'Administrator' : 'Learner'}</span>
              </div>

              <div className="sm:col-span-2 pt-2">
                <span className="text-slate-400 font-semibold block text-[11px]">Current Operational Assignment</span>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.current_assignment}
                    onChange={(e) => setFormData({ ...formData, current_assignment: e.target.value })}
                    className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                ) : (
                  <span className="font-bold text-slate-800">{profile?.current_assignment}</span>
                )}
              </div>
            </div>
          </div>

          {isEditing && (
            <div className="pt-4 mt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={handleSave}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow transition flex items-center space-x-1.5"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Save Changes</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Card: Areas of Interest */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-extrabold text-sm text-slate-900">Areas of Interest</h3>
          <button
            onClick={() => setIsEditingInterests(!isEditingInterests)}
            className="px-3 py-1 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-lg border border-slate-200 transition shadow-2xs"
          >
            {isEditingInterests ? 'Done' : 'Edit Interests'}
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {interests.map((item, idx) => (
            <span
              key={idx}
              className="px-3.5 py-1.5 bg-blue-50 text-blue-700 font-semibold text-xs rounded-xl border border-blue-100 flex items-center space-x-1.5"
            >
              <span>{item}</span>
              {isEditingInterests && (
                <button
                  onClick={() => handleRemoveInterest(item)}
                  className="text-blue-400 hover:text-rose-600 font-bold ml-1"
                >
                  ×
                </button>
              )}
            </span>
          ))}
        </div>

        {isEditingInterests && (
          <div className="flex items-center space-x-2 pt-2">
            <input
              type="text"
              value={newInterestInput}
              onChange={(e) => setNewInterestInput(e.target.value)}
              placeholder="Add new competency interest..."
              className="px-3.5 py-1.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
            <button
              onClick={handleAddInterest}
              className="px-3.5 py-1.5 bg-blue-600 text-white font-bold text-xs rounded-xl shadow-xs"
            >
              Add
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
