# Rebuilding ShieldScan's Dockerfile — from broken to production-grade

*A short field report on why the previous Dockerfile could not build any more, what a production replacement looks like, and how ShieldScan flagged its own CI workflow the first time we pointed it at real code.*

---

## The starting point

ShieldScan is a small SAST + SCA + Secrets pipeline built on Semgrep, Trivy, and Gitleaks, with a local Ollama model on top that turns raw scanner output into a triaged, human-readable report. The tool was solid; the packaging was not.

The existing Dockerfile was a single-stage `python:3.11-slim` image that installed `git`, `curl`, and `wget` with `apt`, then bolted Semgrep on with `pip`, Trivy from an apt repo, and Gitleaks from a GitHub release binary — all as root, in one layer soup, with no version pins anywhere. The first thing I wanted was a baseline build to compare against. That comparison never happened.

```
STEP 4/11: RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && ...
/bin/sh: 1: apt-key: not found
Error: building at STEP "RUN wget ..." while running runtime: exit status 127
```

`apt-key` was removed from Debian trixie. `python:3.11-slim` moved onto trixie some months ago. The Dockerfile has been silently broken since. This is exactly the failure mode a CI-linked container build is supposed to prevent: a Dockerfile is code that rots when the base image moves, and if nothing builds it on a schedule, the rot is invisible until someone tries to use it.

## The rewrite — what changed and why

### Three stages instead of one

```
scanners  ── downloads Trivy + Gitleaks release tarballs
pydeps    ── installs Semgrep + app deps into a portable prefix
runtime   ── copies only the finished artifacts, adds git + a non-root user
```

The three-stage split is not for image size alone (though the runtime image drops the `curl` / build tooling from the earlier stages). It's for **auditability**: the runtime layer contains only the four things the app actually invokes at run time (`python`, `semgrep`, `trivy`, `gitleaks`) plus `git` for the scanners that consume repos. Everything a reviewer might ask "why is this in the final image?" about is gone.

### Pinning versions is not optional

The original Dockerfile had `pip install semgrep` (latest), an apt install of `trivy` (whatever the apt repo serves that hour), and `gitleaks v8.18.0` (a hardcoded old version). This means three different reproducibility stories in one file.

The new Dockerfile pins all four moving parts:

- `python:3.11.16-slim-trixie` — a specific base tag, not the rolling `3.11-slim`
- `semgrep==1.174.0` — via pip, resolvable and pinned
- Trivy `0.74.0` and Gitleaks `8.30.1` — via `ARG` variables that get baked into the URL

Both scanner versions were the latest stable at build time; I verified them by hitting `api.github.com/repos/{owner}/{repo}/releases/latest` rather than trusting a README. That verification step is worth doing every time — READMEs go stale, release feeds don't.

### No apt repo for third-party tools

The Trivy and Gitleaks installs no longer use `apt-key`, `signed-by` keyrings, or the Aquasec apt repo at all. Both binaries are downloaded as tarballs from their upstream GitHub Releases, extracted, and dropped into `/usr/local/bin`. This is not just apt-key avoidance — it removes an entire class of breakage. An upstream apt repo can change its signing key, deprecate a distribution codename, or serve a different binary. A `.tar.gz` at a pinned URL either exists byte-for-byte or 404s. The failure mode is loud, not subtle.

### Non-root user

The runtime stage creates `shield` (UID 10001, GID 10001) and switches to it before the entrypoint. UID 10001 is deliberately outside the typical host UID range (0–999 for system users, ~1000 for the first desktop user), which prevents accidental collisions when host directories are bind-mounted. The trade-off is that `docker run -v $(pwd):/work` needs `--user "$(id -u):$(id -g)"` (Docker) or `--userns=keep-id:uid=10001,gid=10001` (rootless Podman) so the container process can write reports back to the host. Both flags are documented in the README.

### `.dockerignore`

The old build had no `.dockerignore`, meaning the entire repo (including `.git`, `.env` if present, past `security_report_*.md` outputs, and any local `venv/`) was streamed into the build context. The new one excludes `.git`, `.env*` (except `.env.example`), Python cache directories, `assets/`, docs, and generated report files. Two effects: build context shrinks from megabytes to kilobytes, and secrets in `.env` cannot accidentally leak into an intermediate layer.

## The CI workflow

Three jobs, roughly one per failure mode:

```
lint   ──▶  build  ──▶  smoke
```

