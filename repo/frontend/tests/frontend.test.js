const assert = require("node:assert/strict");
const frontend = require("../app.js");

assert.equal(frontend.metersToKm(18450), "18.4 km");
assert.equal(frontend.secondsToMin(3980), "66 min");

const metrics = frontend.dashboardMetrics(frontend.sampleState);
assert.deepEqual(metrics.map((m) => m.label), ["Assigned", "Unassigned", "Planned km", "Plan time"]);
assert.equal(metrics[0].value, 5);
assert.equal(metrics[2].value, "18.4 km");

assert.deepEqual(frontend.nextActionFor("published"), ["accepted", "en_route", "failed"]);
assert.deepEqual(frontend.nextActionFor("arrived"), ["delivered", "failed"]);
assert.deepEqual(frontend.nextActionFor("delivered"), []);

assert.equal(frontend.api.driverRouteToday.method, "GET");
assert.equal(frontend.api.driverRouteToday.path, "/driver/me/routes/today");
assert.equal(frontend.api.statusEvent.path, "/orders/{id}/status-events");

const adminHtml = frontend.renderApp({ ...frontend.sampleState, activeView: "admin" });
assert.match(adminHtml, /Plan review &amp; publish|Plan review & publish/);
assert.match(adminHtml, /Exception queue/);
assert.match(adminHtml, /Quick order intake/);
assert.match(adminHtml, /missing_coordinates/);

const driverHtml = frontend.renderApp({ ...frontend.sampleState, activeView: "driver" });
assert.match(driverHtml, /Today&#39;s route|Today's route/);
assert.match(driverHtml, /Open navigation/);
assert.match(driverHtml, /data-status="accepted"|data-status="arrived"/);

console.log("Frontend prototype tests passed");
