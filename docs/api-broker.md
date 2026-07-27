# API Broker

A broker can fully automate the exchange between model providers.

## Components

- storage adapter;
- message scanner;
- schema validator;
- evidence retriever;
- provider adapters;
- budget and round limiter;
- completion evaluator;
- human escalation channel.

## Processing loop

```text
1. Detect a new unanswered message.
2. Validate its schema and identifiers.
3. Load protocol, state, and referenced evidence.
4. Call the intended recipient model.
5. Validate the model output.
6. Save it as a new append-only file.
7. Update state through a new versioned state file.
8. Evaluate the finish line.
9. Repeat or escalate.
```

## Production requirements

Use idempotency keys, duplicate-reply detection, bounded retries, maximum review rounds, spending and token limits, audit logs, provider timeouts, malware scanning, prompt-injection defenses, human approval gates, secrets management, and least-privilege storage credentials.
