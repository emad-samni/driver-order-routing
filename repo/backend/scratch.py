from app.main import service, _driver_from_payload, _order_from_payload
service.orders.clear(); service.drivers.clear(); service.import_batches.clear(); service.planning_runs.clear(); service.status_events.clear()
d = _driver_from_payload({'name': 'Integration Driver', 'start_location': {'lat': 52.5, 'lng': 13.4}, 'shift_start': '08:00', 'shift_end': '18:00', 'max_stops': 5, 'capacity_units': 20})
print('driver valid:', d.validate_for_planning())
print('available:', d.is_available_for_planning)
o = _order_from_payload({'order_id': 'RET-INT-2', 'recipient_name': 'Planning Customer', 'address': 'Damrak 1, 1012 Amsterdam', 'delivery_date': '2026-08-03', 'time_window_start': '10:00', 'time_window_end': '13:00', 'latitude': 52.3738, 'longitude': 4.8909})
print('order valid:', o.validate_for_planning())
print('order status before planning:', o.status)
run = service.run_planning(o.delivery_date)
print('routes:', len(run.routes), 'unassigned:', len(run.unassigned_orders))
for item in run.unassigned_orders:
    print(' unassigned reason:', item.reason_code, item.details)
