# Manual Deployment

Manual deployment requires no custom code.

## Requirements

- Two AI assistants
- One shared folder
- Read access for both assistants
- Write access for at least one assistant, or a user who can upload generated files

## Procedure

1. Initialize the exchange workspace.
2. Upload the primary evidence.
3. Generate the recursive evidence manifest.
4. Review nested folders, duplicate groups, archives, unsupported types, and connector limitations.
5. Run the evidence-coverage check and record what was opened, parsed, and visually inspected.
6. Do not make definitive absence claims until the missing-claim gate is satisfied.
7. Ask Model A to create the initial challenge.
8. Tell Model B that a new numbered message exists.
9. Model B writes or generates the response file.
10. Tell Model A that the response exists.
11. Continue until the finish-line rule is met.

The human relays only turn notifications, not the substantive argument.

## Fresh-chat recovery

When a model's chat becomes too large, save its latest meaningful conclusions as a non-governing context snapshot, start a new chat, point the model to `START_HERE.md`, and require re-verification against primary evidence and the current coverage report.
