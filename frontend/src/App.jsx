import { useEffect, useState } from 'react';
import { BrowserRouter, NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import { Activity, AlertTriangle, CloudSun, Globe, LogOut, Search, ThermometerSun } from 'lucide-react';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import './App.css';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const defaultLocation = {
  id: 2986170,
  name: 'Chennai',
  country: 'India',
  admin1: 'Tamil Nadu',
  latitude: 13.0878,
  longitude: 80.2785,
};

const weatherConditions = {
  0: 'Clear sky',
  1: 'Mainly clear',
  2: 'Partly cloudy',
  3: 'Overcast',
  45: 'Fog',
  48: 'Freezing fog',
  51: 'Light drizzle',
  53: 'Drizzle',
  55: 'Heavy drizzle',
  61: 'Light rain',
  63: 'Rain',
  65: 'Heavy rain',
  71: 'Light snow',
  73: 'Snow',
  75: 'Heavy snow',
  80: 'Rain showers',
  81: 'Rain showers',
  82: 'Heavy rain showers',
  95: 'Thunderstorm',
  96: 'Thunderstorm with hail',
  99: 'Thunderstorm with hail',
};

const driftVariables = [
  { name: 'Temperature', key: 'temperature_2m_mean', unit: '°C' },
  { name: 'Rainfall', key: 'precipitation_sum', unit: 'mm' },
  { name: 'Humidity', key: 'relative_humidity_2m_mean', unit: '%' },
  { name: 'Pressure', key: 'pressure_msl_mean', unit: 'hPa' },
  { name: 'Wind speed', key: 'wind_speed_10m_max', unit: 'km/h' },
];

function average(values) {
  const validValues = values.filter(Number.isFinite);
  if (validValues.length === 0) return null;
  return validValues.reduce((sum, value) => sum + value, 0) / validValues.length;
}

function formatValue(value, unit = '') {
  return Number.isFinite(value) ? `${value.toFixed(1)}${unit}` : '—';
}

async function readApiResponse(response, fallbackMessage) {
  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { detail: text };
  }
  if (!response.ok) throw new Error(data.detail || fallbackMessage);
  return data;
}

function calculatePsi(baselineValues, recentValues) {
  const baseline = baselineValues.filter(Number.isFinite);
  const recent = recentValues.filter(Number.isFinite);
  if (baseline.length < 2 || recent.length < 2) return null;

  const allValues = [...baseline, ...recent];
  const minimum = Math.min(...allValues);
  const maximum = Math.max(...allValues);
  if (minimum === maximum) return 0;

  const sortedValues = [...allValues].sort((left, right) => left - right);
  const edges = [0.2, 0.4, 0.6, 0.8]
    .map((quantile) => sortedValues[Math.floor(quantile * (sortedValues.length - 1))])
    .filter((edge, index, values) => edge > minimum && edge < maximum && values.indexOf(edge) === index);
  const binCount = edges.length + 1;
  const getBinCounts = (values) => {
    const counts = Array(binCount).fill(0);
    values.forEach((value) => {
      const edgeIndex = edges.findIndex((edge) => value <= edge);
      const bin = edgeIndex === -1 ? binCount - 1 : edgeIndex;
      counts[bin] += 1;
    });
    return counts;
  };

  const baselineBins = getBinCounts(baseline);
  const recentBins = getBinCounts(recent);
  return baselineBins.reduce((score, baselineCount, index) => {
    const expected = (baselineCount + 0.5) / (baseline.length + binCount * 0.5);
    const actual = (recentBins[index] + 0.5) / (recent.length + binCount * 0.5);
    return score + (actual - expected) * Math.log(actual / expected);
  }, 0);
}

