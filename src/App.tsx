import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 relative">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/20 via-transparent to-slate-800/20 pointer-events-none" />
      
      {/* Main content */}
      <div className="relative z-10 p-4 sm:p-6 lg:p-8">
        <Dashboard />
      </div>
    </div>
  );
}

export default App;