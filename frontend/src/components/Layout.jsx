import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import './Layout.css';

export default function Layout() {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="app-main">
        <div className="page-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
