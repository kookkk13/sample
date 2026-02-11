const JSON_HEADERS = {
  'Content-Type': 'application/json',
}

const FRIENDLY_MESSAGES = {
  AUTH_REQUIRED: '로그인이 필요합니다.',
  INVALID_SESSION: '세션이 만료되었습니다. 다시 로그인해주세요.',
  INVALID_CREDENTIALS: '아이디 또는 비밀번호가 올바르지 않습니다.',
  VCF_UNAVAILABLE: 'VCF API에 연결할 수 없습니다. URL/네트워크를 확인해주세요.',
  VCF_LOGIN_FAILED: '로그인 처리 중 오류가 발생했습니다.',
  VCF_FETCH_FAILED: '가상센터 목록을 가져오지 못했습니다.',
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'include',
    ...options,
    headers: {
      ...JSON_HEADERS,
      ...(options.headers || {}),
    },
  })

  if (!response.ok) {
    let payload = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }

    const code = payload?.code
    const message = FRIENDLY_MESSAGES[code] || payload?.message || '요청 처리 중 오류가 발생했습니다.'
    const error = new Error(message)
    error.status = response.status
    error.code = code
    throw error
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export function login({ baseUrl, username, password }) {
  return request('/api/login', {
    method: 'POST',
    body: JSON.stringify({
      baseUrl: baseUrl || undefined,
      username,
      password,
    }),
  })
}

export function fetchVirtualCenters() {
  return request('/api/virtualcenters', {
    method: 'GET',
  })
}
