import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, Eye, EyeOff, Hexagon } from 'lucide-react';
import './Login.css';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    organization_name: '',
    role: 'employee',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const user = await login(formData.email, formData.password);
        navigate(user.role === 'admin' || user.role === 'super_admin' ? '/organization' : '/employee');
      } else {
        await register(formData);
        setIsLogin(true);
        setError('');
        alert('Registration successful! Please login.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Floating 3D Background Objects */}
      <div className="background-objects">
        {/* ... objects ... */}
        <div className="obj sphere sphere-1"></div>
        <div className="obj sphere sphere-2"></div>
        <div className="obj sphere sphere-3"></div>
        <div className="obj cube cube-1">
          <div className="face front"></div>
          <div className="face back"></div>
          <div className="face right"></div>
          <div className="face left"></div>
          <div className="face top"></div>
          <div className="face bottom"></div>
        </div>
        <div className="obj cube cube-2">
          <div className="face front"></div>
          <div className="face back"></div>
          <div className="face right"></div>
          <div className="face left"></div>
          <div className="face top"></div>
          <div className="face bottom"></div>
        </div>
        <div className="obj prism prism-1"></div>
        <div className="obj prism prism-2"></div>
      </div>

      <div className="glass-card">
        <div className="card-content">
          <div className="header">
            <h1>EMPLOYEE MONITORING<br />DASHBOARD</h1>
            <p className="subtitle">{isLogin ? 'Welcome Back' : 'Create New Account'}</p>
          </div>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit} className="login-form">
            {!isLogin && (
              <>
                <div className="input-group">
                  <label>Full Name</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder=" "
                      required
                      style={{ paddingLeft: '16px' }} 
                    />
                    <div className="input-highlight"></div>
                  </div>
                </div>

                <div className="input-group">
                  <label>Organization Name</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="organization_name"
                      value={formData.organization_name}
                      onChange={handleChange}
                      placeholder=" "
                      required
                      style={{ paddingLeft: '16px' }}
                    />
                    <div className="input-highlight"></div>
                  </div>
                </div>
              </>
            )}

            <div className="input-group">
              <label>Email Address</label>
              <div className="input-wrapper">
                <Mail className="input-icon" size={18} />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder=" "
                  required
                />
                <div className="input-highlight"></div>
              </div>
            </div>

            <div className="input-group">
              <label>Password</label>
              <div className="input-wrapper">
                <Lock className="input-icon" size={18} />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder=" "
                  required
                />
                <button 
                  type="button" 
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
                <div className="input-highlight"></div>
              </div>
            </div>

            {!isLogin && (
              <div className="input-group">
                <label>Role</label>
                <div className="input-wrapper">
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="custom-select"
                  >
                    <option value="employee">Employee</option>
                    <option value="admin">Admin (Manager)</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>
              </div>
            )}

            {isLogin && (
              <div className="forgot-password">
                <a href="#">Forgot Password?</a>
              </div>
            )}

            <button type="submit" className="login-btn" disabled={loading}>
              <span className="btn-text">
                {loading ? 'PROCESSING...' : (isLogin ? 'LOGIN' : 'REGISTER')}
              </span>
              <div className="btn-glow"></div>
            </button>

            <div className="toggle-mode">
              <p>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button 
                  type="button" 
                  className="toggle-btn"
                  onClick={() => setIsLogin(!isLogin)}
                >
                  {isLogin ? 'Register' : 'Login'}
                </button>
              </p>
            </div>
          </form>

          <div className="footer-logo">
            <Hexagon size={20} fill="currentColor" />
            <span>EMD</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
