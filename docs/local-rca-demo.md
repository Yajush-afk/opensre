# Local RCA Demo

This is the fastest path to a first RCA report.

It runs a bundled alert and evidence fixture locally, renders the RCA in your terminal, and does not require a Tracer account, Slack, Datadog, or AWS credentials.

## Prerequisites

- Python 3.11+
- `make`
- One LLM key

Use Anthropic by default:

```bash
ANTHROPIC_API_KEY=your-key
```

Or switch to OpenAI:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

## Run the demo

```bash
make install
cp .env.example .env
make local-rca-demo
```

The report is printed in the terminal. When running inside Cursor or VS Code, Tracer also opens the last report in your editor.

## Save the report to a file

```bash
python3 -m app.demo.local_rca --output /tmp/tracer-local-rca.md
```

## What this demo uses

- Bundled Datadog-style alert payload
- Bundled Datadog logs and monitor evidence
- The real RCA diagnosis and report renderer

## Next step

If you want to run Tracer against your own systems, continue with [SETUP.md](../SETUP.md).
