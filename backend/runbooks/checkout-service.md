# Checkout Service

## Overview

checkout-service owns the cart-to-order flow. It receives `POST /checkout`
from the frontend, validates the cart contents, creates an order record,
and hands off to payments-service and inventory-service to finish the
purchase. It is the most user-facing service in the stack: any elevated
error rate here shows up immediately as failed purchases.

## Dependencies

- payments-service (synchronous call, blocks the checkout response)
- inventory-service (synchronous call, blocks the checkout response)
- Postgres `orders` table

## Normal operating range

- error rate: under 2%
- p50 latency: ~110ms
- request volume: 30-70 requests per tick under normal simulated load

Anything sustained above 5% error rate should be treated as an active
incident, not noise.

## Known issues

### Missing shipping_method field causes 500s

Symptom: `500 Internal Server Error handling POST /checkout: KeyError:
'shipping_method'`, sometimes surfacing instead as `OrderCreationError:
missing required field shipping_method for order {order_id}` or
`Unhandled exception in checkout flow: 'shipping_method' not found in
request body`.

Root cause: a deploy changed the checkout request schema to require a
`shipping_method` field but didn't add a default or backward-compatible
fallback for clients still sending the old request shape. Every request
missing the field throws a KeyError deep in order creation.

This is the single most common incident on this service. If you see this
exact error signature, check deploy history for a recent change to the
checkout request schema or order creation code before looking anywhere
else. The fix is almost always either rolling back that deploy or shipping
a hotfix that defaults `shipping_method` when absent.

### Elevated latency without elevated errors

If latency climbs but the error rate stays flat, suspect payments-service
or inventory-service slowness rather than checkout-service itself, since
both downstream calls are synchronous and block the checkout response.
Check their metrics before assuming the problem is here.

## Escalation

If error rate stays above 20% for more than a few minutes and the cause
isn't obvious from deploy history, treat it as customer-impacting and
escalate immediately. Checkout failures directly block revenue.