**`lint`** runs Hadolint against the Dockerfile with `failure-threshold: warning` and `ignore: DL3008`. DL3008 asks for pinned apt package versions (`git=1:2.47.3-...`). In practice this is the wrong trade-off for third-party base images — the Debian archive periodically drops old package versions, so pinning breaks the build every few months. Every mature production Dockerfile I've read ignores DL3008 for this reason; hitting the same conclusion feels less like a shortcut and more like joining the club.

**`build`** uses `docker/build-push-action@v6` with `type=gha` layer caching and `outputs: type=docker,dest=/tmp/shieldscan.tar`. The image tarball is uploaded as an artifact so the smoke job doesn't rebuild — a design that trades ~1 MB of artifact upload for ~2 minutes of duplicated build.

**`smoke`** downloads the artifact, loads it, verifies each scanner is on `PATH` inside the container, prepares a small fixture (`chown`ed to UID 10001 so the non-root user can write reports), runs an end-to-end scan, and asserts both `security_report_*.md` and `findings_*.json` exist. If any of that regresses, the workflow fails visibly.

Locally I proved the pipeline before pushing by (1) running Hadolint through Podman with the CI's exact flags, (2) validating the YAML with Python's `yaml.safe_load`, and (3) running the Podman build + smoke sequence by hand. First real CI run: green.

## The meta-finding — ShieldScan versus its own workflow

The interesting part came when I pointed the newly-containerized ShieldScan at `progress-payment`, a Python repo I know well. Semgrep produced six findings — all identical:

> GitHub Actions step uses a mutable tag or branch reference. Tags and branch names can be silently repointed by the action owner, enabling supply-chain attacks — as seen in the trivy-action and kics-github-action compromises. Pin the reference to a full 40-character commit SHA instead.

Those six findings live in progress-payment's `.github/workflows/ci.yml` at lines 13, 15, 31, 33, 52 — every `uses: actions/checkout@v4` and friends. **Every one of them also applies to the ShieldScan CI workflow I had just written.** The tool found the exact anti-pattern in the exact file I had shipped a commit earlier.

That's the strongest possible signal that the pipeline is doing real work, not producing plausible-sounding noise. It also gave me the first concrete Faz 2 follow-up: harden ShieldScan's own CI to SHA-pinned actions, which is a small mechanical change and a straightforward writeup on its own.

## LLM triage — what it actually contributes

The scan ran twice: once with `mistral` not pulled locally (so Ollama returned 404 and the deterministic fallback report kicked in), then again after `ollama pull mistral`. Same six findings both times, very different reports.

The fallback report walks the raw finding list and prints the first five identically-worded warnings. It's what you'd write in an afternoon.

The LLM triage report opens with an executive summary, groups all six into a single `Issue` block with the shared rule and all five line numbers, categorizes the whole cluster as `WARNING → Medium`, gives a concrete remediation (pin to SHA), and adds preventive advice beyond the specific findings (signed and verified actions).

The value of the LLM is not that it does security analysis — Semgrep did that, and the six findings exist with or without Ollama. The value is that it takes N raw finding lines and produces a shape a human can act on in thirty seconds instead of ten minutes. That is the entire "Katman 2" thesis of the wider Awaken strategy in one demo: **real tool does the analysis, the model does the presentation.** Anything that inverts that — a model pretending to do the analysis — is where AI-branded security tooling goes wrong.

## How AI was used to write this

Every artefact in this Faz 1 pass — the new Dockerfile, the `.dockerignore`, the CI workflow, the README edits, and this writeup — was drafted by Claude Opus 4.7 acting as a paired engineer, with me approving each design decision, running the local builds and tests, and making the judgement calls (which base image to use, whether to pin apt packages, whether to install Podman or Docker, whether to pull `mistral` or skip the LLM path). The model chose sensible defaults (multi-stage, non-root, `.dockerignore`, three-job CI with cache) and I checked each one against what the repo actually needed; wherever it guessed at moving targets (release versions, Docker Hub tags), we verified against live sources before committing. The point of doing it this way is not just to ship faster — it's so that the next time I do something like this, I know which decisions to challenge.

## What's next

- **SHA-pin ShieldScan's own CI actions** so the tool passes its own scan.
- **Repeat the same Dockerfile + CI + writeup treatment on a second repo** to close out Faz 1. Current candidate: `dns-threat-intelligence-tool`, which has no Docker packaging yet — a cleaner "green field" test than a rewrite.
- **Faz 2 sketch:** turn the ShieldScan pipeline into a reusable "drop-in security workflow" template that other open-source repos can adopt with a single-file PR. That is where the tool stops being a demo and starts being a contribution.
