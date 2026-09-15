# Cards/3DS

## GET /api/v1/cards/3ds/requests

**Get active requests**

Retrieves active 3DS requests that need to be either approved or declined

---

## POST /api/v1/cards/3ds/requests/{transactionId}/approve

**Approve request**

Approves 3DS request allowing the transaction to proceed

---

## POST /api/v1/cards/3ds/requests/{transactionId}/decline

**Decline request**

Declines 3DS request blocking the transaction from proceeding

---

