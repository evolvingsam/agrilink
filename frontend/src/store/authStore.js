import { create } from 'zustand';

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),

  setUser: (user) => set({ user, isAuthenticated: true }),
  updateWalletBalance: (newBalance) =>
    set({ user: { ...get().user, wallet_balance: newBalance } }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },
  setTokens: (access, refresh) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    set({ isAuthenticated: true });
  },
}));
