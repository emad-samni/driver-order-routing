const assert = require("node:assert/strict");
const frontend = require("../app.js");

assert.equal(frontend.metersToKm(18450), "18.4 km");
assert.equal(frontend.secondsToMin(3980), "66 min");

const state = frontend.sampleState;
assert.deepEqual(frontend.dashboardMetrics(state).map((m) => m.label), ["Assigned", "Unassigned", "Planned km", "Plan time"]);
assert.equal(frontend.dashboardMetrics(state)[0].value, 5);
assert.equal(frontend.dashboardMetrics(state)[2].value, "18.4 km");

assert.deepEqual(frontend.nextActionFor("published"), ["accepted", "en_route", "failed"]);
assert.deepEqual(frontend.nextActionFor("arrived"), ["delivered", "failed"]);
assert.deepEqual(frontend.nextActionFor("delivered"), []);

assert.equal(frontend.api.driverRouteToday.method, "GET");
assert.equal(frontend.api.driverRouteToday.path, "/driver/me/routes/today");
assert.equal(frontend.api.statusEvent.path, "/orders/{id}/status-events");
assert.equal(frontend.api.excelTemplate.path, "/excel-template");
assert.equal(frontend.api.importExcel.path, "/orders/import/excel");

const importMetrics = frontend.importMetrics(state.importBatch);
assert.deepEqual(importMetrics.map((m) => m.label), ["Rows", "Ready", "Draft", "Errors"]);
assert.equal(importMetrics[1].value, 3);
assert.equal(importMetrics[3].value, 3);

const adminHtml = frontend.renderApp({ ...state, activeView: "admin" });
assert.match(adminHtml, /Quick order intake/);
assert.match(adminHtml, /Excel order import/);
assert.match(adminHtml, /Driver capacity/);
assert.match(adminHtml, /Plan review & publish/);
assert.match(adminHtml, /Exception queue/);
assert.match(adminHtml, /Upload \.xlsx/);

const driverHtml = frontend.renderApp({ ...state, activeView: "driver" });
assert.match(driverHtml, /Today's route/);

console.log("Frontend prototype tests passed");