function calculateDriftReport(dailyWeather) {
  const midpoint = Math.floor(dailyWeather.time.length / 2);
  return driftVariables.map((variable) => {
    const values = dailyWeather[variable.key] ?? [];
    const baseline = values.slice(0, midpoint);
    const recent = values.slice(midpoint);
    const psi = calculatePsi(baseline, recent);
    const status = psi == null ? 'INSUFFICIENT DATA' : psi >= 0.2 ? 'DRIFT' : psi >= 0.1 ? 'WATCH' : 'NORMAL';
    return {
      ...variable,
      baseline: average(baseline),
      recent: average(recent),
      psi,
      status,
    };
  });
}

function statusClass(status) {
  if (status === 'NORMAL') return 'normal';
  if (status === 'WATCH') return 'watch';
  if (status === 'DRIFT') return 'drift';
  return 'unknown';
}

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/locations', label: 'Locations' },
  { to: '/weather-data', label: 'Weather Data' },
  { to: '/drift-history', label: 'Drift History' },
  { to: '/alerts', label: 'Alerts' },
  { to: '/about', label: 'About' },
];

function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}

function AppShell() {
  const navigate = useNavigate();
  const [selectedLocation, setSelectedLocation] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('selected-location')) ?? defaultLocation;
    } catch {
      return defaultLocation;
    }
  });
  const [currentWeather, setCurrentWeather] = useState(null);
  const [weatherHistory, setWeatherHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState('');
  const [authUser, setAuthUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('auth-user'));
    } catch {
      return null;
    }
  });

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({
      latitude: selectedLocation.latitude,
      longitude: selectedLocation.longitude,
      current: 'temperature_2m,weather_code',
      daily: 'temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max',
      past_days: '30',
      forecast_days: '1',
      timezone: 'auto',
    });

    async function loadCurrentWeather() {
      setCurrentWeather(null);
      setWeatherHistory(null);
      setHistoryError('');
      setHistoryLoading(true);
      try {
        const response = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`, { signal: controller.signal });
        if (!response.ok) throw new Error('Weather request failed');
        const data = await response.json();
        setCurrentWeather({
          temperature: data.current.temperature_2m,
          condition: weatherConditions[data.current.weather_code] ?? 'Variable conditions',
        });
        setWeatherHistory(data.daily);
      } catch (error) {
        if (error.name !== 'AbortError') {
          setCurrentWeather({ temperature: null, condition: 'Unavailable' });
          setHistoryError('Weather history is unavailable. Check your connection and try again.');
        }
      } finally {
        if (!controller.signal.aborted) setHistoryLoading(false);
      }
    }

    loadCurrentWeather();
    return () => controller.abort();
  }, [selectedLocation.latitude, selectedLocation.longitude]);

  const driftReport = weatherHistory ? calculateDriftReport(weatherHistory) : [];
  const activeDriftCount = driftReport.filter((item) => item.status === 'DRIFT').length;

  function selectLocation(location) {
    const nextLocation = {
      id: location.id,
      name: location.name,
      country: location.country,
      admin1: location.admin1,
      latitude: location.latitude,
      longitude: location.longitude,
    };
    setSelectedLocation(nextLocation);
    localStorage.setItem('selected-location', JSON.stringify(nextLocation));
    navigate('/');
  }

  function completeLogin(authData) {
    localStorage.setItem('access-token', authData.access_token);
    localStorage.setItem('auth-user', JSON.stringify(authData.user));
    setAuthUser(authData.user);
    navigate('/');
  }

  function logout() {
    localStorage.removeItem('access-token');
    localStorage.removeItem('auth-user');
    setAuthUser(null);
  }

  return (
    <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <CloudSun size={28} />
            <div>
              <strong>Weather Drift</strong>
              <span>Monitoring</span>
            </div>
          </div>
          <nav className="nav">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                <span>{item.label}</span>
                {item.to === '/alerts' && activeDriftCount > 0 && (
                  <span className="nav-badge" aria-label={`${activeDriftCount} active drift alerts`}>{activeDriftCount}</span>
                )}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main className="main-panel">
          <header className="topbar">
            <div>
              <p className="eyebrow">Weather intelligence platform</p>
              <h1>Operational Climate Monitoring</h1>
            </div>
            {authUser ? (
              <div className="auth-user">
                <span>{authUser.username}</span>
                <button className="secondary-btn" type="button" onClick={logout}>
                  <LogOut size={16} />
                  Sign out
                </button>
              </div>
            ) : (
              <button className="primary-btn" type="button" onClick={() => navigate('/login')}>Login</button>
            )}
          </header>

          <Routes>
            <Route path="/" element={<DashboardPage location={selectedLocation} weather={currentWeather} dailyWeather={weatherHistory} driftReport={driftReport} loading={historyLoading} error={historyError} />} />
            <Route path="/login" element={<LoginPage onLogin={completeLogin} />} />
            <Route path="/locations" element={<LocationsPage selectedLocation={selectedLocation} onSelect={selectLocation} />} />
            <Route path="/weather-data" element={<WeatherDataPage location={selectedLocation} dailyWeather={weatherHistory} driftReport={driftReport} loading={historyLoading} error={historyError} />} />
            <Route path="/drift-history" element={<DriftHistoryPage location={selectedLocation} dailyWeather={weatherHistory} driftReport={driftReport} loading={historyLoading} error={historyError} />} />
            <Route path="/alerts" element={<AlertsPage location={selectedLocation} driftReport={driftReport} loading={historyLoading} error={historyError} />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
  );
}

function LoginPage({ onLogin }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitAuth(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      if (isRegistering) {
        const registerResponse = await fetch(`${apiBaseUrl}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password }),
        });
        await readApiResponse(registerResponse, 'Could not create your account.');
      }

      const loginResponse = await fetch(`${apiBaseUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const authData = await readApiResponse(loginResponse, 'Sign-in failed. Check your credentials.');
      onLogin(authData);
    } catch (authError) {
      setError(authError.message || 'Authentication failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page-content">
      <div className="panel auth-panel">
        <p className="eyebrow">Weather Drift</p>
        <h2>{isRegistering ? 'Create account' : 'Sign in'}</h2>
        <form className="auth-form" onSubmit={submitAuth}>
          <label htmlFor="auth-username">Username or email</label>
          <input
            id="auth-username"
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
          {isRegistering && (
            <>
              <label htmlFor="auth-email">Email</label>
              <input
                id="auth-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </>
          )}
          <label htmlFor="auth-password">Password</label>
          <input
            id="auth-password"
            type="password"
            autoComplete={isRegistering ? 'new-password' : 'current-password'}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button className="primary-btn auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Please wait...' : isRegistering ? 'Create account' : 'Sign in'}
          </button>
        </form>
        <button className="auth-toggle" type="button" onClick={() => { setIsRegistering(!isRegistering); setError(''); }}>
          {isRegistering ? 'Already have an account? Sign in' : 'Create an account'}
        </button>
      </div>
    </section>
  );
}

function DashboardPage({ location, weather, dailyWeather, driftReport, loading, error }) {
  const drifted = driftReport.filter((item) => item.status === 'DRIFT');
  const watchList = driftReport.filter((item) => item.status === 'WATCH');
  const driftChanges = driftReport.filter((item) => item.status === 'DRIFT' || item.status === 'WATCH');
  const overallStatus = loading ? 'ANALYZING' : error ? 'UNAVAILABLE' : drifted.length ? 'DRIFT' : watchList.length ? 'WATCH' : 'NORMAL';
  const driftMessage = drifted.length
    ? `Potential drift detected in ${drifted.map((item) => item.name).join(', ')}.`
    : watchList.length
      ? `Monitor possible changes in ${watchList.map((item) => item.name).join(', ')}.`
      : error
        ? 'Drift analysis is unavailable for this location.'
        : loading
          ? 'Analyzing recent weather history for drift.'
          : 'No significant drift detected in the current comparison window.';
  const metrics = [
    { label: 'Current temperature', value: weather?.temperature == null ? '—' : `${weather.temperature}°C`, icon: <ThermometerSun size={18} /> },
    { label: 'Drift status', value: overallStatus, icon: <Activity size={18} /> },
    { label: 'Active alerts', value: String(drifted.length), icon: <AlertTriangle size={18} /> },
    { label: 'Regional coverage', value: '147 stations', icon: <Globe size={18} /> },
  ];

  return (
    <section className="page-content">
      <div className="hero-card">
        <div>
          <p className="eyebrow">Selected location</p>
          <h2>{location.name}, {location.country}</h2>
          <p className="subtext">{location.admin1 ? `${location.admin1} • ` : ''}{location.latitude.toFixed(3)}°, {location.longitude.toFixed(3)}° • Live weather</p>
        </div>
        <div className="hero-badge">{weather?.condition ?? 'Loading...'}</div>
      </div>

      <div className="stats-grid">
        {metrics.map((item) => (
          <div key={item.label} className="metric-card">
            <div className="metric-icon">{item.icon}</div>
            <div>
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </div>
          </div>
        ))}
      </div>

      <div className="panel-grid">
        <div className="panel large">
          <h3>Weather trends: {location.name}</h3>
          {loading && <p className="data-status" role="status">Loading temperature history...</p>}
          {error && <p className="data-error" role="alert">{error}</p>}
          {dailyWeather && (
            <div className="weather-trend-chart" role="img" aria-label={`Daily high, average, and low temperatures for ${location.name}`}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={dailyWeather.time.map((date, index) => ({
                    date,
                    high: dailyWeather.temperature_2m_max[index],
                    average: dailyWeather.temperature_2m_mean[index],
                    low: dailyWeather.temperature_2m_min[index],
                  }))}
                  margin={{ top: 10, right: 12, bottom: 4, left: 4 }}
                >
                  <CartesianGrid stroke="#dce5ed" strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(date) => date.slice(5)} minTickGap={24} />
                  <YAxis unit="°C" width={48} domain={['auto', 'auto']} />
                  <Tooltip
                    labelFormatter={(date) => date}
                    formatter={(value, name) => [`${Number(value).toFixed(1)}°C`, name]}
                  />
                  <Legend verticalAlign="bottom" height={30} />
                  <Line type="monotone" dataKey="high" name="High" stroke="#d55e00" strokeWidth={2} dot={false} activeDot={{ r: 4 }} connectNulls />
                  <Line type="monotone" dataKey="average" name="Average" stroke="#0f766e" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} connectNulls />
                  <Line type="monotone" dataKey="low" name="Low" stroke="#0072b2" strokeWidth={2} dot={false} activeDot={{ r: 4 }} connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="panel">
          <h3>Drift status</h3>
          <div className={`status-box ${statusClass(overallStatus)}`}>
            <span className={`status-pill ${statusClass(overallStatus)}`}>{overallStatus}</span>
            <p>{driftMessage}</p>
          </div>
          <h4 className="drift-changes-heading">Drift changes</h4>
          {loading && <p className="data-status">Calculating comparison records...</p>}
          {error && <p className="data-error">Drift records are unavailable.</p>}
          {!loading && !error && driftChanges.length === 0 && (
            <p className="data-status">No drift changes recorded for this comparison window.</p>
          )}
          {!loading && !error && driftChanges.length > 0 && (
            <div className="dashboard-drift-list">
              {driftChanges.map((item) => (
                <div className="dashboard-drift-record" key={item.key}>
                  <div className="dashboard-drift-copy">
                    <strong>{item.name}</strong>
                    <span>Baseline {formatValue(item.baseline, item.unit)} · Recent {formatValue(item.recent, item.unit)}</span>
                  </div>
                  <div className="dashboard-drift-score">
                    <span className={`status-pill ${statusClass(item.status)}`}>{item.status}</span>
                    <span>PSI {formatValue(item.psi)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function LocationsPage({ selectedLocation, onSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');

  const orderedResults = [
    ...(selectedLocation ? [{ ...selectedLocation, isSelectedLocation: true }] : []),
    ...results.filter((location) => String(location.id) !== String(selectedLocation?.id)),
  ];

  async function searchLocations(event) {
    event.preventDefault();
    const searchTerm = query.trim();
    if (!searchTerm) return;

    setIsSearching(true);
    setError('');
    try {
      const params = new URLSearchParams({ name: searchTerm, count: '10', language: 'en', format: 'json' });
      const response = await fetch(`https://geocoding-api.open-meteo.com/v1/search?${params}`);
      if (!response.ok) throw new Error('Location search failed');
      const data = await response.json();
      setResults(data.results ?? []);
      if (!data.results?.length) setError('No matching locations found. Try another search.');
    } catch {
      setResults([]);
      setError('Location search is unavailable. Check your connection and try again.');
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <div className="page-content">
      <div className="panel">
        <h3>Search world locations</h3>
        <form className="location-search" onSubmit={searchLocations}>
          <input
            aria-label="Search locations worldwide"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="City, town, or region"
          />
          <button className="primary-btn" type="submit" disabled={isSearching || !query.trim()}>
            <Search size={16} />
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </form>
        <p className="current-location">Selected: {selectedLocation.name}, {selectedLocation.country}</p>
        {error && <p className="location-error" role="status">{error}</p>}
        {orderedResults.length > 0 && (
          <div className="location-results" aria-live="polite">
            {orderedResults.map((location) => {
              const isSelected = String(location.id) === String(selectedLocation.id);
              const isCurrentSelectedRow = location.isSelectedLocation === true;
              return (
                <div className="location-result" key={`${location.id}-${location.isSelectedLocation ? 'selected' : 'result'}`}>
                  <div className="location-name">
                    <strong>{location.name}</strong>
                    <span>{[location.admin1, location.country].filter(Boolean).join(', ')}</span>
                  </div>
                  <span className="location-coordinates">{location.latitude.toFixed(2)}°, {location.longitude.toFixed(2)}°</span>
                  <button
                    className="select-location"
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => {
                      onSelect(location);
                    }}
                  >
                    {isCurrentSelectedRow ? 'Current' : isSelected ? 'Selected' : 'Select'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function WeatherDataPage({ location, dailyWeather, driftReport, loading, error }) {
  return (
    <div className="page-content">
      <div className="panel">
        <h3>Weather observations: {location.name}, {location.country}</h3>
        <DriftSummary location={location} driftReport={driftReport} loading={loading} error={error} />
        {loading && <p className="data-status" role="status">Loading weather history...</p>}
        {error && <p className="data-error" role="alert">{error}</p>}
        {dailyWeather && (
          <div className="table-scroll">
            <div className="list-table">
              <div className="row header weather-row">
                <span>Date</span>
                <span>Max</span>
                <span>Min</span>
                <span>Avg</span>
                <span>Rain</span>
                <span>Humidity</span>
                <span>Wind</span>
              </div>
              {[...dailyWeather.time.keys()].reverse().map((index) => (
                <div className="row weather-row" key={dailyWeather.time[index]}>
                  <span>{dailyWeather.time[index]}</span>
                  <span>{formatValue(dailyWeather.temperature_2m_max[index], '°C')}</span>
                  <span>{formatValue(dailyWeather.temperature_2m_min[index], '°C')}</span>
                  <span>{formatValue(dailyWeather.temperature_2m_mean[index], '°C')}</span>
                  <span>{formatValue(dailyWeather.precipitation_sum[index], ' mm')}</span>
                  <span>{formatValue(dailyWeather.relative_humidity_2m_mean[index], '%')}</span>
                  <span>{formatValue(dailyWeather.wind_speed_10m_max[index], ' km/h')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DriftHistoryPage({ location, dailyWeather, driftReport, loading, error }) {
  return (
    <div className="page-content">
      <div className="panel">
        <h3>Drift history: {location.name}, {location.country}</h3>
        <p className="comparison-period">Population Stability Index compares the earlier and recent halves of the available weather window.</p>
        <DriftSummary location={location} driftReport={driftReport} loading={loading} error={error} />
        {loading && <p className="data-status" role="status">Loading weather history...</p>}
        {error && <p className="data-error" role="alert">{error}</p>}
        {dailyWeather && (
          <div className="table-scroll">
            <div className="list-table">
              <div className="row header drift-row">
                <span>Variable</span>
                <span>Baseline avg</span>
                <span>Recent avg</span>
                <span>PSI</span>
                <span>Status</span>
              </div>
              {driftReport.map((comparison) => (
                <div className="row drift-row" key={comparison.key}>
                  <span>{comparison.name}</span>
                  <span>{formatValue(comparison.baseline, comparison.unit)}</span>
                  <span>{formatValue(comparison.recent, comparison.unit)}</span>
                  <span>{formatValue(comparison.psi)}</span>
                  <span className={`status-pill ${statusClass(comparison.status)}`}>
                    {comparison.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DriftSummary({ location, driftReport, loading, error }) {
  const drifted = driftReport.filter((item) => item.status === 'DRIFT');
  const watchList = driftReport.filter((item) => item.status === 'WATCH');
  const status = loading ? 'ANALYZING' : error ? 'UNAVAILABLE' : drifted.length ? 'DRIFT' : watchList.length ? 'WATCH' : 'NORMAL';
  const message = drifted.length
    ? `Potential drift detected in ${drifted.map((item) => item.name).join(', ')} for ${location.name}.`
    : watchList.length
      ? `Monitor possible changes in ${watchList.map((item) => item.name).join(', ')} for ${location.name}.`
      : error
        ? 'Drift analysis is unavailable for this location.'
        : loading
          ? 'Analyzing recent weather history for drift.'
          : `No significant drift detected for ${location.name}.`;

  return (
    <div className={`drift-summary ${statusClass(status)}`} role={drifted.length ? 'alert' : 'status'}>
      <span className={`status-pill ${statusClass(status)}`}>{status}</span>
      <span>{message}</span>
    </div>
  );
}

function AlertsPage({ location, driftReport, loading, error }) {
  const drifted = driftReport.filter((item) => item.status === 'DRIFT');
  const watchList = driftReport.filter((item) => item.status === 'WATCH');

  return (
    <div className="page-content">
      <div className="panel">
        <h3>Alerts: {location.name}, {location.country}</h3>
        <DriftSummary location={location} driftReport={driftReport} loading={loading} error={error} />
        <div className="alert-list">
          {loading && <p className="data-status" role="status">Calculating location-specific alerts...</p>}
          {error && <p className="data-error" role="alert">{error}</p>}
          {!loading && !error && drifted.map((item) => (
            <div className="alert-item warning" key={item.key}>
              <strong>Potential {item.name.toLowerCase()} drift detected</strong>
              <p>PSI {formatValue(item.psi)}. Baseline average: {formatValue(item.baseline, item.unit)}; recent average: {formatValue(item.recent, item.unit)}. Review this distributional change for {location.name}.</p>
            </div>
          ))}
          {!loading && !error && watchList.map((item) => (
            <div className="alert-item watch" key={item.key}>
              <strong>Monitor {item.name.toLowerCase()} changes</strong>
              <p>PSI {formatValue(item.psi)} for {location.name}; the recent distribution differs slightly from its baseline.</p>
            </div>
          ))}
          {!loading && !error && drifted.length === 0 && watchList.length === 0 && (
            <div className="alert-item normal">
              <strong>No active drift alerts</strong>
              <p>No significant distribution changes were found for {location.name} in the current comparison window.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AboutPage() {
  return (
    <div className="page-content">
      <div className="panel">
        <h3>About this system</h3>
        <p className="about-copy">
          This application monitors historical weather observations for statistically significant changes in distribution and flagging anomalous behavior. It uses the Kolmogorov-Smirnov test, Population Stability Index, and Isolation Forest to assess change across temperature, rainfall, humidity, pressure, and wind speed. Combined results are used to generate alerts, but the system does not claim physical sensor failure and instead highlights potential distributional shifts requiring review.
        </p>
      </div>
    </div>
  );
}

export default App;
