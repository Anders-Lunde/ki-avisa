# Shared virtual server

KI-avisa's public site runs on Cloudflare Pages; see [HOSTING.md](HOSTING.md).
The existing SSH alias `hetzner-root` points to the shared AgentHouse/Train My
Camera Ubuntu host. Changing that VM does not deploy KI-avisa or change its
Cloudflare configuration. Confirm the hostname and current service inventory
before maintenance, because the VM supports other projects too.

## Security maintenance, 7 November 2026

The authorized hardening pass patched Caddy and the installed Chrome browser,
restricted shared credentials to their owner, reduced SSH's unauthenticated
connection window, enabled more detailed SSH key logging, and added Caddy's
`NoNewPrivileges` systemd setting. Automatic security updates remain enabled,
with unattended reboots explicitly disabled. Existing SSH key access,
forwarding, X11, Tailscale and firewall allowances were preserved.

A pre-existing fetch-proxy restart loop was repaired by replacing Pydantic's
removed `Field(regex=...)` argument with `pattern=...`. The shared source is
`AgentHouse/scripts/fetch_proxy.py`; the deployed copy was backed up first.

Verification covered fresh SSH authentication, all 16 checked application and
infrastructure services, backend health, the public application and auth check,
private-port isolation, and a sandboxed headless Chrome launch. There was no
host reboot or content deployment. Camera capture, uploads and authenticated
user workflows were not exercised.

Private findings, outstanding maintenance, exact receipts and rollback notes:
`v5/workspace/security/20261107-hetzner/REPORT.md` (ignored by Git).
The VM's protected backup and receipts are under
`/var/backups/ki-avisa-hardening/20261107T171347Z/`.
Do not commit private receipts, raw logs, environment files or OAuth material.

Before further hardening, read that report and the VM's current receipts rather
than repeating this run. Review the unresolved package coverage and service
privilege findings at the next maintenance pass; those changes need their own
compatibility checks.

## Service isolation follow-up, 7 November 2026

The eight research proxies now run as `ah-research`. The Train My Camera API,
auth service and four application jobs use `tmc-app`. Both are dedicated
non-login accounts. systemd blocks privilege escalation and filesystem writes
outside the existing application data/state paths and service homes. Existing
operator/root access and the T3 administrative development service are intact.

The migration preserved existing media, databases, quotas and model files.
Database, media write/read, real DINOv3 embeddings, segmentation, FFmpeg and
offline sentence embeddings passed under the new accounts. Public pages,
API/auth endpoints, SSH and the existing scheduled image worker also passed.
Ubuntu Pro enrollment and the outstanding ESM security updates were completed
later the same day; see the completion record below.

Current private status, verification and exact rollback instructions:
`v5/workspace/security/20261107-followup/REPORT.md`. Server backup:
`/var/backups/ki-avisa-hardening/20261107T172943Z-isolation/`.
Read the current receipt before resuming; do not repeat the identity migration.

## ESM security updates completed, 7 November 2026

The VM is attached to the owner's Ubuntu Pro free personal subscription, with
only ESM Apps enabled. All 19 outstanding security package updates were applied.
Ubuntu reports zero pending standard, ESM Apps or ESM Infra security updates.
Existing unattended security updates include ESM Apps; automatic reboots remain
disabled.

Fresh SSH access, public site/app responses, API/auth and research services,
database/storage, production DINOv3 embeddings, segmentation and FFmpeg passed.
No application restart or host reboot was needed. The previous package versions
were saved as 19 rollback DEBs under the protected server backup
`/var/backups/ki-avisa-hardening/20261107T175045Z-esm/`.

Private completion report: `v5/workspace/security/20261107-esm-completion/REPORT.md`.
This completes the two outstanding findings from the initial pass. Routine
nonsecurity/phased package updates and full dependency audits are separate work.

## Application dependency audit, 7 November 2026

The deployed Python API, eight research proxies, Better Auth service, web/site
builds and T3 dependency tree were audited and patched with compatibility checks
and retained rollback copies. The API and five checked npm lockfiles now have
zero reported vulnerabilities. The research environment retains Pillow 11.3
because the existing MoviePy version requires Pillow below 12; its findings
remain open. Do not force that upgrade inside the shared environment.

All 234 API tests, live model/storage/media checks, research embeddings, video
resize, browser rendering and fresh SSH passed. The auth migration only added
nullable signing-key metadata columns and preserved existing keys/sessions.
T3 keeps its existing application version and Tailscale address. Existing
credentials, customer data and Stripe API version were preserved. Previous
static assets remain available for already-open tabs.

Mobile npm dependencies were patched in source, including the Capacitor native
security fix. Installed native apps are not patched by the server update:
native dependency synchronization, Android/iOS builds and redistribution remain
necessary. The VM has no native build toolchains. No native release was made.

The 5–6 November OpenSSH password-bypass report (CVE-2026-123158) requires musl
without PAM and enabled password authentication. This host uses glibc, PAM and
key-only authentication, so it does not match those exploit conditions. Ubuntu's
tracker still says "Needs evaluation"; this is a host-configuration assessment.
See the [OpenSSH release notice](https://www.openssh.org/txt/release-10.6p2) and
[Ubuntu tracker](https://ubuntu.com/security/CVE-2026-123158).

Private verification, exact changes, corrected staging error, remaining work
and rollback: `v5/workspace/security/20261107-dependencies/REPORT.md`.
Server receipts and rollback script:
`/var/backups/ki-avisa-hardening/20261107-dependencies/`.
Production database/media backup: the app's `backups/20261107T181601Z/`.
No KI-avisa publication, host reboot, key rotation or Git push was performed.
