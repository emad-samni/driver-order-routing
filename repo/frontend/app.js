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
    orders: [
      { id: "ORD-1001", recipient_name: "Amina Hassan", address: "Al Wasl Rd, Dubai", time_window: "09:00–11:00", status: "published", priority: "high", instructions: "Cold-chain bag; call on arrival." },
      { id: "ORD-1002", recipient_name: "Omar Clinic", address: "Jumeirah St, Dubai", time_window: "10:00–12:00", status: "en_route", priority: "normal", instructions: "Reception desk." },
      { id: "ORD-1003", recipient_name: "M. Rahman", address: "Business Bay, Dubai", time_window: "11:30–13:30", status: "delivered", priority: "normal", instructions: "Proof note captured." },
      { id: "ORD-1004", recipient_name: "Noura Ali", address: "Missing coordinates", time_window: "09:00–10:00", status: "ready_to_plan", priority: "high", exception: "missing_coordinates" },
    ],
    drivers: [
      { id: "drv-lina", name: "Lina", phone: "+971500000001", availability: "on_route", shift: "08:00–15:00", capacity: "4/8 stops" },
      { id: "drv-samir", name: "Samir", phone: "+971500000002", availability: "assigned", shift: "09:00–17:00", capacity: "1/10 stops" },
      { id: "drv-maya", name: "Maya", phone: "+971500000003", availability: "available", shift: "12:00–20:00", capacity: "0/8 stops" },
    ],
    routes: [
      {
        driver_id: "drv-lina",
        driver_name: "Lina",
        distance_meters: 7650,
        duration_seconds: 1680,
        progress: "1/3 complete",
        stops: [
          { order_id: "ORD-1001", sequence: 1, recipient_name: "Amina Hassan", address: "Al Wasl Rd, Dubai", planned_arrival: "09:18", time_window: "09:00–11:00", status: "published", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=25.2048,55.2708" },
          { order_id: "ORD-1002", sequence: 2, recipient_name: "Omar Clinic", address: "Jumeirah St, Dubai", planned_arrival: "10:04", time_window: "10:00–12:00", status: "en_route", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=25.2173,55.2531" },
          { order_id: "ORD-1003", sequence: 3, recipient_name: "M. Rahman", address: "Business Bay, Dubai", planned_arrival: "11:45", time_window: "11:30–13:30", status: "delivered", navigation_url: "https://www.google.com/maps/dir/?api=1&destination=25.1867,55.2729" },
        ],
      },
      {
        driver_id: "drv-samir",
        driver_name: "Samir",
        distance_meters: 10800,
        duration_seconds: 2300,
        progress: "0/2 complete",
        stops: [
          { order_id: "ORD-1005", sequence: 1, recipient_name: "Care Supplies LLC", address: "Karama, Dubai", planned_arrival: "12:20", time_window: "12:00–14:00", status: "published", navigation_url: "https://www.google.com/maps/search/?api=1&query=Karama+Dubai" },
          { order_id: "ORD-1006", sequence: 2, recipient_name: "Fatima S.", address: "Deira, Dubai", planned_arrival: "13:05", time_window: "12:30–15:00", status: "failed", navigation_url: "https://www.google.com/maps/search/?api=1&query=Deira+Dubai" },
        ],
      },
    ],
    unassigned: [
      { order_id: "ORD-1004", recipient_name: "Noura Ali", reason_code: "missing_coordinates", details: "Address is present but prototype requires lat/lng before route planning." },
    ],
  };

  const api = {
    createOrder: { method: "POST", path: "/orders" },
    listOrders: { method: "GET", path: "/orders" },
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
      <div class="actions"><button class="primary">Save ready order</button><button class="secondary">Import CSV batch</button></div>
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
      <div class="actions"><button class="primary">Run optimization</button><button class="secondary">Publish routes</button><button class="secondary">Manual override</button></div>
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
      <p class="panel-subtitle">Reason codes match backend unassigned outputs.</p>
      <div class="card-list">${state.unassigned.map((item) => `<article class="card exception"><div class="card-title">${escapeHtml(item.order_id)} — ${escapeHtml(item.recipient_name)}</div><div class="card-meta">${escapeHtml(item.details)}</div><div class="badges">${statusBadge(item.reason_code)}</div></article>`).join("")}</div>
    </section>`;
  }

  function renderAdmin(state) {
    return `<div class="grid two"><div class="grid">${renderOrderForm()}${renderDriverForm()}${renderExceptions(state)}</div><div>${renderPlanReview(state)}</div></div>`;
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

  const exported = { api, sampleState, metersToKm, secondsToMin, statusClass, dashboardMetrics, nextActionFor, renderApp, mount };
  if (typeof module !== "undefined" && module.exports) module.exports = exported;
  global.DriverRoutingFrontend = exported;
  if (typeof document !== "undefined") mount(document.getElementById("app"));
})(typeof window !== "undefined" ? window : globalThis);
