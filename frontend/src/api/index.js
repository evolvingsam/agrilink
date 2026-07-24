import api from './client';

export const authApi = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (data) => api.post('/auth/register/', data),
  me: () => api.get('/auth/me/'),
  updateMe: (data) => api.put('/auth/me/', data),
};

export const produceApi = {
  getCrops: () => api.get('/produce/crops/?page_size=100'),
  getCollectionPoints: () => api.get('/produce/collection-points/?page_size=100'),
  getListings: (params) => api.get('/produce/listings/', { params }),
  getListing: (id) => api.get(`/produce/listings/${id}/`),
  createListing: (data) => api.post('/produce/listings/', data),
  updateListing: (id, data) => api.put(`/produce/listings/${id}/`, data),
  deleteListing: (id) => api.delete(`/produce/listings/${id}/`),
  uploadPhoto: (id, formData) =>
    api.post(`/produce/listings/${id}/upload-photo/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

export const gradingApi = {
  assess: (listingId) => api.post('/grading/assess/', { listing_id: listingId }),
  getResult: (listingId) => api.get(`/grading/results/${listingId}/`),
};

export const assistantApi = {
  newConversation: () => api.post('/assistant/new/'),
  chat: (data) => api.post('/assistant/chat/', data),
  history: (conversationId) => api.get(`/assistant/history/${conversationId}/`),
  transcribeAudio: (formData) => api.post('/assistant/transcribe/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export const ordersApi = {
  getOrders: (params) => api.get('/orders/', { params }),
  getOrder: (id) => api.get(`/orders/${id}/`),
  createOrder: (data) => api.post('/orders/', data),
  payOrder: (id) => api.post(`/orders/${id}/pay/`),
  acceptDelivery: (id) => api.post(`/orders/${id}/accept-delivery/`),
  completeDelivery: (id) => api.post(`/orders/${id}/complete-delivery/`),
  cancelOrder: (id) => api.delete(`/orders/${id}/cancel/`),
};

export const matchingApi = {
  getResults: (orderId) => api.get(`/orders/matching/results/${orderId}/`),
  runMatching: () => api.post('/orders/matching/run/'),
};

export const logisticsApi = {
  getRoutes: (params) => api.get('/logistics/routes/', { params }),
  getRoute: (id) => api.get(`/logistics/routes/${id}/`),
  updateRouteStatus: (id, data) => api.put(`/logistics/routes/${id}/status/`, data),
  generateRoutes: () => api.post('/logistics/routes/generate/'),
  getRouteBriefing: (id) => api.get(`/logistics/routes/${id}/briefing/`),
};

export const paymentsApi = {
  getPayments: (params) => api.get('/payments/', { params }),
  getPayment: (id) => api.get(`/payments/${id}/`),
  triggerPayment: (matchId) => api.post(`/payments/trigger/${matchId}/`),
};

export const marketApi = {
  getTrends: (params) => api.get('/market/trends/', { params }),
  getPrices: (params) => api.get('/market/prices/', { params }),
};
