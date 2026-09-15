# Cards/Management

## PUT /api/v1/cards/{cardId}/block

**Block card**

Blocks selected card making it impossible to use it for any transactions.

---

## PUT /api/v1/cards/{cardId}/close

**Close card**

Closes the card. This action cannot be undone and the card will be permanently closed.

---

## PUT /api/v1/cards/{cardId}/limit

**Change card limit**

Updates maximum amount that can be spent using the card within a day

---

## PUT /api/v1/cards/{cardId}/name

**Change card name**

Updates the display name of the card

---

## PUT /api/v1/cards/{cardId}/unblock

**Unblock card**

Unblocks selected card allowing it to be used for transactions once again.

---

