# Scheduled-Agent Deployment

Scheduled tasks can reduce manual turn notifications.

## Important limitation

A watcher on one AI platform normally cannot wake a session on another platform. Each side needs its own scheduled watcher, an API broker, or a human nudge.

## Safe watcher behavior

1. Poll no more frequently than the platform permits.
2. Find the newest unanswered message.
3. Check for an existing reply before doing work.
4. Write exactly one response.
5. Remain silent when nothing changed.
6. Notify only when the other model must be prompted, a human decision is required, an error blocks progress, or the review is complete.
7. Stop when the completion marker exists.

Before creating a watcher, check for an existing task to avoid duplicate replies.
