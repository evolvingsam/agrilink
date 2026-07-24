import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { authApi } from './api';
import { ProtectedRoute, PublicOnlyRoute } from './components/RouteGuards';
import Layout from './components/Layout';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Farmer pages
import FarmerHomePage from './pages/farmer/FarmerHomePage';
import ListingsPage from './pages/farmer/ListingsPage';
import NewListingPage from './pages/farmer/NewListingPage';
import ListingDetailPage from './pages/farmer/ListingDetailPage';
import ChatPage from './pages/farmer/ChatPage';
import MarketPage from './pages/farmer/MarketPage';
import PaymentsPage from './pages/farmer/PaymentsPage';

// Buyer pages
import BuyerHomePage from './pages/buyer/BuyerHomePage';
import OrdersPage from './pages/buyer/OrdersPage';

// Dispatcher pages
import DispatcherHomePage from './pages/dispatcher/DispatcherHomePage';

import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppRoutes() {
  const { user, setUser, isAuthenticated } = useAuthStore();
  const role = user?.role;

  // On app load, if we have a token, fetch the user profile
  useEffect(() => {
    if (isAuthenticated && !user) {
      authApi.me().then((res) => setUser(res.data)).catch(() => {});
    }
  }, [isAuthenticated, user, setUser]);

  function RoleHome() {
    if (!user) return <div className="loading-center"><span className="spinner" /></div>;
    if (role === 'farmer') return <FarmerHomePage />;
    if (role === 'buyer') return <BuyerHomePage />;
    return <DispatcherHomePage />;
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          {/* Role-agnostic home that renders per role */}
          <Route index element={<RoleHome />} />

          {/* Farmer routes */}
          <Route path="/listings" element={<ListingsPage />} />
          <Route path="/listings/new" element={<NewListingPage />} />
          <Route path="/listings/:id" element={<ListingDetailPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/market" element={<MarketPage />} />
          <Route path="/payments" element={<PaymentsPage />} />

          {/* Buyer routes */}
          <Route path="/orders" element={<OrdersPage />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
