---
name: monitor_job
version: 0.1.0
allowed_tools:
  - query_job
  - read_job_logs
---

# Monitor a Bohrium compute job

Use this skill to query job status. Treat queued and running jobs as non-terminal. Read logs after a terminal failure or when the user explicitly asks for them.

