/* Driver Routing frontend prototype.
 * Dependency-free PWA-style responsive prototype aligned to the backend contract
 * in repo/backend/docs/api-and-schema.md. It uses sample state now; the API
 * adapter names below map directly to planned FastAPI endpoints.
 */
(function (global) {
  const sampleState = {
    activeView: "admin",
    published: true,
    selectedDriverId: "drv-lina",
    dashboard: {
      orders_by_status: { published: 2, en_route: 1, delivered: 1, failed: 1 },
      total_orders: 6,
      total_drivers: 3,
      latest_plan_summary: {
        routes: 3,
        assigned_orders: 5,
        unassigned_orders: 1,
        planned_distance_meters: 18450,
        planned_duration_seconds: 3980,
      },
      status_event_count: 9,
    },
    excelTemplate: {
      endpoint: "GET /excel-template",
      required: ["order_id", "recipient_name", "address", "delivery_date", "time_window_start", "time_window_end"],
      optional: ["phone", "lat", "lng", "priority", "service_duration_minutes", "package_units", "special_instructions"],
      example: "ORD-2001 | Erika Müller | Alexanderplatz 1, Berlin | 2026-07-31 | 09:00 | 12:00 | lat/lng optional",
    },
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
    orders: [
      { id: "ORD-1001", recipient_name: "M. Schneider", address: "Alexanderplatz 1, Berlin", time_window: "09:00–11:00", status: "published", priority: "high", instructions: "Large furniture parcel; call on arrival." },
      { id: "ORD-1002", recipient_name: "Jansen Family", address: "Nieuwezijds Voorburgwal, Amsterdam", time_window: "10:00–12:00", status: "en_route", priority: "normal", instructions: "Lift gate needed." },
      { id: "ORD-1003", recipient_name: "L. de Vries", address: "Westblaak, Rotterdam", time_window: "11:30–13:30", status: "delivered", priority: "normal", instructions: "Proof note captured." },
      { id: "ORD-1004", recipient_name: "Erika Müller", address: "Missing coordinates", time_window: "09:00–10:00", status: "ready_to_plan", priority: "high", exception: "missing_coordinates" },
    ],
    drivers: [
      { id: "drv-lina", name: "Lina", phone: "+49****0001", availability: "on_route", shift: "08:00–15:00", capacity: "4/8 stops" },
      { id: "drv-samir", name: "Samir", phone: "+31****0002", availability: "assigned", shift: "09:00–17:00", capacity: "1/10 stops" },
      { id: "drv-maya", name: "Maya", phone: "+49****0003", availability: "available", shift: "12:00–20:00", capacity: "0/8 stops" },
    ],
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
  };

  const api = {
    createOrder: { method: "POST", path: "/orders" },
    listOrders: { method: "GET", path: "/orders" },
    excelTemplate: { method: "GET", path: "/excel-template" },
    importExcel: { method: "POST", path: "/orders/import/excel" },
    importBatch: { method: "GET", path: "/import-batches/{id}" },
    createDriver: { method: "POST", path: "/drivers" },
    runPlan: { method: "POST", path: "/planning-runs" },
    publishPlan: { method: "POST", path: "/planning-runs/{id}/publish" },
    driverRouteToday: { method: "GET", path: "/driver/me/routes/today" },
    statusEvent: { method: "POST", path: "/orders/{id}/status-events" },
    dashboard: { method: "GET", path: "/dashboard/dispatch" },
  };

  function metersToKm(meters) { return `${(meters / 1000).toFixed(1)} km`; }
  function secondsToMin(seconds) { return `${Math.round(seconds / 60)} min`; }
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
      <div class="status-row">${dashboardMetrics(state).map((m) => `<div class="metric"><strong>${escapeHtml(m.value)}</strong><span>${escapeHtml(m.label)}</span></div>`).join("")}</div>
    </section>`;
  }

  function renderOrderForm() {
    return `<section class="panel">
      <h2>Quick order intake</h2>
      <p class="panel-subtitle">Fields mirror the backend POST /orders contract. Prototype form is visual-only until FastAPI wrapper exists.</p>
      <div class="form-grid two">
        <div class="field"><label>Recipient</label><input value="New Customer" /></div>
        <div class="field"><label>Delivery date</label><input type="date" value="2026-07-30" /></div>
        <div class="field"><label>Address</label><input value="Customer address" /></div>
        <div class="field"><label>Time window</label><input value="09:00–12:00" /></div>
        <div class="field"><label>Priority</label><select><option>normal</option><option>high</option><option>low</option></select></div>
        <div class="field"><label>Service minutes</label><input type="number" value="10" /></div>
      </div>
      <div class="actions"><button class="primary">Save ready order</button><button class="secondary">Use Excel import instead</button></div>
    </section>`;
  }

  function renderExcelImport(state) {
    const template = state.excelTemplate;
    const batch = state.importBatch;
    return `<section class="panel import-panel">
      <div class="card-header"><h2>Excel order import</h2>${statusBadge(batch.status)}</div>
      <p class="panel-subtitle">First-pilot intake: upload retailer .xlsx orders, validate every row, keep fixable rows as draft, and plan only routeable orders.</p>
      <div class="template-box">
        <strong>Template columns</strong>
        <div class="card-meta">Required: ${template.required.map(escapeHtml).join(", ")}</div>
        <div class="card-meta">Optional: ${template.optional.map(escapeHtml).join(", ")}</div>
        <div class="card-meta">Example: ${escapeHtml(template.example)}</div>
      </div>
      <div class="actions"><button class="primary">Upload .xlsx</button><button class="secondary">Download template</button><button class="secondary">Review import batch</button></div>
      <div class="import-metrics">${importMetrics(batch).map((m) => `<div class="metric mini"><strong>${escapeHtml(m.value)}</strong><span>${escapeHtml(m.label)}</span></div>`).join("")}</div>
      <div class="row-error-list" aria-label="Row-level validation results">
        ${(batch.row_errors || []).map((err) => `<article class="row-error ${err.status === "draft" ? "warn" : "danger"}">
          <div><strong>Row ${escapeHtml(err.row_number)} • ${escapeHtml(err.field)}</strong><div class="card-meta">${escapeHtml(err.message)}</div><div class="card-meta">Fix: ${escapeHtml(err.suggested_fix)}</div></div>
          <div class="badges">${statusBadge(err.error_code)}${statusBadge(err.status)}</div>
        </article>`).join("")}
      </div>
    </section>`;
  }

  function renderDriverForm() {
    return `<section class="panel">
      <h2>Driver capacity</h2>
      <div class="form-grid">
        <div class="field"><label>Driver</label><input value="Driver name" /></div>
        <div class="field"><label>Start location</label><input value="Store/depot coordinates or address" /></div>
        <div class="field"><label>Shift</label><input value="08:00–16:00" /></div>
        <div class="field"><label>Max stops / units</label><input value="10 stops / 20 units" /></div>
      </div>
      <div class="actions"><button class="primary">Add driver</button><button class="secondary">Set unavailable</button></div>
    </section>`;
  }

  function renderPlanReview(state) {
    return `<section class="panel">
      <div class="card-header"><h2>Plan review & publish</h2><span>${state.published ? statusBadge("published") : statusBadge("review")}</span></div>
      <p class="panel-subtitle">List-first route review; map visualization can be added later. Admin keeps control before publish.</p>
      <div class="form-grid two planning-config">
        <div class="field"><label>Optimization strategy</label><select><option>balanced</option><option>shortest distance / fuel proxy</option><option>on-time priority</option><option>balanced workload</option></select></div>
        <div class="field"><label>Constraint mode</label><select><option>strict constraints</option><option>relaxed with manual review</option></select></div>
      </div>
      <div class="actions"><button class="primary">Run optimization</button><button class="secondary">Publish routes</button><button class="secondary">Manual override + audit note</button></div>
      <div class="card-list" style="margin-top:12px">${state.routes.map(renderRouteCard).join("")}</div>
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
      <p class="panel-subtitle">Reason codes match backend unassigned outputs. Admin dashboard should poll /dashboard/dispatch every 10–30 seconds once API exists.</p>
      <div class="card-list">${state.unassigned.map((item) => `<article class="card exception"><div class="card-title">${escapeHtml(item.order_id)} — ${escapeHtml(item.recipient_name)}</div><div class="card-meta">${escapeHtml(item.details)}</div><div class="badges">${statusBadge(item.reason_code)}</div></article>`).join("")}</div>
    </section>`;
  }

  function renderAdmin(state) {
    return `<div class="grid two"><div class="grid">${renderExcelImport(state)}${renderOrderForm()}${renderDriverForm()}${renderExceptions(state)}</div><div>${renderPlanReview(state)}</div></div>`;
  }

  function nextActionFor(status) {
    const transitions = {
      published: ["accepted", "en_route", "failed"],
      accepted: ["en_route", "failed", "returned"],
      en_route: ["arrived", "failed"],
      arrived: ["delivered", "failed"],
      failed: ["returned"],
    };
    return transitions[status] || [];
  }

  function renderDriver(state) {
    const route = state.routes.find((r) => r.driver_id === state.selectedDriverId) || state.routes[0];
    const nextStop = route.stops.find((s) => !["delivered", "failed", "returned"].includes(s.status));
    return `<section class="mobile-frame">
      <div class="driver-header"><h2>Today's route</h2><div>${escapeHtml(route.driver_name)} • ${escapeHtml(route.progress)}</div></div>
      <div class="driver-body">
        ${route.stops.map((stop) => renderDriverStop(stop, nextStop && nextStop.order_id === stop.order_id)).join("")}
      </div>
    </section>`;
  }

  function renderDriverStop(stop, isNext) {
    const actions = nextActionFor(stop.status);
    return `<article class="card ${isNext ? "next-stop" : ""}">
      <div class="card-header"><div><div class="card-title">${stop.sequence}. ${escapeHtml(stop.recipient_name)}</div><div class="card-meta">${escapeHtml(stop.planned_arrival)} • ${escapeHtml(stop.time_window)}</div></div>${statusBadge(stop.status)}</div>
      <p class="card-meta">${escapeHtml(stop.address)}</p>
      <a class="nav-link" href="${escapeHtml(stop.navigation_url)}" target="_blank" rel="noreferrer">Open navigation</a>
      <div class="status-buttons">${actions.map((action) => `<button data-order="${escapeHtml(stop.order_id)}" data-status="${escapeHtml(action)}">${escapeHtml(action.replace("_", " "))}</button>`).join("")}</div>
      ${actions.includes("failed") ? `<div class="field" style="margin-top:10px"><label>Failure / proof note</label><textarea placeholder="Required if failed; optional proof note if delivered"></textarea></div>` : ""}
    </article>`;
  }

  function renderApp(state) {
    return `<div class="app-shell">
      <header class="topbar"><div class="logo"><div class="logo-mark">DR</div><div>Driver Routing<br><small>Frontend MVP</small></div></div><div class="role-pill">${state.activeView === "admin" ? "Admin / Dispatcher" : "Driver"}</div></header>
      <main>${renderHero(state)}<nav class="tabs"><button class="tab ${state.activeView === "admin" ? "active" : ""}" data-view="admin">Admin</button><button class="tab ${state.activeView === "driver" ? "active" : ""}" data-view="driver">Driver</button></nav>${state.activeView === "admin" ? renderAdmin(state) : renderDriver(state)}</main>
      <nav class="bottom-nav"><button class="tab ${state.activeView === "admin" ? "active" : ""}" data-view="admin">Admin</button><button class="tab ${state.activeView === "driver" ? "active" : ""}" data-view="driver">Driver</button></nav>
    </div>`;
  }

  function mount(root, initialState = sampleState) {
    let state = JSON.parse(JSON.stringify(initialState));
    function rerender() {
      root.innerHTML = renderApp(state);
      root.querySelectorAll("[data-view]").forEach((btn) => btn.addEventListener("click", () => { state.activeView = btn.dataset.view; rerender(); }));
      root.querySelectorAll("[data-order][data-status]").forEach((btn) => btn.addEventListener("click", () => {
        state.routes.forEach((route) => route.stops.forEach((stop) => { if (stop.order_id === btn.dataset.order) stop.status = btn.dataset.status; }));
        state.activeView = "driver";
        rerender();
      }));
    }
    rerender();
    return { getState: () => state, setState: (next) => { state = next; rerender(); } };
  }

  const exported = { api, sampleState, metersToKm, secondsToMin, statusClass, dashboardMetrics, importMetrics, nextActionFor, renderApp, mount };
  if (typeof module !== "undefined" && module.exports) module.exports = exported;
  global.DriverRoutingFrontend = exported;
  if (typeof document !== "undefined") mount(document.getElementById("app"));
})(typeof window !== "undefined" ? window : globalThis);
