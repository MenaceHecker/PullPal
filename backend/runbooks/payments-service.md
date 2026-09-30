# Payments Service

## Overview

payments-service is the only thing in the stack that talks to the
external payment provider. checkout-service calls it synchronously for
every order, so any slowness here shows up directly as checkout latency,
not just payments-service's own metrics.

## Dependencies

- External payment provider (outbound HTTPS, not part of this stack)
- A connection pool sized for the provider's expected concurrency

## Normal operating range

- error rate: under 2%
- p50 latency: ~110ms, occasionally higher right after a provider-side
  incident on their end, which is out of our control
- request volume: 30-70 requests per tick under normal simulated load

## Known issues

### Provider timeouts after a connection pool change

Symptom: `Timeout calling payment-provider after 30000ms for charge
{order_id}`, `ConnectionPoolExhausted: no available connections to
payment-provider`, and `Retry limit exceeded charging card for order
{order_id}, giving up`. Latency climbs sharply, often four times normal
or worse, alongside the error rate.

Root cause: the connection pool to the payment provider was sized too
small for actual concurrency. Under load, requests queue up waiting for a
free connection, some of them time out before ever getting one, and the
retry logic burns through its budget without making progress.

Check deploy history for a recent change to the payment-provider
connection pool size before assuming the provider itself is degraded.
The provider's own status page is the other thing worth checking, since
this exact symptom (timeouts plus pool exhaustion) can also happen if
they are genuinely having an incident on their end.

### Distinguishing "we caused it" from "they caused it"

If error rate is up but latency is roughly normal, that points at the
provider rejecting requests, not a pool problem here. Pool exhaustion
specifically shows up as latency climbing first, errors following.

## Escalation

Payment failures are revenue-impacting the same way checkout failures
are. If this is a provider-side incident, there is nothing to roll back
on our end, escalate to communicate status rather than to fix anything.
