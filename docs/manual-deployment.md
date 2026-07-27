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
3. Generate the evidence manifest.
4. Ask Model A to create the initial challenge.
5. Tell Model B that a new numbered message exists.
6. Model B writes or generates the response file.
7. Tell Model A that the response exists.
8. Continue until the finish-line rule is met.

The human relays only turn notifications, not the substantive argument.

## Fresh-chat recovery

When a model's chat becomes too large, save its latest meaningful conclusions as a non-governing context snapshot, start a new chat, point the model to `START_HERE.md`, and require re-verification against primary evidence.
