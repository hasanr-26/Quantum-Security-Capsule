# 09 — Complete Feature Guide

Every screen, every button, every script. For each one: **what it is**, **what it
does**, **why it is in the project**, and **what to say when demonstrating it**.

Use this as the operating manual and as the demo script.

---

## Contents

1. [Starting and stopping the platform](#1-starting-and-stopping-the-platform)
2. [The masthead — live status bar](#2-the-masthead--live-status-bar)
3. [Tab 01 — Settlement](#3-tab-01--settlement)
4. [Tab 02 — Packet Inspector](#4-tab-02--packet-inspector)
5. [Tab 03 — 3D Visualizer](#5-tab-03--3d-visualizer)
6. [Tab 04 — Interception Lab](#6-tab-04--interception-lab)
7. [Tab 05 — Cryptography](#7-tab-05--cryptography)
8. [Command-line demonstrations](#8-command-line-demonstrations)
9. [The test suite](#9-the-test-suite)
10. [API reference](#10-api-reference)
11. [Suggested demo running orders](#11-suggested-demo-running-orders)

---

## 1. Starting and Stopping the Platform

### Starting

```bash
cd QSC
pip install -r requirements.txt
python -m src.server.run
```

On first run this generates a TLS certificate into `certs/` and then starts two
listeners in one process:

| Address | What it is |
| :--- | :--- |
| `https://127.0.0.1:8443` | Settlement node — the API and the web workbench |
| `https://127.0.0.1:8444` | Interception proxy — a TLS-terminating middlebox |
| `https://127.0.0.1:8443/api/docs` | Auto-generated interactive API documentation |

Open `https://127.0.0.1:8443` in a browser. It will warn about the self-signed
certificate — that is expected and correct, because the certificate is one this
project generated rather than one a public CA issued. Click through
(**Advanced → Proceed**). The connection is still real TLS 1.3; the browser is
objecting to who vouched for the certificate, not to the encryption.

### Stopping

**Press `Ctrl + C` in the terminal where the server is running.** That is the
normal way. Both listeners shut down together because they run in one process.

If the terminal has been closed and the process is still holding the ports:

```powershell
# Windows PowerShell — find and stop it
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*src.server.run*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

```bash
# macOS / Linux
pkill -f "src.server.run"
```

To check whether anything is still listening:

```powershell
netstat -ano | findstr "8443 8444"
```

### Useful start-up flags

| Flag | Effect | When to use |
| :--- | :--- | :--- |
| `--no-proxy` | Starts only the settlement node, not the interception proxy | When you only need the API and want fewer moving parts |
| `--port 9443` | Runs the node on a different port | If 8443 is already taken |
| `--regenerate-cert` | Forces a fresh TLS certificate | If the certificate expired or you want a clean one |

---

## 2. The Masthead — Live Status Bar

The strip across the top polls the server every four seconds. It is the fastest
way to prove the page is talking to a live backend rather than showing fixtures:
the numbers move while you work.

| Field | What it shows | Why it matters |
| :--- | :--- | :--- |
| **Transport** | The TLS version actually negotiated (`TLSv1.3`), with a green dot when the connection is healthy | Proves real transport security, read from a live handshake |
| **Cipher** | The negotiated cipher suite, e.g. `TLS_AES_256_GCM_SHA384` | This value comes out of the OpenSSL session object — it is not typed into the page |
| **Uptime** | How long the node has been running | Shows it is a persistent service, not a script that runs and exits |
| **API Calls** | Total requests the node has served this session | Increments as you click — the simplest proof that buttons cause network traffic |
| **Capsules** | How many capsules have been built | Counts real cryptographic work done |
| **Rejected** | How many capsules were refused by the validator | Goes up when you tamper or replay — the security controls are doing something |
| **Replay Cache** | Number of single-use replay tokens consumed | Demonstrates the anti-replay store filling up |
| **ML-KEM Key** | First 12 hex characters of the current public key fingerprint | Changes when you rotate keys — proves the keyset is real and mutable |

**Demo line:** *"Everything in this bar is polled from the running node. Watch
the API call counter as I click — that is real network traffic, not a mock."*

---

## 3. Tab 01 — Settlement

**What this tab is for:** building a real payment capsule and putting it through
the full security pipeline, end to end. This is the core of the project.

### 3.1 Instruction Builder (left panel)

#### Message Standard

| Option | What it is | Why it is offered |
| :--- | :--- | :--- |
| **ISO 20022 pacs.008** | The message format that actually moves money between banks on CHAPS, TARGET2 and SWIFT gpi | The real thing a settlement system would carry. Shows the project handles genuine institutional formats, not toy strings |
| **SWIFT MT103** | The older SWIFT FIN wire format, with field tags `:20:`, `:32A:`, `:50K:`, `:59:` | Still in heavy production use. Demonstrates the capsule is format-agnostic — it protects bytes, whatever they mean |
| **Card Authorisation Record** | A PCI-DSS-scope record containing a PAN, CVV and cardholder | Used for the interception demo, because leaked card data is instantly and obviously damaging to a non-technical audience |

Every generation produces **fresh** content — new message IDs, a new UETR, live
timestamps, a randomised amount and a randomly chosen banking corridor. Build two
capsules in a row and compare: they differ. That is the answer to *"is this
hardcoded?"*

#### Validity Window (seconds)

**What it does:** sets the capsule's time-to-live — how long after issue it
remains acceptable. Default 300 seconds.

**Why it exists:** a capsule that never expires is a capsule an attacker can hold
and use later. A tight window shrinks that opportunity, and the receiver enforces
it at validation stage 2.

**Demo trick:** set it to `5`, build a capsule, wait ten seconds, then press
Transmit & Settle. Stage 2 fails with `Capsule expired at ...` — a live
demonstration of TTL enforcement rather than a claim about it.

#### Policy Jurisdiction

**What it does:** stamps a regulatory jurisdiction into the capsule's policy
block (UK / EU / US / IN).

**Why it exists:** the policy block sits **inside the SHA3-512 integrity hash**.
That means the jurisdiction, classification and hop limit are cryptographically
bound to the message — an intermediary cannot quietly relabel a payment as
belonging to a different regulatory regime without breaking the integrity check.
This matters for data-residency and cross-border compliance.

#### Rotate Keys

**What it does:** generates a brand-new ML-KEM-768 and ML-DSA-65 keypair on the
server and reports the exact key sizes and generation times.

**Why it exists:** two reasons.
1. It proves the keys are generated, not loaded from a file — the fingerprint in
   the masthead changes every time.
2. It demonstrates **key rotation invalidates old capsules.** Build a capsule,
   rotate keys, then try to settle the old capsule: it fails at stage 5, because
   the signature no longer matches the current public key. That is correct
   behaviour and a good thing to show deliberately.

#### Build Capsule

**What it does:** runs the full eight-step construction pipeline on the server:
ML-KEM encapsulation → HKDF key derivation → AES-256-GCM sealing → replay token
→ canonicalisation → SHA3-512 integrity lock → ML-DSA-65 signature.

**What to point at afterwards:** the **Current Capsule** panel underneath fills
in with real measurements — payload size, wire size, expansion ratio, the 1088-byte
KEM ciphertext, the 3309-byte signature, and the build time in milliseconds.

**Demo line:** *"A 2 KB payment became a 9.5 KB capsule. Most of that is the
1088-byte KEM ciphertext and the 3309-byte lattice signature — those are the exact
sizes NIST FIPS 203 and 204 specify. That overhead is fixed, so it disappears as
payloads get larger."*

#### Transmit & Settle

**What it does:** sends the capsule over real HTTPS to the settlement endpoint,
which runs the five-stage validation pipeline and, if every control passes,
decrypts the payload.

**What to point at:** the right-hand pipeline panel, and specifically the
**timings** — stages 1–3 cost single-digit microseconds, stage 4 around 60
microseconds, stage 5 around 17 milliseconds.

**Demo line:** *"Notice the ordering. The cheap checks run first. A replayed or
expired capsule is thrown out in about two microseconds and never touches the
expensive lattice verifier. Under a flood of junk traffic this node spends almost
nothing rejecting it."*

#### Route: Network Path

| Option | What happens |
| :--- | :--- |
| **Direct to settlement node (:8443)** | The browser talks straight to the settlement API |
| **Via interception proxy (:8444)** | The request is routed through the man-in-the-middle proxy first, which records it before forwarding |

**Why it exists:** it lets you settle a capsule *through a hostile hop* and show
that it still settles perfectly — the proxy could read the capsule and could not
understand it. Switch to proxy, settle, then go to Tab 04 and you will see the
flow you just sent sitting in the harvest archive.

### 3.2 Zero-Trust Validation Pipeline (right panel, top)

**What it is:** the five security controls every inbound capsule must clear,
shown with pass/fail status, the specific reason, and the measured time each
control took.

| Stage | Control | What it stops |
| :--- | :--- | :--- |
| 1 | Protocol Version | Malformed or wrong-version messages |
| 2 | Freshness Window | Stale capsules held and used later |
| 3 | Replay Token | The same valid capsule being submitted twice |
| 4 | Integrity Lock (SHA3-512) | Any modification to any field in transit |
| 5 | Origin Signature (ML-DSA-65) | Forgery — a capsule from someone who is not the claimed sender |

If a stage fails, the remaining stages show **SKIPPED**. That is deliberate: the
pipeline fails closed at the first objection, and the display shows you exactly
where it stopped rather than hiding it.

### 3.3 Decrypted Payload at Settlement Engine

**What it is:** the plaintext the settlement engine recovered — shown in green on
success, red with the rejection reason on failure.

**Why it matters:** it closes the loop. The payment went in as plaintext, became
ciphertext on the wire, and came back out identical at the other end. The header
shows the split between validation time and decryption time.

### 3.4 Network Console

**What the API logs are for.** This is the single most persuasive panel for a
sceptical evaluator, so it is worth understanding fully.

Each line is one real `fetch()` call the page made:

```
19:01:55.172  POST /api/v1/capsule/encapsulate  ->  200  37.6ms wire  34.4ms server
```

| Part | Meaning |
| :--- | :--- |
| `19:01:55.172` | Wall-clock timestamp, millisecond precision |
| `POST /api/v1/...` | The HTTP method and endpoint actually called |
| `200` | The real HTTP status code returned |
| `37.6ms wire` | Measured in the browser with `performance.now()` — total round trip |
| `34.4ms server` | Read from the `X-QSC-Process-Time-Ms` response header — how long the server spent computing |
| `INTERCEPTED` | Appears when the response came back through the MITM proxy |

**Why the two timings are shown separately:** the gap between them is network
overhead; the server figure is actual cryptographic work. When you see
`34.4ms server` on an encapsulate call, that is genuine lattice arithmetic, and it
is why the number varies between calls rather than being suspiciously constant.

Colour coding: blue for normal traffic, green for successful operations, amber
for warnings (a plaintext payment being sent), red for failures.

**Demo line:** *"Every line here is a real HTTPS request. If you open your
browser's developer tools, Network tab, you will see exactly the same requests.
Nothing is faked at this layer."*

The **Clear** button empties the console — useful before starting a fresh demo so
the audience sees only what you are about to do.

---

## 4. Tab 02 — Packet Inspector

**What this tab is for:** showing the raw bytes. Summaries can be fabricated; a
hex dump with byte offsets that you can interactively modify cannot.

**Prerequisite:** build a capsule on Tab 01 first.

### 4.1 Field legend (coloured chips)

**What it is:** one chip per capsule field, each showing the field name, a colour
and its exact size in bytes.

**What it does:** click a chip and every byte belonging to that field highlights
in the hex view, the view scrolls to it, and the byte offset is armed in the
attack lab below.

**Why it matters:** the offsets are computed **server-side** in
[`wire.py`](../src/capsule/wire.py) from the same canonical JSON that was hashed
and signed. So when you click `signature` and 4414 bytes light up, you are seeing
the true position of the real signature in the real transmitted message.

Chips worth pointing at:

- **`kem_ciphertext` — 1454 B encoded (1088 B raw).** The ML-KEM-768 encapsulation.
- **`signature` — 4414 B encoded (3309 B raw).** The ML-DSA-65 lattice signature.
  It is visibly the largest thing in the capsule; that is the honest cost of
  post-quantum security.
- **`payload_ciphertext`.** The actual payment. Point out that it is unreadable in
  the ASCII column while everything around it is legible JSON.

### 4.2 The hex view

**What it is:** a Wireshark-style dump — byte offset in hex, sixteen bytes per
row, ASCII interpretation on the right.

**What it does:** click any individual byte to select it. The Byte Selection panel
shows its offset, its owning field, its value in hex and binary, its character,
and a plain-English note about what that field is for.

**Why it matters:** an evaluator can scroll to the top and read
`{"capsule_id":"qsc_...` in the ASCII column, then scroll into the ciphertext
region and see it turn to noise. That transition is the encryption, visible.

### 4.3 Attack Lab — Single Bit Flip

This is the most convincing security demonstration in the whole workbench.

| Control | What it does |
| :--- | :--- |
| **Byte Offset** | Which byte to modify. Auto-filled when you click a field chip or a byte |
| **Bit Index (0–7)** | Which single bit within that byte to flip |
| **Flip Bit & Resubmit** | Modifies exactly one bit and re-submits the capsule for settlement |
| **Replay Capsule Verbatim** | Re-sends an already-settled capsule unchanged, as an attacker replaying a captured message |

**Why one bit:** it is the smallest change an active attacker can possibly make.
If the system catches a single bit, it catches everything larger. This forecloses
the objection *"sure, but would it catch a subtle change?"*

**The three flips worth demonstrating, in order:**

1. **Click `payload_ciphertext`, then Flip Bit.**
   → Rejected at **stage 4, Integrity Lock**. The SHA3-512 digest no longer matches.

2. **Click `signature`, then Flip Bit.**
   → Rejected at **stage 5, Origin Signature** — and note it *passed* stage 4.
   This is not a bug; it is the design. The signature is deliberately excluded
   from the integrity hash (it cannot sign itself), so a different control has to
   catch it. Two controls, different coverage, no gap between them.

3. **Press Replay Capsule Verbatim on a settled capsule.**
   → Rejected at **stage 3, Replay Token**, in about two microseconds, with stages
   4 and 5 marked SKIPPED. Nothing was modified — the message is byte-identical
   and still refused.

**Demo line:** *"I changed one bit out of seventy-six thousand. Watch which
control catches it, and notice the signature flip gets past the hash check and is
stopped by the lattice verification instead. The two controls cover different
ground on purpose."*

---

## 5. Tab 03 — 3D Visualizer

**What this tab is for:** explaining *why* message-level security matters to
someone who will not read a hex dump. It is the conceptual argument, animated.

**The scene:** a payment crossing five nodes —
Originating Bank → Edge Gateway → Reverse Proxy → Message Broker → Clearing House
— with a Quantum Eavesdropper circling above. Drag to orbit, scroll to zoom.

### 5.1 The two modes

| Button | What it represents |
| :--- | :--- |
| **Mode A — TLS 1.3** | How essentially every production banking API works today: plaintext inside a TLS tunnel |
| **Mode B — QSC Capsule** | The payment sealed in a post-quantum capsule before it enters the network |

The point of having both is direct comparison. Same network, same hops, same
attack — only the protection model differs.

### 5.2 Run Full Process

**What it does:** plays the complete journey as a timed sequence, roughly 22
seconds, with the **Narration** panel on the right explaining each phase as it
happens.

The six phases:

| Phase | Mode A (TLS) | Mode B (QSC) |
| :--- | :--- | :--- |
| **1. Key Generation** | Amber ECDHE P-256 key glyphs appear at both ends. Narration explains this rests on the discrete logarithm problem — exactly what Shor breaks | Violet ML-DSA signing key and green ML-KEM encapsulation key appear. Narration gives the exact key sizes |
| **2. Encapsulation** | Payment is serialised as plaintext JSON. Narration: *no message-level protection at all* | The five sealing operations are listed in order with their real sizes |
| **3. Wire Transit** | Payment moves to the Edge Gateway, leaving a trail | Same, but the narration notes the tunnel is no longer load-bearing |
| **4. Proxy Hop** | **The tunnel segment disappears and the payload turns red.** TLS terminated; the payment is plaintext in proxy memory | The tunnel terminates identically — and the capsule stays green and sealed |
| **5. Message Broker** | Narration: the plaintext payment is now written to a Kafka log on disk | Narration: what lands on disk is the capsule — encryption at rest for free |
| **6. Settlement** | Narration: the engine trusts the payment because TLS delivered it. No signature, no integrity check | The five validation stages are listed with their real costs |

**Demo line for phase 4:** *"This is the moment that matters. The proxy has to
decrypt TLS to route the message — that is its job, not an attack. In Mode A the
payment is now sitting in plaintext in that machine's memory. In Mode B the proxy
does exactly the same thing and finds a capsule it cannot open."*

### 5.3 Run Quantum Attack

**What it does:** plays the harvest-now-decrypt-later timeline in four phases.

| Phase | What you see | What it means |
| :--- | :--- | :--- |
| **1. Harvest** | Red copies of the message peel off the wire and fly to the eavesdropper | Passive recording. Nothing is altered, nothing detectable |
| **2. The Archive Waits** | The scene holds | Years pass. This is why the threat is urgent *now* — the ciphertext is already out of your control |
| **3. Shor's Algorithm** | A shockwave expands, beams fire, **every tunnel segment vanishes** | Archived ECDHE session keys recovered. The tunnel is gone retroactively |
| **4. Result** | **Mode A:** payload turns red — *"RECOVERED by the adversary"*. **Mode B:** capsule stays green and pulses — *"attack deflected"* | The whole argument, in one frame |

**Why the tunnel disappears in both modes:** this is the honest part. QSC does
not save TLS. TLS falls either way. The difference is what is left underneath.

**Demo line:** *"Run it in Mode A, then switch to Mode B and run it again. The
tunnel collapses identically both times — I am not strawmanning TLS. The
difference is that in Mode B there is a second layer underneath, and Shor's
algorithm has nothing to say about lattice problems."*

### 5.4 The other controls

| Control | What it does |
| :--- | :--- |
| **Timeline (bottom)** | Click any of the five steps to jump straight to it — useful when an audience asks to see the proxy hop again |
| **Reset** | Clears the scene and the narration back to the start |
| **Clear** (narration panel) | Empties the narration log without resetting the scene |
| **Scene HUD** (top left) | Current mode, current phase, and the payload's protection state |
| **Lattice Parameters** (top right) | The actual ML-KEM-768 parameters: ring, modulus q = 3329, module rank k = 3 |
| **Status** (bottom left) | One-line summary of what is happening right now |

---

## 6. Tab 04 — Interception Lab

**What this tab is for:** proving the claim with real captured network traffic
rather than an animation. If the 3D tab is the argument, this is the evidence.

**Requires the proxy to be running** — that is, started without `--no-proxy`.

### 6.1 What is real here, and what is not

Say this explicitly during a demo; it earns credibility rather than costing it.

| Element | Status |
| :--- | :--- |
| The network hops, the TLS termination, the captured bytes | **Real.** The proxy genuinely terminates TLS and records what it relays |
| Shor's algorithm having broken the archived sessions | **Modelled.** This is the 2030s threat applied to genuinely captured bytes |

The proxy is not an exotic attack. It occupies the same position as an API
gateway, a service mesh sidecar, a WAF, a CDN edge or a corporate TLS inspection
appliance. Every one of those sees exactly what this proxy sees.

### 6.2 The controls

| Button | What it does | Why it is there |
| :--- | :--- | :--- |
| **Message Standard** | Chooses the payload type. **Card Authorisation** is the strongest choice for a demo | Leaked PAN and CVV are instantly understandable to any audience |
| **Send Payment via TLS Only** | Generates a payment and POSTs it as plaintext through the proxy | The control group — how banking APIs work today |
| **Send Payment as Capsule** | Generates a payment, encapsulates it, and sends the capsule through the same proxy | The treatment group — same payment, same route, different protection |
| **Break Archived TLS Sessions** | Applies the quantum threat model to everything harvested so far | The reveal |
| **Clear Harvest Archive** | Empties the capture store | Reset between demos |

**Send both, using the same message standard.** The comparison only lands if the
two flows carry equivalent data.

### 6.3 Harvested Flows table

Each row is one real request the proxy relayed:

| Column | Meaning |
| :--- | :--- |
| **Capture** | Sequential capture ID |
| **Method / Path** | The real HTTP method and endpoint |
| **Req** | Request body size in bytes, as recorded off the wire |
| **RTT** | Measured round-trip time through the proxy to the upstream node |
| **Protection** | `TLS_ONLY` (red) or `QSC_CAPSULE` (green) — the proxy's own classification of what it captured |

### 6.4 Post-Quantum Forensics

After pressing **Break Archived TLS Sessions**, the panel splits into two verdicts.

**BREACHED** — the TLS-only flow:
- Lists the sensitive fields recovered in the clear: `amount, cardholder, cvv, pan`
- Shows the **full recovered payment** in red, including the card number

**RESISTED** — the capsule flow:
- Shows the routing metadata that *is* visible: `BARCGB22XXX → HDFCINBBXXX`
- Lists what remains opaque and its size: 1088 B KEM ciphertext, the AES-GCM
  payload, the 16 B tag, the 12 B nonce
- States plainly that Shor's algorithm does not apply, and why

**Be honest about the metadata.** The sender, recipient, capsule ID and timestamps
*are* visible to the interceptor. That is deliberate — intermediaries need to
route the message. If an evaluator raises it, agree: QSC protects the payment, not
the fact that a payment occurred. Traffic analysis is a separate problem with
separate solutions.

**Demo line:** *"Same payment, same wire, same proxy, thirty seconds apart. One
of them just handed an adversary a live card number. The other handed them 1088
bytes of lattice ciphertext."*

---

## 7. Tab 05 — Cryptography

**What this tab is for:** the reference panel. When someone asks *"what exactly
are you running?"*, this answers it without opening an editor.

### 7.1 Post-Quantum Parameter Sets (left)

Reports the live parameters for every primitive in the stack:

| Block | Notable values |
| :--- | :--- |
| **ML-KEM-768** (FIPS 203) | Module-LWE hardness, n = 256, q = 3329, k = 3, NIST category 3, and the exact key/ciphertext sizes |
| **ML-DSA-65** (FIPS 204) | Module-LWE and Module-SIS, q = 8380417, matrix (6, 5), 3309-byte signatures |
| **AES-256-GCM** (SP 800-38D) | 256-bit key, 96-bit nonce, 128-bit tag |
| **SHA3-512** (FIPS 202) | Keccak-f[1600] sponge, 512-bit digest |
| **HKDF-SHA3-512** (SP 800-56C Rev. 2) | Derives the AES content key from the ML-KEM shared secret |

**Why the KDF row matters:** NIST requires that a shared secret from a key
establishment scheme be run through an approved KDF before use as a working key.
The raw ML-KEM output is never used directly as the AES key. Pointing this out
signals the implementation follows the standards properly rather than just
name-dropping them.

### 7.2 Live TLS Session (right)

**What it is:** the result of the server opening a genuine TLS connection to
itself over loopback and reporting what was negotiated.

| Field | Why it is interesting |
| :--- | :--- |
| **Protocol / Cipher suite** | `TLSv1.3` / `TLS_AES_256_GCM_SHA384`, read from the live OpenSSL session |
| **Certificate verified: yes** | Verification is genuinely on. The probe validates the chain and hostname — it is not skipping checks to succeed |
| **Subject CN, Organisation, SANs, Valid until** | The real certificate contents |
| **TCP connect / TLS handshake (ms)** | Separately measured — connection setup vs handshake cost |
| **Handshake sequence** | ClientHello → ServerHello → EncryptedExtensions → Certificate → CertificateVerify → Finished |
| **Quantum exposure of this channel** | States plainly that this channel's ECDHE key exchange and ECDSA certificate are broken by Shor's algorithm |

That last block is the key one. **The transport layer of this very platform is
quantum-vulnerable, and the platform says so about itself.** That is the argument
in miniature: the tunnel is not the thing you should be relying on.

**Re-probe Handshake** runs the probe again — useful to show the timings change
because it is a fresh connection each time.

---

## 8. Command-Line Demonstrations

Scripts matter because a terminal is harder to fake than a web page, and some
audiences trust it more.

### 8.1 `hndl_demo.py` — the headline demo

```bash
python src/demo/hndl_demo.py        # requires the node to be running
```

**What it does:** the Interception Lab comparison, driven from a real HTTPS
client outside the browser. One payment, sent twice — once as plaintext, once as
a capsule — both through the interception proxy, then the quantum threat model
applied to the captures.

**Why it exists:** it proves the workbench is a *view* onto a real API, not the
system itself. The same result arrives through `requests` with certificate
verification enabled.

**What to point at:** the `[ BREACHED ]` block showing the recovered PAN and CVV,
immediately followed by `[ RESISTED ]` showing only ciphertext sizes.

### 8.2 `banking_transfer.py`

```bash
python src/demo/banking_transfer.py
```

**What it does:** a self-contained end-to-end interbank wire transfer — build,
transmit, validate, decrypt.

**Why it exists:** the simplest possible complete story, with no server and no
browser. Good opening demo.

### 8.3 `replay_attack_demo.py`

```bash
python src/demo/replay_attack_demo.py
```

**What it does:** runs four scenarios in sequence — a legitimate transmission,
then a replay, then a tampered ciphertext, then a forged signature from a rogue
key. The first succeeds; the other three are rejected, each with the specific
reason.

**Why it exists:** the threat model, demonstrated rather than described. Note
that these rejections now come from genuine ML-DSA lattice verification.

### 8.4 `tls_qsc_demo.py`

```bash
python src/demo/tls_qsc_demo.py
```

**What it does:** opens a raw TLS 1.3 socket on port 9443, performs a real
handshake, and pushes a capsule through it — reporting the negotiated cipher.

**Why it exists:** shows the capsule is transport-agnostic. No FastAPI, no HTTP —
just bytes over a socket.

### 8.5 `file_encrypt_demo.py`

```bash
python src/demo/file_encrypt_demo.py
```

**What it does:** encrypts a sensitive document into a portable `.qsc` container
on disk and decrypts it back, verifying the content is byte-identical.

**Why it exists:** demonstrates **data at rest**, not just in transit. A capsule
on a USB stick has the same protection as one on a wire. This is the answer to
*"what about backups and archives?"*

### 8.6 `benchmark.py`

```bash
python src/demo/benchmark.py --iterations 100
```

**What it does:** times every primitive and the full lifecycle, reporting median,
mean, p95 and operations per second, plus the size overhead breakdown.

**Why it exists:** so performance claims are measured rather than asserted. It
also surfaces an honest weakness — ML-DSA signing is slow in pure Python because
of FIPS 204's rejection-sampling loop. Raising that yourself is far better than
having an evaluator find it. The fix is a native backend, and the wrapper classes
are structured to allow it.

---

## 9. The Test Suite

```bash
pytest tests/ -v          # all 69 tests
pytest tests/test_pqc_crypto.py -v          # just the primitives
```

| Suite | What it proves |
| :--- | :--- |
| `test_pqc_crypto.py` | Key sizes match FIPS 203/204 exactly; encapsulation round-trips; the wrong private key yields the wrong secret; tampered ciphertext triggers FIPS 203 implicit rejection; forged, wrong-key, bit-flipped and truncated signatures all fail; HKDF separates keys by capsule ID |
| `test_tls_handshake.py` | A real server negotiates TLS 1.3; the certificate chain genuinely validates; **a client that does not know our CA is correctly refused** — proving verification is not being skipped |
| `test_mitm_resistance.py` | Searches the raw capsule bytes for the actual PAN, CVV and cardholder and confirms none appear; bit flips are caught at the correct stage; replays are stopped at stage 3 with later stages skipped |
| `test_settlement_api.py` | Every endpoint; that the byte offsets driving the hex inspector are exact; that generated payloads differ between calls |
| `test_builder.py`, `test_validator.py`, `test_replay_protection.py` | Core capsule lifecycle |
| `test_api_endpoints.py` | The earlier standalone visualizer |

**Demo line:** *"One of these tests takes the finished capsule bytes and greps
them for the actual card number that went in. If message-level encryption were
not really happening, that test would fail."*

---

## 10. API Reference

All endpoints are live at `https://127.0.0.1:8443`, with interactive
documentation at `/api/docs`.

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Liveness and uptime |
| `GET` | `/api/v1/pqc/parameters` | NIST parameter sets for every primitive |
| `POST` | `/api/v1/pqc/keys/generate` | Rotate the keyset; returns sizes, fingerprints and timings |
| `GET` | `/api/v1/payloads` | List the supported message standards |
| `POST` | `/api/v1/payloads/generate?kind=` | Generate a fresh wire message |
| `POST` | `/api/v1/capsule/encapsulate` | Build a capsule; returns it with wire format and byte offsets |
| `POST` | `/api/v1/capsule/settle` | Validate and settle a capsule; returns the five-stage trace |
| `GET` | `/api/v1/capsule/{id}/hexdump` | Hex-dump rows for a capsule |
| `POST` | `/api/v1/attack/tamper` | Flip one bit and resubmit |
| `POST` | `/api/v1/attack/replay` | Resubmit a capsule verbatim |
| `POST` | `/api/v1/legacy/transfer` | Send a payment with TLS-only protection (the control group) |
| `GET` | `/api/v1/network/telemetry` | Live counters |
| `GET` | `/api/v1/network/tls` | Live TLS handshake probe |

Interception proxy, at `https://127.0.0.1:8444`:

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/_intercept/captures` | Everything harvested so far |
| `DELETE` | `/_intercept/captures` | Clear the archive |
| `POST` | `/_intercept/quantum-decrypt` | Apply the quantum threat model to the captures |
| `*` | `/{any path}` | Relays to the settlement node, recording both directions |

**Proving it from outside the browser:**

```bash
curl --cacert certs/cert.pem https://127.0.0.1:8443/api/v1/health
```

This is worth doing live. It answers *"is the browser page just faking it?"* in
one command.

---

## 11. Suggested Demo Running Orders

### Five minutes (technical audience)

1. `python -m src.server.run`, open the workbench — point at the live masthead.
2. **Tab 01:** Build Capsule → Transmit & Settle. Point at the five stages and the
   microsecond-to-millisecond spread.
3. **Tab 02:** click `payload_ciphertext`, Flip Bit → rejected at stage 4. Then
   click `signature`, Flip Bit → rejected at stage 5, and explain why the two
   controls differ.
4. **Tab 04:** send both payment types, Break Archived TLS Sessions, show the PAN
   next to the ciphertext.
5. Close on **Tab 05**, quantum exposure block: *"this platform's own transport is
   quantum-vulnerable, and it says so."*

### Ten minutes (mixed audience)

Insert **Tab 03** after step 2: Mode A → Run Full Process → Run Quantum Attack,
then Mode B and repeat. The narration panel carries the explanation, so you can
let it run and talk over it.

### Two minutes (non-technical)

**Tab 03 only.** Mode A, Run Full Process, Run Quantum Attack. Then Mode B, same
two buttons. The contrast in the final frame — red *"RECOVERED by the adversary"*
versus green *"attack deflected"* — is the entire pitch and needs no vocabulary.

### If asked "is any of this hardcoded?"

1. Build two capsules in a row on Tab 01 — the payloads differ, the corridors
   differ, the timings differ.
2. Run the `curl` command above in a terminal — same API, outside the browser.
3. Open browser developer tools, Network tab, and click Build Capsule.
4. Run `pytest tests/test_mitm_resistance.py -v` — the test that greps the capsule
   bytes for the card number.
