---
name: nethserver-containerfile
description: 'Write and review secure, production-ready Containerfiles following NethServer container best practices. Use when creating a new Containerfile, reviewing an existing container image, or mentions "/Containerfile". Supports: (1) Rootless container configuration with non-root USER, (2) Multi-stage build separation of build and runtime, (3) Minimal and pinned base image selection (Alpine/Debian-slim), (4) Vulnerability scanning guidance with Trivy and layer inspection with Dive, (5) Renovate setup for automated dependency updates'
---

# NethServer Secure Containerfile

## Overview

Write and review Containerfiles following NethServer container security best practices.
Source: [NethServer Development Handbook — Creating Secure Containers](https://nethserver.github.io/dev/best_practices/#creating-secure-containers)

---

## Rules (apply all unless explicitly overridden)

### 1. Rootless containers

Always run the container as a non-root user. Add a dedicated user at the end of the build stage:

```Containerfile
RUN adduser -D -u 1001 appuser
USER appuser
```

If the upstream image already defines a non-root user (e.g., `node`, `nobody`), use it.
Only omit this if the software cannot run rootless and you explicitly document why.

### 2. Multi-stage builds

Separate the build environment from the runtime image to keep the final image small and free of build tools:

```Containerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

# Stage 2: Runtime
FROM alpine:3.20
WORKDIR /app
COPY --from=builder /app/myapp .
USER nobody
CMD ["./myapp"]
```

Use multi-stage builds for any compiled language (Go, Rust, Java, C/C++) and for Node.js apps that require a build step.

### 3. Minimal base images

Prefer minimal base images to reduce attack surface:

- **First choice**: `alpine:X.Y` — smallest, fewest packages
- **Fallback** (MUSL incompatibility): `debian:X.Y-slim` or `ubuntu:X.Y`

```Containerfile
# Preferred
FROM alpine:3.20

# Fallback when Alpine is not compatible
FROM debian:12-slim
```

Never use bare distro images (`FROM ubuntu`, `FROM debian`) without the `slim` or `minimal` variant unless strictly required.

### 4. Pin image versions — never use `latest`

Always specify the exact version tag:

```Containerfile
# Good
FROM alpine:3.20
FROM node:20-alpine3.20

# Bad — never do this
FROM alpine:latest
FROM node
```

Pinned versions ensure reproducible builds and prevent unexpected breakage from upstream changes.

### 5. Dependency pinning (optional, project-dependent)

When installing packages, you may pin versions for reproducibility:

```Containerfile
# Alpine
RUN apk add --no-cache openssl=3.3.0-r0

# Debian/Ubuntu
RUN apt-get install -y --no-install-recommends openssl=3.0.11-1
```

**Trade-off**: strict pinning improves reproducibility but can delay security patches.
Use Renovate (see below) to automate updates when pinning is used.

### 6. Automate dependency updates with Renovate

Add a `renovate.json` to the repository to keep base image versions and dependencies updated automatically.
The NethServer default Renovate config is available at [NethServer/.github](https://github.com/NethServer/.github).

### 7. No secrets in layers

- Never `COPY` `.env` files, private keys, or credentials into the image.
- Never pass secrets as `ARG` or `ENV` variables that end up in the final layer.
- Use Docker secrets or environment injection at runtime instead.

---

## Checklist before finishing a Containerfile

- [ ] Final stage uses a non-root `USER`
- [ ] Multi-stage build separates build and runtime (for compiled/built apps)
- [ ] Base image tag is pinned (no `latest`)
- [ ] Base image is minimal (`alpine` or `*-slim`)
- [ ] No secrets or credentials baked into layers
- [ ] Renovate is configured for automated updates
- [ ] Image analyzed with [Dive](https://github.com/wagoodman/dive) to inspect layers
- [ ] Image scanned with [Trivy](https://github.com/aquasecurity/trivy) for CVEs and secrets
- [ ] SBOM generated with Trivy in CycloneDX format (`.cdx.json`) and attached to the release

---

## Scanning and tooling

### Trivy — vulnerability scan

```bash
# Scan a local image
trivy image myapp:latest

# Generate CycloneDX SBOM
trivy image --format cyclonedx --output myapp.cdx.json myapp:latest
```

### Dive — layer inspection

```bash
dive myapp:latest
```

Use Dive to spot unnecessary files, leftover build artifacts, or accidentally included secrets.

---

## Example: complete secure Containerfile (Go application)

```Containerfile
# Stage 1: Build
FROM golang:1.22-alpine3.20 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o myapp .

# Stage 2: Runtime
FROM alpine:3.20
RUN apk add --no-cache ca-certificates tzdata \
    && adduser -D -u 1001 appuser
WORKDIR /app
COPY --from=builder /app/myapp .
USER appuser
EXPOSE 8080
CMD ["./myapp"]
```
