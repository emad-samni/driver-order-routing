/* Driver Routing frontend — API-backed MVP prototype.
 *
 * Wired to real backend endpoints with connection status and error handling.
 * Falls back to sample data only when the API is unreachable.
 */
(function (global) {
  const API_BASE = ""; // Same origin; served by FastAPI static mount or proxy

  const api = {
    createOrder: { method: "POST", path: "/orders" },
    listOrders: { method: "GET", path: "/orders" },
    excelTemplate: { method: "GET", path: "/excel-template" },
    importExcel: { method: "POST", path: "/orders/import/excel" },
    importBatch: { method: "GET", path: "/import-batches/{id}" },
    createDriver: { method: "POST", path: "/drivers" },
    listDrivers: { method: "GET", path: "/drivers" },
    runPlan: { method: "POST", path: "/planning-runs" },
    publishPlan: { method: "POST", path: "/planning-runs/{id}/publish" },
    driverRouteToday: { method: "GET", path: "/driver/me/routes/today" },
    statusEvent: { method: "POST", path: "/orders/{id}/status-events" },
    dashboard: { method: "GET", path: "/dashboard/dispatch" },
  };

  async function apiRequest(definition, options = {}) {
    const url = definition.path.replace("{id}", options.id || "");
    const response = await fetch(url, {
      method: definition.method,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      const error = new Error(detail.detail || `HTTP ${response.status}`);
      error.status = response.status;
      error.body = detail;
      throw error;
    }
    if (response.status === 204) return null;
    return response.json();
  }

  function statusClass(status) {
    if (["delivered", "available"].includes(status)) return "ok";
    if (["failed", "missing_coordinates", "time_window_infeasible"].includes(status)) return "danger";
    if (["en_route", "arrived", "high"].includes(status)) return "warn";
    return "muted";
  }
  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[ch]));
  }
  function statusBadge(status) { return `<span class="badge ${statusClass(status)}">${escapeHtml(status)}</span>`; }
  function metersToKm(meters) { return `${(meters / 1000).toFixed(1)} km`; }
  function secondsToMin(seconds) { return `${Math.round(seconds / 60)} min`; }

  const sampleState = {
    activeView: "admin",
    published: true,
    selectedDriverId: "drv-lina",
    dashboard: {
      orders_by_status: { published: 2, en_route: 1, delivered: 1, failed: 1 },
      total_orders: 6,
      total_drivers: 3,
      latest_plan_summary: { routes: 3, assigned_orders: 5, unassigned_orders: 1, planned_distance_meters: 18450, planned_duration_seconds: 3980 },
      status_event_count: 9,
    },
    excelTemplate: { endpoint: "GET /excel-template", required: ["order_id", "recipient_name", "address", "delivery_date", "time_window_start", "time_window_end"], optional: ["phone", "lat", "lng", "priority", "service_duration_minutes", "package_units", "special_instructions"], example: "ORD-2001 | Erika Müller | Alexanderplatz 1, Berlin | 2026-07-31 | 09:00 | 12:00 | lat/lng optional" },
    importBatch: {
      id: "imp-demo-0730",
      filename: "retailer-orders-2026-07-31.xlsx",
      status: "needs_corrections",
      total_rows: 6,
      valid_rows: 3,
      draft_rows: 2,
      duplicate_rows: 1,
      routeable_rows: 3,
      row_errors: [
        { row_number: 5, field: "lat/lng", error_code: "geocoding_required", status: "draft", message: "Address imported but coordinates are missing.", suggested_fix: "Add lat/lng manually or geocode before planning." },
        { row_number: 7, field: "order_id", error_code: "duplicate_order_id", status: "rejected", message: "Order ORD-2001 already exists in this batch.", suggested_fix: "Use a unique retailer order ID." },
        { row_number: 8, field: "time_window_end", error_code: "invalid_time_window", status: "rejected", message: "End time is before start time.", suggested_fix: "Set end time after start time, e.g. 14:00." },
      ],
    },
    orders: [],
    drivers: [],
    routes: [
      {
        driver_id: "drv-lina",
        driver_name: "Lina",
        distance_meters: 7650,
        duration_seconds: 1680,
        progress: "1/3 complete",
        stops: [
          { order_id: "ORD-1001", sequence: 1, recipient_name: "M. Schneider", address: "Alexanderplatz 1, Berlin", planned_arrival: "09:18", time_window: "09:00–11:00", status: "published", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=52.5219,13.4132" },
          { order_id: "ORD-1002", sequence: 2, recipient_name: "Jansen Family", address: "Nieuwezijds Voorburgwal, Amsterdam", planned_arrival: "10:04", time_window: "10:00–12:00", status: "en_route", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=52.3738,4.8909" },
          { order_id: "ORD-1003", sequence: 3, recipient_name: "L. de Vries", address: "Westblaak, Rotterdam", planned_arrival: "11:45", time_window: "11:30–13:30", status: "delivered", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=51.9194,4.4780" },
        ],
      },
      {
        driver_id: "drv-samir",
        driver_name: "Samir",
        distance_meters: 10800,
        duration_seconds: 2300,
        progress: "0/2 complete",
        stops: [
          { order_id: "ORD-1005", sequence: 1, recipient_name: "Media Markt Store Ops", address: "Kurfuerstendamm, Berlin", planned_arrival: "12:20", time_window: "12:00–14:00", status: "published", navigation_url: "https://www.google.com/maps/search/?api=1&query=Kurfuerstendamm+Berlin" },
          { order_id: "ORD-1006", sequence: 2, recipient_name: "IKEA Customer Pickup", address: "Haarlemmermeerstraat, Amsterdam", planned_arrival: "13:05", time_window: "12:30–15:00", status: "failed", navigation_url: "https://www.google.com/maps/search/?api=1&query=Haarlemmermeerstraat+Amsterdam" },
        ],
      },
    ],
    unassigned: [
      { order_id: "ORD-1004", recipient_name: "Erika Müller", reason_code: "missing_coordinates", details: "Address is present but prototype requires lat/lng before route planning." },
    ],
    backendConnected: false,
    connectionError: null,
    loading: false,
  };

  async function loadDashboard() {
    const data = await apiRequest(api.dashboard);
    return {
      orders_by_status: data.orders_by_status || {},
      total_orders: data.total_orders || 0,
      total_drivers: data.total_drivers || 0,
      latest_plan_summary: data.latest_plan_summary || null,
      status_event_count: data.status_event_count || 0,
    };
  }
  async function loadExcelTemplate() {
    const data = await apiRequest(api.excelTemplate);
    const columns = data.columns || [];
    return {
      required: columns.filter((c) => c.required).map((c) => c.column),
      optional: columns.filter((c) => !c.required).map((c) => c.column),
      example: columns[0]?.example || "",
    };
  }
  async function loadOrders() {
    const data = await apiRequest(api.listOrders);
    return (data || []).map((o) => ({
      id: o.id,
      recipient_name: o.recipient_name,
      address: o.address,
      time_window: `${o.time_window_start || ""}${o.time_window_start && o.time_window_end ? "–" : ""}${o.time_window_end || ""}`,
      status: o.status,
      priority: o.priority,
      instructions: o.special_instructions || "",
    }));
  }
  async function loadDrivers() {
    const data = await apiRequest(api.listDrivers);
    return (data || []).map((d) => ({
      id: d.id,
      name: d.name,
      phone: d.phone || "",
      availability: d.availability_status,
      shift: `${d.shift_start || ""}${d.shift_start && d.shift_end ? "–" : ""}${d.shift_end || ""}`,
      capacity: `${d.max_stops || 0} stops`,
    }));
  }
  async function loadPlanningRuns() {
    // List via dashboard summary or plan runs endpoint if available.
    // We fall back to empty until a plan-list endpoint is added.
    return [];
  }
  async function loadLatestPlanRoutes() {
    const runs = await loadPlanningRuns();
    // Prefer the most recent run when available.
    const latest = runs[0];
    if (!latest) return [];
    return (latest.routes || []).map((r) => ({
      driver_id: r.driver_id,
      driver_name: r.driver_name,
      distance_meters: r.planned_distance_meters || 0,
      duration_seconds: r.planned_duration_seconds || 0,
      progress: `${r.stops.filter((s) => ["delivered", "failed", "returned"].includes(s.status)).length}/${r.stops.length} complete`,
      stops: (r.stops || []).map((stop) => ({
        order_id: stop.order_id,
        sequence: stop.sequence,
        recipient_name: stop.recipient_name,
        address: stop.address,
        planned_arrival: stop.planned_arrival ? stop.planned_arrival.slice(11, 16) : "",
        time_window: "",
        status: stop.status,
        navigation_url: stop.navigation_url || "",
      })),
    }));
  }

  function dashboardMetrics(state) {
    const summary = state.dashboard.latest_plan_summary || {};
    return [
      { label: "Assigned", value: summary.assigned_orders || 0 },
      { label: "Unassigned", value: summary.unassigned_orders || 0 },
      { label: "Planned km", value: metersToKm(summary.planned_distance_meters || 0) },
      { label: "Plan time", value: secondsToMin(summary.planned_duration_seconds || 0) },
    ];
  }
  function importMetrics(batch) {
    return [
      { label: "Rows", value: batch.total_rows || 0 },
      { label: "Ready", value: batch.valid_rows || 0 },
      { label: "Draft", value: batch.draft_rows || 0 },
      { label: "Errors", value: (batch.row_errors || []).length },
    ];
  }

  function renderHero(state) {
    return `<section class="hero">
      <div class="hero-card">
        <h1>Mobile-first dispatch command center</h1>
        <p>Plan feasible driver routes, review exceptions, publish to drivers, and monitor status updates without phone chaos.</p>
      </div>
      <div class="status-row">
        <div class="metric"><strong>${state.backendConnected ? statusBadge("connected") : statusBadge("disconnected")}</strong><span>Backend</span></div>
        <div class="metric"><strong>${escapeHtml(state.loading ? "..." : "ready")}</strong><span>UI</span></div>
        ${dashboardMetrics(state).map((m) => `<div class="metric"><strong>${escapeHtml(m.value)}</strong><span>${escapeHtml(m.label)}</span></div>`).join("")}
      </div>
      ${state.connectionError ? `<div class="alert danger">${escapeHtml(state.connectionError)}</div>` : ""}
    </section>`;
  }

  function renderOrderForm(state) {
    return `<section class="panel">
      <h2>Quick order intake</h2>
      <p class="panel-subtitle">Create a new order via the backend API.</p>
      <form id="order-form" class="form-grid two">
        <div class="field"><label>Recipient</label><input id="recipient_name" value="" placeholder="Customer name" required /></div>
        <div class="field"><label>Delivery date</label><input id="delivery_date" type="date" value="${new Date().toISOString().slice(0, 10)}" required /></div>
        <div class="field"><label>Address</label><input id="address" value="" placeholder="Street, city" required /></div>
        <div class="field"><label>Time window start</label><input id="time_window_start" type="time" value="09:00" required /></div>
        <div class="field"><label>Time window end</label><input id="time_window_end" type="time" value="12:00" required /></div>
        <div class="field"><label>Priority</label><select id="priority"><option>normal</option><option>high</option><option>low</option></select></div>
        <div class="field"><label>Latitude</label><input id="latitude" type="number" step="any" placeholder="optional" /></div>
        <div class="field"><label>Longitude</label><input id="longitude" type="number" step="any" placeholder="optional" /></div>
        <div class="field"><label>Service minutes</label><input id="service_minutes" type="number" value="10" /></div>
        <div class="field"><label>Instructions</label><input id="instructions" value="" placeholder="optional" /></div>
        <div class="actions"><button type="submit" class="primary">Save ready order</button><span class="field-meta" id="order-form-status"></span></div>
      </form>
    </section>`;
  }

  function renderExcelImport(state) {
    const template = state.excelTemplate || sampleState.excelTemplate;
    const batch = state.importBatch || sampleState.importBatch;
    return `<section class="panel import-panel">
      <div class="card-header"><h2>Excel order import</h2>${statusBadge(batch.status || "draft")}</div>
      <p class="panel-subtitle">Upload retailer .xlsx orders, validate every row, keep fixable rows as draft, and plan only routeable orders.</p>
      <div class="template-box">
        <strong>Template columns</strong>
        <div class="card-meta">Required: ${(template.required || []).map(escapeHtml).join(", ")}</div>
        <div class="card-meta">Optional: ${(template.optional || []).map(escapeHtml).join(", ")}</div>
        <div class="card-meta">Example: ${escapeHtml(template.example || "")}</div>
      </div>
      <form id="excel-form" class="actions">
        <input id="excel-file" type="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
        <button type="submit" class="primary">Upload .xlsx</button>
      </form>
      <div id="excel-result" class="card-meta"></div>
      <div class="import-metrics">${importMetrics(batch).map((m) => `<div class="metric mini"><strong>${escapeHtml(m.value)}</strong><span>${escapeHtml(m.label)}</span></div>`).join("")}</div>
      <div class="row-error-list" aria-label="Row-level validation results">
        ${(batch.row_errors || []).map((err) => `<article class="row-error ${err.status === "draft" ? "warn" : "danger"}">
          <div><strong>Row ${escapeHtml(err.row_number)} • ${escapeHtml(err.field)}</strong><div class="card-meta">${escapeHtml(err.message)}</div><div class="card-meta">Fix: ${escapeHtml(err.suggested_fix)}</div></div>
          <div class="badges">${statusBadge(err.error_code)}${statusBadge(err.status)}</div>
        </article>`).join("")}
      </div>
    </section>`;
  }

  function renderDriverForm(state) {
    return `<section class="panel">
      <h2>Driver capacity</h2>
      <form id="driver-form" class="form-grid">
        <div class="field"><label>Driver</label><input id="driver_name" value="" placeholder="Driver name" required /></div>
        <div class="field"><label>Start address</label><input id="start_address" value="" placeholder="Depot address" /></div>
        <div class="field"><label>Latitude</label><input id="driver_lat" type="number" step="any" required /></div>
        <div class="field"><label>Longitude</label><input id="driver_lng" type="number" step="any" required /></div>
        <div class="field"><label>Shift start</label><input id="shift_start" type="time" value="08:00" required /></div>
        <div class="field"><label>Shift end</label><input id="shift_end" type="time" value="18:00" required /></div>
        <div class="field"><label>Max stops</label><input id="max_stops" type="number" value="10" required /></div>
        <div class="field"><label>Capacity units</label><input id="capacity_units" type="number" value="20" required /></div>
        <div class="actions"><button type="submit" class="primary">Add driver</button><span class="field-meta" id="driver-form-status"></span></div>
      </form>
    </section>`;
  }

  function renderPlanReview(state) {
    const routeCards = (state.routes || []).map(renderRouteCard).join("");
    return `<section class="panel">
      <div class="card-header"><h2>Plan review & publish</h2><span>${state.published ? statusBadge("published") : statusBadge("review")}</span></div>
      <p class="panel-subtitle">Run planning from existing orders/drivers, review routes, and publish.</p>
      <form id="plan-form" class="form-grid two planning-config">
        <div class="field"><label>Delivery date</label><input id="delivery_date" type="date" value="${new Date().toISOString().slice(0, 10)}" required /></div>
        <div class="field"><label>Publish run id</label><input id="publish_run_id" value="" placeholder="leave empty to skip" /></div>
        <div class="actions"><button type="submit" class="primary">Run optimization</button><span class="field-meta" id="plan-form-status"></span></div>
      </form>
      <div id="plan-card-list" class="card-list" style="margin-top:12px">${routeCards}</div>
    </section>`;
  }

  function renderRouteCard(route) {
    return `<article class="card route-card">
      <div class="card-header"><div><div class="card-title">${escapeHtml(route.driver_name)}</div><div class="card-meta">${metersToKm(route.distance_meters)} • ${secondsToMin(route.duration_seconds)} • ${escapeHtml(route.progress)}</div></div>${statusBadge("route")}</div>
      ${route.stops.map((stop) => `<div class="stop-row"><div class="stop-seq">${stop.sequence}</div><div><strong>${escapeHtml(stop.recipient_name)}</strong><div class="card-meta">${escapeHtml(stop.planned_arrival)} • ${escapeHtml(stop.time_window)} • ${escapeHtml(stop.address)}</div><div class="badges">${statusBadge(stop.status)}</div></div></div>`).join("")}
    </article>`;
  }

  function renderExceptions(state) {
    return `<section class="panel">
      <h2>Exception queue</h2>
      <p class="panel-subtitle">Unassigned orders and plan exceptions.</p>
      <div class="card-list">${(state.unassigned || []).map((item) => `<article class="card exception"><div class="card-title">${escapeHtml(item.order_id)} — ${escapeHtml(item.recipient_name)}</div><div class="card-meta">${escapeHtml(item.details)}</div><div class="badges">${statusBadge(item.reason_code)}</div></article>`).join("")}</div>
    </section>`;
  }

  function renderAdmin(state) {
    return `<div class="grid two"><div class="grid">${renderExcelImport(state)}${renderOrderForm(state)}${renderDriverForm(state)}${renderExceptions(state)}</div><div>${renderPlanReview(state)}</div></div>`;
  }

  function nextActionFor(status) {
    const transitions = { published: ["accepted", "en_route", "failed"], accepted: ["en_route", "failed", "returned"], en_route: ["arrived", "failed"], arrived: ["delivered", "failed"], failed: ["returned"] };
    return transitions[status] || [];
  }

  function renderDriver(state) {
    const route = (state.routes || []).find((r) => r.driver_id === state.selectedDriverId) || (state.routes || [])[0];
    if (!route) return `<section class="mobile-frame"><div class="driver-header"><h2>Today's route</h2><div>No route assigned</div></div></section>`;
    const nextStop = route.stops.find((s) => !["delivered", "failed", "returned"].includes(s.status));
    return `<section class="mobile-frame">
      <div class="driver-header"><h2>Today's route</h2><div>${escapeHtml(route.driver_name)} • ${escapeHtml(route.progress)}</div></div>
      <div class="driver-body">${route.stops.map((stop) => renderDriverStop(stop, nextStop && nextStop.order_id === stop.order_id)).join("")}</div>
    </section>`;
  }

  function renderDriverStop(stop, isNext) {
    const actions = nextActionFor(stop.status);
    return `<article class="card ${isNext ? "next-stop" : ""}">
      <div class="card-header"><div><div class="card-title">${stop.sequence}. ${escapeHtml(stop.recipient_name)}</div><div class="card-meta">${escapeHtml(stop.planned_arrival)} • ${escapeHtml(stop.time_window)}</div></div>${statusBadge(stop.status)}</div>
      <p class="card-meta">${escapeHtml(stop.address)}</p>
      <a class="nav-link" href="${escapeHtml(stop.navigation_url || "")}" target="_blank" rel="noreferrer">Open navigation</a>
      <div class="status-buttons">${actions.map((action) => `<button data-order="${escapeHtml(stop.order_id)}" data-status="${escapeHtml(action)}">${escapeHtml(action.replace("_", " "))}</button>`).join("")}</div>
      ${actions.includes("failed") ? `<div class="field" style="margin-top:10px"><label>Failure / proof note</label><textarea id="note-${escapeHtml(stop.order_id)}" placeholder="Required if failed; optional proof note if delivered"></textarea></div>` : ""}
    </article>`;
  }

  function renderApp(state) {
    return `<div class="app-shell">
      <header class="topbar"><div class="logo"><div class="logo-mark">DR</div><div>Driver Routing<br><small>Frontend MVP</small></div></div><div class="role-pill">${state.activeView === "admin" ? "Admin / Dispatcher" : "Driver"}</div></header>
      <main>${renderHero(state)}<nav class="tabs"><button class="tab ${state.activeView === "admin" ? "active" : ""}" data-view="admin">Admin</button><button class="tab ${state.activeView === "driver" ? "active" : ""}" data-view="driver">Driver</button></nav>${state.activeView === "admin" ? renderAdmin(state) : renderDriver(state)}</main>
      <nav class="bottom-nav"><button class="tab ${state.activeView === "admin" ? "active" : ""}" data-view="admin">Admin</button><button class="tab ${state.activeView === "driver" ? "active" : ""}" data-view="driver">Driver</button></nav>
    </div>`;
  }

  async function fetchWithFallback(request, fallback) {
    try {
      const result = await request();
      return result;
    } catch (error) {
      console.warn("API request failed, using fallback", error);
      return fallback;
    }
  }

  async function initState() {
    let backendConnected = false;
    let connectionError = null;
    let dashboard = sampleState.dashboard;
    let excelTemplate = sampleState.excelTemplate;
    let orders = [];
    let drivers = [];
    let routes = [];
    let unassigned = [];
    let importBatch = sampleState.importBatch;
    let loading = true;

    try {
      const healthUrl = `${API_BASE}/health`;
      const healthResponse = await fetch(healthUrl, { method: "GET" });
      backendConnected = healthResponse.ok;
      if (!backendConnected) connectionError = `Health check failed: HTTP ${healthResponse.status}`;
    } catch (error) {
      backendConnected = false;
      connectionError = `Backend unreachable: ${error.message}`;
    }

    if (backendConnected) {
      try {
        [dashboard, excelTemplate, orders, drivers, routes] = await Promise.all([
          fetchWithFallback(loadDashboard, sampleState.dashboard),
          fetchWithFallback(loadExcelTemplate, sampleState.excelTemplate),
          fetchWithFallback(loadOrders, []),
          fetchWithFallback(loadDrivers, []),
          fetchWithFallback(loadLatestPlanRoutes, []),
        ]);
      } catch (error) {
        connectionError = `Data load failed: ${error.message}`;
        backendConnected = false;
      }
    }

    loading = false;
    return { ...sampleState, backendConnected, connectionError, dashboard, excelTemplate, orders, drivers, routes, unassigned, importBatch, loading };
  }

  async function refreshData(root) {
    const state = await initState();
    root.__state = state;
    rerender(root);
  }

  async function mount(root) {
    await refreshData(root);
    root.__refreshData = () => refreshData(root);
    return { getState: () => root.__state, setState: (next) => { root.__state = next; rerender(root); } };
  }

  function rerender(root) {
    const state = root.__State || root.__state;
    if (!state) return;
    root.innerHTML = renderApp(state);
    bindEvents(root, state);
  }

  async function bindEvents(root, state) {
    root.querySelectorAll("[data-view]").forEach((btn) => btn.addEventListener("click", () => { state.activeView = btn.dataset.view; rerender(root); }));
    root.querySelectorAll("[data-order][data-status]").forEach((btn) => btn.addEventListener("click", async () => {
      try {
        await apiRequest(api.statusEvent, { id: btn.dataset.order, body: { to_status: btn.dataset.status, actor_user_id: "frontend-user", note: "Updated from driver view" } });
      } catch (error) {
        alert(`Status update failed: ${error.message}`);
      }
      state.activeView = "driver";
      rerender(root);
    }));

    const orderForm = root.querySelector("#order-form");
    if (orderForm) {
      orderForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const statusEl = root.querySelector("#order-form-status");
        statusEl.textContent = "Saving...";
        const body = {
          recipient_name: root.querySelector("#recipient_name").value,
          delivery_date: root.querySelector("#delivery_date").value,
          address: root.querySelector("#address").value,
          time_window_start: root.querySelector("#time_window_start").value,
          time_window_end: root.querySelector("#time_window_end").value,
          priority: root.querySelector("#priority").value,
          latitude: root.querySelector("#latitude").value ? parseFloat(root.querySelector("#latitude").value) : undefined,
          longitude: root.querySelector("#longitude").value ? parseFloat(root.querySelector("#longitude").value) : undefined,
          service_minutes: parseInt(root.querySelector("#service_minutes").value || "10", 10),
          special_instructions: root.querySelector("#instructions").value,
        };
        try {
          await apiRequest(api.createOrder, { body });
          statusEl.textContent = "Saved";
          await root.__refreshData();
        } catch (error) {
          statusEl.textContent = `Failed: ${error.message}`;
        }
      });
    }

    const driverForm = root.querySelector("#driver-form");
    if (driverForm) {
      driverForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const statusEl = root.querySelector("#driver-form-status");
        statusEl.textContent = "Saving...";
        const body = {
          name: root.querySelector("#driver_name").value,
          start_address: root.querySelector("#start_address").value,
          start_location: { lat: parseFloat(root.querySelector("#driver_lat").value), lng: parseFloat(root.querySelector("#driver_lng").value) },
          shift_start: root.querySelector("#shift_start").value,
          shift_end: root.querySelector("#shift_end").value,
          max_stops: parseInt(root.querySelector("#max_stops").value || "0", 10),
          capacity_units: parseInt(root.querySelector("#capacity_units").value || "0", 10),
        };
        try {
          await apiRequest(api.createDriver, { body });
          statusEl.textContent = "Saved";
          await root.__refreshData();
        } catch (error) {
          statusEl.textContent = `Failed: ${error.message}`;
        }
      });
    }

    const excelForm = root.querySelector("#excel-form");
    if (excelForm) {
      excelForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const fileInput = root.querySelector("#excel-file");
        const resultEl = root.querySelector("#excel-result");
        const file = fileInput.files[0];
        if (!file) { resultEl.textContent = "Select a .xlsx file first."; return; }
        resultEl.textContent = "Importing...";
        try {
          const arrayBuffer = await file.arrayBuffer();
          const blob = new Blob([arrayBuffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
          const response = await fetch(api.importExcel.path, { method: "POST", body: blob });
          if (!response.ok) {
            const detail = await response.json().catch(() => ({}));
            throw new Error(detail.detail || `Import failed: HTTP ${response.status}`);
          }
          const data = await response.json();
          resultEl.textContent = `Imported ${data.valid_rows || 0} routeable rows (${data.invalid_rows || 0} issues).`;
          await root.__refreshData();
        } catch (error) {
          resultEl.textContent = `Import failed: ${error.message}`;
        }
      });
    }

    const planForm = root.querySelector("#plan-form");
    if (planForm) {
      planForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const statusEl = root.querySelector("#plan-form-status");
        statusEl.textContent = "Planning...";
        const body = { delivery_date: root.querySelector("#delivery_date").value };
        try {
          const run = await apiRequest(api.runPlan, { body });
          statusEl.textContent = `Run created: ${run.id}`;
          const publishId = root.querySelector("#publish_run_id").value.trim();
          if (publishId) {
            const published = await apiRequest(api.publishPlan, { id: publishId });
            statusEl.textContent = `Published run ${published.id}`;
          }
          await root.__refreshData();
        } catch (error) {
          statusEl.textContent = `Failed: ${error.message}`;
        }
      });
    }
  }

  const exported = { api, sampleState, metersToKm, secondsToMin, statusClass, dashboardMetrics, importMetrics, nextActionFor, renderApp, mount };
  if (typeof module !== "undefined" && module.exports) module.exports = exported;
  global.DriverRoutingFrontend = exported;
  if (typeof document !== "undefined") mount(document.getElementById("app"));
})(typeof window !== "undefined" ? window : globalThis);
