import { api } from '@/lib/api';

// Mock Next.js router
const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  refresh: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  prefetch: jest.fn(),
};

// Mock API client
jest.mock('@/lib/api', () => ({
  api: {
    getSessions: jest.fn(),
    getSession: jest.fn(),
    createSession: jest.fn(),
    getAssets: jest.fn(),
    getMarketplaceAssets: jest.fn(),
    getMarketplaceStats: jest.fn(),
  },
}));

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('getSessions should fetch all sessions', async () => {
    const mockSessions = [
      {
        session_id: 'session-1',
        name: 'Test Story',
        status: 'active',
      },
    ];

    (api.getSessions as jest.Mock).mockResolvedValue(mockSessions);

    const sessions = await api.getSessions();

    expect(sessions).toEqual(mockSessions);
    expect(sessions.length).toBe(1);
    expect(sessions[0].name).toBe('Test Story');
  });

  test('getSession should fetch a single session', async () => {
    const mockSession = {
      session_id: 'session-1',
      name: 'Test Story',
      status: 'active',
    };

    (api.getSession as jest.Mock).mockResolvedValue(mockSession);

    const session = await api.getSession('session-1');

    expect(session).toEqual(mockSession);
    expect(session.session_id).toBe('session-1');
  });

  test('createSession should create a new session', async () => {
    const mockSession = {
      session_id: 'session-new',
      name: 'New Story',
      status: 'created',
    };

    (api.createSession as jest.Mock).mockResolvedValue(mockSession);

    const session = await api.createSession('New Story');

    expect(session).toEqual(mockSession);
    expect(session.name).toBe('New Story');
  });

  test('getMarketplaceAssets should fetch marketplace assets', async () => {
    const mockAssets = [
      {
        id: 'asset-1',
        name: 'Test Asset',
        type: 'world_rule',
        price: 0,
      },
    ];

    (api.getMarketplaceAssets as jest.Mock).mockResolvedValue(mockAssets);

    const assets = await api.getMarketplaceAssets();

    expect(assets).toEqual(mockAssets);
    expect(assets.length).toBe(1);
  });

  test('getMarketplaceStats should fetch marketplace statistics', async () => {
    const mockStats = {
      total_listings: 150,
      total_transactions: 1200,
      total_revenue: 45000,
    };

    (api.getMarketplaceStats as jest.Mock).mockResolvedValue(mockStats);

    const stats = await api.getMarketplaceStats();

    expect(stats).toEqual(mockStats);
    expect(stats.total_listings).toBe(150);
  });
});
