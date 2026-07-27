# Claim Status Dimensions

A single label such as “approved” is often too vague to govern action.

SEEP keeps at least four status dimensions separate:

| Dimension | Question |
|---|---|
| Submission | Was the item transmitted for review? |
| Approval | Did an authorized party approve it? |
| Compliance | Does it satisfy the governing requirement or an approved deviation? |
| Execution | Is it released, ready, blocked, fabricated, deployed, or complete? |

Example:

```json
{
  "status_dimensions": {
    "submission": "submitted",
    "approval": "approved-as-noted",
    "compliance": "unresolved-deviation",
    "execution": "hold-before-release"
  }
}
```

These values are project-defined strings because industries use different formal terms. The protocol requirement is separation, not one universal vocabulary.
