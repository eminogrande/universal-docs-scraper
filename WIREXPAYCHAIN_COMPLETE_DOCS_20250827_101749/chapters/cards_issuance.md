# Cards/Issuance

## POST /api/v1/cards/plastic

**Issue plastic card**

Issues a plastic card for the specified user and sends it to the provided address.

---

## POST /api/v1/cards/virtual

**Issue virtual card**

Issues a virtual card for the specified user

---

## PUT /api/v1/cards/{cardId}/activate

**Activate card**

Activates a card that has been issues to a user and is currently in **NotActivated** state. </br> **Note:** This endpoint is needed only for physical cards to provide additional layer of security in case the card is stolen during delivery.

---

