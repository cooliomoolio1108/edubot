import requests, streamlit as st

def get_jwt() -> str | None:
    """Safely fetch the current login token from session state."""
    return st.session_state.get("login_token")

def get_headers() -> dict:
    """Return Authorization header if logged in, else empty dict."""
    jwt = get_jwt()
    return {"Authorization": f"Bearer {jwt}"} if jwt else {}

def header(jwt):
    return {"Authorization": f"Bearer {jwt}"}

def api_get(url: str, jwt: str | None = None, params: dict | None = None):
    try:
        response = requests.get(url, headers=header(jwt), params=params)
        response.raise_for_status()
        return response.json()  # or your process_json wrapper
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            st.warning("Unauthorized. Please log in.")
        else:
            st.error(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request failed: {req_err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None
