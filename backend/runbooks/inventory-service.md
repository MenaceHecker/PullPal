# Inventory Service

## Overview

inventory-service tracks stock levels and reserves inventory for every
order checkout-service creates. It's called synchronously during
checkout, same as payments-service, so problems here also show up as
checkout latency and failures even though the root cause is elsewhere.

## Dependencies

- Postgres `inventory` table
- An in-process cache of recent stock lookups, to avoid hitting the
  database for every single reservation check

## Normal operating range

- error rate: under 2%
- p50 latency: ~110ms
- request volume: 30-70 requests per tick under normal simulated load

## Known issues

### Worker restarts from a stock-reservation cache leak

Symptom: `OOMKilled: inventory-worker exceeded memory limit (512Mi)`,
`Process restarted unexpectedly while reserving stock for order
{order_id}`, and `Failed to reserve inventory for order {order_id}:
worker unavailable`. Error rate and latency both climb, and the pattern
is often choppy rather than a clean step change, since it tracks the
worker's memory growth and restart cycle rather than a single bad
request path.

Root cause: the stock-reservation cache was changed to cache lookups in
process memory without an eviction policy. Under sustained load the
cache grows unbounded until the worker hits its memory limit and gets
killed, at which point in-flight reservations fail and the worker
restarts with a cold (and then immediately regrowing) cache.

Check deploy history for a recent change to how stock lookups are
cached. The fix is adding an eviction policy or a size cap to the cache,
not just restarting the worker, since it will just leak again.

### How this differs from a normal blip

A single restart with a quick recovery is not this issue, workers do
restart occasionally for unrelated reasons. This issue specifically
looks like a slow climb in error rate and latency over several minutes
before the restart, then a partial recovery that starts climbing again.

## Escalation

Out-of-stock false negatives during this incident (reservations failing
even though stock exists) directly cost sales, treat sustained elevated
error rate here the same as a checkout-service incident.
