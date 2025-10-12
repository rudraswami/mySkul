import MockAdapter from 'axios-mock-adapter';

describe('apiClient CSRF retry logic', () => {
  let apiClient;
  let mock;

  beforeAll(() => {
    if (typeof global.localStorage === 'undefined') {
      const store = new Map();
      global.localStorage = {
        getItem: jest.fn((key) => (store.has(key) ? store.get(key) : null)),
        setItem: jest.fn((key, value) => {
          store.set(key, value);
        }),
        removeItem: jest.fn((key) => {
          store.delete(key);
        }),
        clear: jest.fn(() => {
          store.clear();
        }),
      };
    }
  });

  const withClient = async () => {
    jest.resetModules();
    const module = await import('./client');
    apiClient = module.apiClient;
    mock = new MockAdapter(apiClient);
  };

  beforeEach(async () => {
    await withClient();
    mock.resetHandlers();
    mock.onAny().reply((config) => {
      throw new Error(`Unexpected request to ${config.url}`);
    });
  });

  afterEach(() => {
    mock.restore();
  });

  it('retries once and succeeds after refreshing CSRF token', async () => {
    mock.onGet('/auth/csrf-token').replyOnce(200, { csrf_token: 'initial-token' });
    mock.onGet('/auth/csrf-token').replyOnce(200, { csrf_token: 'refreshed-token' });

    mock.onPost('/protected').replyOnce(403, {
      detail: 'CSRF token invalid',
    });
    mock.onPost('/protected').replyOnce(200, { ok: true });

    const response = await apiClient.post('/protected', { foo: 'bar' });

    expect(response.data).toEqual({ ok: true });
    expect(mock.history.post).toHaveLength(2);
    expect(mock.history.get).toHaveLength(2);
  });

  it('surfaces 403 after a single retry attempt', async () => {
    mock.onGet('/auth/csrf-token').replyOnce(200, { csrf_token: 'initial-token' });
    mock.onGet('/auth/csrf-token').replyOnce(200, { csrf_token: 'refreshed-token' });

    mock.onPost('/protected').replyOnce(403, {
      detail: 'CSRF token invalid',
    });
    mock.onPost('/protected').replyOnce(403, {
      detail: 'CSRF token still invalid',
    });

    await expect(apiClient.post('/protected', { foo: 'bar' })).rejects.toMatchObject({
      response: { status: 403 },
    });

    expect(mock.history.post).toHaveLength(2);
    expect(mock.history.get).toHaveLength(2);
  });
});
