from conftest import auth_header, register


def _slug(data: dict) -> str:
    return data["memberships"][0]["organization_slug"]


def test_built_in_tools_execution():
    from app.tools.registry import registry

    # 1. Calculator
    calc_res = registry.execute("calculator", expression="150 * 0.85")
    assert calc_res["success"] is True
    assert calc_res["result"] == "127.5"

    # 2. Web Search
    search_res = registry.execute("web_search", query="billing price plans")
    assert search_res["success"] is True
    assert len(search_res["result"]) > 0
    assert "Pricing" in search_res["result"][0]["title"]

    # 3. CRM Lookup
    crm_res = registry.execute("crm_lookup", customer_email="alice@company.com")
    assert crm_res["success"] is True
    assert crm_res["result"]["email"] == "alice@company.com"
    assert "Plan" in crm_res["result"]["tier"]

    # 4. Send Email
    email_res = registry.execute(
        "send_email", recipient="customer@example.com", subject="Ticket Resolved", body="Your request has been processed."
    )
    assert email_res["success"] is True
    assert email_res["result"]["status"] == "queued"

    # 5. Calendar Scheduler
    cal_res = registry.execute(
        "schedule_calendar", title="Onboarding Call", attendee_email="bob@tenant.com", date_time="2026-08-01 10:00 UTC"
    )
    assert cal_res["success"] is True
    assert cal_res["result"]["status"] == "scheduled"

    # 6. GitHub Tool
    gh_res = registry.execute("github_tool", action="create_issue", repo="acme/support", title="Bug in auth flow")
    assert gh_res["success"] is True
    assert gh_res["result"]["status"] == "created"


def test_mcp_servers_and_client():
    from app.mcp import mcp_client

    servers = mcp_client.list_servers()
    server_ids = {s["id"] for s in servers}
    assert server_ids == {"filesystem", "github", "browser"}

    # Test Filesystem MCP Call
    fs_call = mcp_client.call_tool("filesystem", "fs_list_directory", {"path": "."})
    assert fs_call["success"] is True
    assert "items" in fs_call["result"]

    # Test GitHub MCP Call
    gh_call = mcp_client.call_tool("github", "github_search_code", {"query": "auth", "repo": "acme/repo"})
    assert gh_call["success"] is True
    assert len(gh_call["result"]["matches"]) > 0

    # Test Browser MCP Call
    br_call = mcp_client.call_tool("browser", "browser_extract_links", {"url": "https://tenantdesk.ai"})
    assert br_call["success"] is True
    assert len(br_call["result"]["links"]) > 0


def test_tools_api_endpoints(client):
    user = register(client, "tool_user@example.com", workspace="Tool Corp")
    token = user["access_token"]
    slug = _slug(user)

    # GET /tools
    tools_list = client.get(f"/api/v1/workspaces/{slug}/tools", headers=auth_header(token))
    assert tools_list.status_code == 200
    names = {t["name"] for t in tools_list.json()}
    assert {"calculator", "web_search", "crm_lookup", "send_email", "schedule_calendar", "github_tool"}.issubset(names)

    # POST /tools/execute
    exec_res = client.post(
        f"/api/v1/workspaces/{slug}/tools/execute",
        json={"tool_name": "calculator", "arguments": {"expression": "500 / 4"}},
        headers=auth_header(token),
    )
    assert exec_res.status_code == 200
    assert exec_res.json()["result"] in ("125", "125.0")


def test_mcp_api_endpoints(client):
    user = register(client, "mcp_user@example.com", workspace="MCP Corp")
    token = user["access_token"]
    slug = _slug(user)

    # GET /mcp/servers
    servers_res = client.get(f"/api/v1/workspaces/{slug}/mcp/servers", headers=auth_header(token))
    assert servers_res.status_code == 200
    assert len(servers_res.json()) == 3

    # POST /mcp/call
    call_res = client.post(
        f"/api/v1/workspaces/{slug}/mcp/call",
        json={"server_id": "github", "tool_name": "github_create_issue", "arguments": {"repo": "test/repo", "title": "MCP Issue"}},
        headers=auth_header(token),
    )
    assert call_res.status_code == 200
    assert call_res.json()["result"]["status"] == "created"
