# Jira Dashboard

A local analytics dashboard that visualises Jira issues by label over time.
It works in two modes:

- **Static** — loads embedded CSV data directly in the browser (no server needed).
- **Live** — pulls fresh data from your Jira Cloud instance through a local proxy server.

---

## Files

| File | Purpose |
|---|---|
| `updated_dashboard.html` | The dashboard (all charts + UI) |
| `jira_proxy.py` | Local HTTP proxy that forwards Jira API calls and serves the HTML |
| `JIRA.csv` | Sample / exported CSV data |

---

## Option 1 — Open without a server (static CSV data)

Just double-click `updated_dashboard.html` in Finder, or open it in any browser:

```
open updated_dashboard.html
```

The embedded CSV data will load automatically. No server required.

---

## Option 2 — Run with the proxy (live Jira data)

### Requirements

- Python 3 (no extra packages needed — uses only the standard library)
- A Jira Cloud account with an API token

### 1. Get a Jira API token

1. Go to <https://id.atlassian.com/manage-profile/security/api-tokens>
2. Click **Create API token**, give it a name, copy the token.

### 2. Start the proxy

Open a terminal in the project folder and run:

```bash
python3 jira_proxy.py
```

Expected output:

```
✅ Jira Dashboard Proxy running at http://localhost:8765
   Serving files from: /path/to/Jira_dashboard
   Press Ctrl+C to stop.
```

The browser will open `http://localhost:8765` automatically.

### 3. Connect to Jira from the dashboard

1. In the left sidebar, click **Data Source** to expand the panel.
2. Fill in:

   | Field | Example |
   |---|---|
   | Jira URL | `https://yourcompany.atlassian.net` |
   | Email | `you@yourcompany.com` |
   | API Token | *(paste the token from step 1)* |
   | JQL | `project = XYZ ORDER BY created DESC` |

3. Optionally check **Remember credentials** to save them in your browser's local storage.
4. Click **⬇ Fetch from Jira**.

The status line will show progress (`Fetched 350 / 1024 issues…`) and all charts will update automatically when the fetch is complete.

### 4. Stop the proxy

Press `Ctrl+C` in the terminal.

---

## Dashboard features

| Feature | Description |
|---|---|
| **Weekly Evolution** | Table at the top — last 6 ISO weeks per category, with sparklines and ▲/▼ delta vs previous week. A "spike!" badge appears when a category grows more than 50% week-over-week. |
| **Total by Category** | Bar chart — click a bar to drill down into daily detail for that category. |
| **Trends Over Time** | Line chart — click legend items to show/hide categories. |
| **Weekly / Monthly Breakdown** | Pie charts for a selected week or month. |
| **Date filter** | Start / End date inputs in the sidebar filter all charts simultaneously. |
| **Download HTML** | Saves the current dashboard (with data) as a standalone HTML file. |

---

## JQL tips

```
# All issues in a project
project = XYZ ORDER BY created DESC

# Issues created in the last 90 days
project = XYZ AND created >= -90d ORDER BY created DESC

# Issues with specific labels
project = XYZ AND labels in (Doublons, MD5) ORDER BY created DESC
```

The dashboard uses the `labels` and `created` fields from each issue. Other fields are ignored.

---

## Troubleshooting

**"Missing Jira credentials in headers"** — all three fields (URL, email, token) must be filled in.

**401 Unauthorized** — wrong email or API token. Make sure you are using an API token, not your account password.

**404 / connection refused** — the proxy is not running. Start it with `python3 jira_proxy.py`.

**Charts do not update after fetch** — check the browser console for JavaScript errors. Ensure the JQL returns at least one issue.
