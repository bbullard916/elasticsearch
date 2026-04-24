# Elastic Defend causing Microsoft Word to hang during document close due to requeueing of file scans

## Summary

Elastic Defend (Elastic Endpoint) can cause Microsoft Word to hang for 30–60 seconds when closing documents. The hang is caused by the malware scanner generating a burst of requeue events for Office-related files (lock files, telemetry databases, temp/cache files) during Word's close/save sequence. Kernel-level filter operations block synchronously while the user-space security service processes scan decisions, serializing Word's file operations through the event pipeline.

## Environment

- Elastic Defend (Elastic Endpoint) integrated via Elastic Agent, version 9.3
- Self-managed / on-premise deployment
- Windows hosts running Microsoft Office (Word)
- Observed when opening and closing documents stored on local disk and on user profile paths

## Observed behavior

During Word document close, the malware scanner generates a large number of requeue events for files associated with `WINWORD.EXE` (for example, Office lock files, telemetry databases, and temp/cache files). Requeue events occur repeatedly—many times per file—over a 2–3 minute window, producing a burst of queue activity that blocks Word's file close sequence. Kernel-level filter operations are held synchronously while the user-space security service processes scan decisions, causing applications to wait and exhibit 30–60 second hangs.

## Root cause

Word's normal close/save sequence holds file handles while flushing multiple files simultaneously. Elastic Defend's malware scanner attempts to open those files for scanning but encounters locks or I/O errors and requeues the files. The repeated requeueing, combined with synchronous allow/deny decisions processed by the security service, serializes Word's file operations through the event pipeline and prevents timely completion of the close sequence.

A contributing factor is cross-EDR interference: concurrent endpoint protection products can block or delay access to `elastic-endpoint.exe`, which causes or exacerbates the behavior.

## Customer fix

In at least one instance, the root cause was traced to another EDR product interfering with Elastic Defend. Adding `C:\Program Files\Elastic\Endpoint\elastic-endpoint.exe` to the other EDR's real-time file system protection exceptions resolved the issue entirely. Adding `WINWORD.EXE` as a Trusted Application in Elastic Defend also resolved the hang independently, but the underlying trigger was the cross-EDR interference. Both mitigations are effective and can be applied together or separately depending on the environment.

## Immediate mitigations

### 1. Exclude Elastic Endpoint from other EDR products

If another endpoint protection product is running on the same host, add `elastic-endpoint.exe` to that product's real-time file system protection exceptions and retest.

**Path to exclude:**

```
C:\Program Files\Elastic\Endpoint\elastic-endpoint.exe
```

Cross-EDR interference has been confirmed to cause this behavior. Resolving the interference may eliminate the need for Trusted Application exclusions in Elastic Defend entirely.

### 2. Add Trusted Application entries for Microsoft Office processes

Add `WINWORD.EXE` (and other Office executables as needed) as a Trusted Application in Elastic Defend. This bypasses synchronous file scanning for writes originating from those processes and prevents the requeue storm that causes the hang.

> **Note:** Trusted Application exclusions bypass synchronous on-write scanning for files written by the excluded process and therefore reduce coverage for file-drop scenarios originating solely from that process. Behavioral protections, process event collection, memory scanning, and API monitoring remain active and continue to provide detection for many document-delivered threats.

### 3. Add targeted Event Filters for Office artifacts

Add Event Filters to reduce unnecessary events that trigger scanning for innocuous Office artifacts. Recommended patterns include:

- `~$*.docx`, `~$*.xlsx`, `~$*.pptx` (Office lock files)
- Office sandbox temp paths scoped to user profiles
- Office telemetry SQLite files (`*.db`, `*.db-journal`, `*.db-wal` in Office telemetry directories)
- Word diagnostic logs and cache locations

Event filters reduce the volume of file events sent to Elasticsearch while leaving kernel interception and malware scanning behavior intact. They prevent writing events to Elasticsearch but do not reduce kernel interception or scanning by themselves. Use event filters to lower noise and queue pressure from harmless Office infrastructure files.

## Additional troubleshooting

If the mitigations above are ineffective:

1. **Check for other endpoint protection products** running on the same host. If another EDR is present, add `elastic-endpoint.exe` to that product's real-time file system protection exceptions and retest.

2. **Collect an Elastic Agent diagnostic bundle** during reproduction and review endpoint logs for the following evidence:
   - Requeue messages (for example, `Queue.cpp` entries showing repeated requeueing of Office-related files)
   - Sync decision logs showing synchronous allow/deny processing (for example, `SyncKernelMessageManager` entries)
   - I/O errors or "Invalid file" messages when attempting to load transient Office files

## Long-term considerations

- If Trusted Application exclusions are required broadly, review the organization's threat model because on-write protections for file drops from excluded processes will be bypassed.
- Consider narrowing exclusions (scoped paths, targeted file patterns) to reduce detection surface loss while addressing the performance impact.
- If requeue storms persist despite mitigations, escalate with diagnostic evidence for developer analysis to evaluate whether the requeue logic or synchronous decision path can be optimized to avoid serializing application file close sequences.

## References

- [Elastic Defend: Trusted Applications](https://www.elastic.co/guide/en/security/current/trusted-apps-ov.html)
- [Elastic Defend: Event Filters](https://www.elastic.co/guide/en/security/current/event-filters.html)
