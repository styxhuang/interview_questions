---
name: submit_job
version: 0.1.0
allowed_tools:
  - submit_job
  - query_job
---

# Submit a Bohrium compute job

Use this skill when the user wants to start a compute job.

Before submission, collect an image, command, CPU count and memory size. Attach a stable client request id so a lost response can be reconciled before another submission is attempted.

