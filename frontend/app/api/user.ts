import { getCSRFToken } from '~/lib/django'

export const Client = {
  APP: 'app',
  BROWSER: 'browser'
} as const;

export type ClientType = (typeof Client)["APP"] | (typeof Client)["BROWSER"];

export function getSessionToken(): string | null {
  return tokenStorage.getItem('sessionToken')
}

export const settings: {
  client: ClientType;
  baseUrl: string;
  withCredentials: boolean;
} = {
  client: Client.BROWSER,
  baseUrl: `/api/_allauth/${Client.BROWSER}/v1`,
  withCredentials: false
}

export function updateUser(data: Record<string, any>, id: number) {
  const options = {
    method: 'PATCH',
    body: JSON.stringify({
      ...data,
      birth_date: data.birth_date.length ? data.birth_date : null,
    }),
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    credentials: settings.withCredentials ? 'include' as RequestCredentials : undefined
  }

  if (settings.client === Client.BROWSER) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      (options.headers as Record<string, string>)['X-CSRFToken'] = csrfToken;
    }
  } else if (settings.client === Client.APP) {
    (options.headers as Record<string, string>)['User-Agent'] = 'django-allauth example app';
    const sessionToken = getSessionToken();
    if (sessionToken) {
      (options.headers as Record<string, string>)['X-Session-Token'] = sessionToken;
    }
  }

  return fetch(`/api/user/users/${id}/`, options);
}
