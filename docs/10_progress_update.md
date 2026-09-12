# Project Progress Update

**Project:** Quantum Security Capsule (QSC)
**Prepared for:** Project Guide
**Date:** September 2026
**Status:** Working prototype complete and demonstrable

---

## 1. What the project is, in one paragraph

When a bank sends a payment over the internet, the data is protected by
something called **TLS** — the same technology behind the padlock icon in a web
browser. TLS protects the *connection* between two computers. Our project takes
a different approach: instead of protecting the connection, we protect **the
message itself**. Each payment is sealed inside its own secure container — we
call it a **capsule** — which stays locked no matter how many computers it
passes through on its journey.

---

## 2. The problem we are solving

There are two problems with the way things work today. Both are easiest to
explain with the same picture.

> **Think of TLS as an armoured tunnel between two buildings.** The payment walks
> through the tunnel and is safe while inside it.

### Problem one: the tunnel has gaps

A payment does not travel from the sending bank to the receiving bank in one
hop. On the way it passes through four or five other computers — security
gateways, routers, message queues. **The tunnel ends and restarts at every one
of them.** At each of those points, the payment briefly steps out of the tunnel
and sits there in readable form.

This is not a flaw anyone introduced by mistake. Those middle computers need to
read the address on the message in order to route it — so the tunnel has to open.
But today, when the tunnel opens, *everything* is readable: the amount, the
account numbers, the names.

### Problem two: "Harvest Now, Decrypt Later"

This is the more serious one.

The locks TLS uses are extremely strong against today's computers. They are
**not** strong against a **quantum computer**, a new kind of machine that experts
expect to become practical sometime in the 2030s. A known method called **Shor's
algorithm** will break these locks quickly.

Here is why that matters today rather than in ten years:

> An attacker does not need to break the lock now. They can simply **record the
> encrypted traffic today and store it**, then unlock it all later when the
> technology arrives.

So a payment sent this morning, with a confidentiality requirement of twenty
years — a mortgage, a bond, a corporate account — **is already at risk**, because
a copy of it may already be sitting in someone else's storage waiting.

### What our approach does

> **QSC puts a locked safe inside the tunnel.** The middle computers can still
> read the address on the outside of the safe and route it correctly. But they
> cannot open it. And crucially, **the safe's lock is of a new type that quantum
> computers cannot pick** — so even if the tunnel is broken open years later, the
> safe inside is still shut.

---

## 3. Where the project currently stands

**The prototype is complete and fully working.** It is not a slide deck or a
mock-up — it is a running system that can be demonstrated live on a laptop in
about two minutes.

### What has been built

| Part | What it does | Status |
| :--- | :--- | :--- |
| **The security engine** | Seals and unseals payments using the new quantum-resistant methods | Complete |
| **A live server** | Runs as a real network service that other programs can talk to | Complete |
| **A web dashboard** | Five screens showing the whole system working, in a browser | Complete |
| **A 3D animation** | Explains the idea visually, for non-technical viewers | Complete |
| **An attack simulator** | Lets anyone attack the system live and watch it defend itself | Complete |
| **Automated testing** | 69 tests that verify the security actually works | All passing |
| **Documentation** | Ten documents covering design, security, performance and operation | Complete |

### The single most important improvement this phase

The earlier version of the project had a significant weakness: the
quantum-resistant encryption was **imitated rather than real**. The code produced
outputs of the right size and shape, but it was not actually performing the
mathematics. Any expert examining it closely would have found this immediately.

**This has now been fixed.** The project uses genuine, standards-compliant
implementations of the two methods the US National Institute of Standards and
Technology (NIST) officially approved in 2024:

- **ML-KEM-768** — for securely agreeing on a secret key
- **ML-DSA-65** — for digitally signing messages so the recipient knows who sent them

These libraries have been independently checked against NIST's official test
data. This means the project can now honestly claim to implement the real
standards, which is the difference between a demonstration and a toy.

---

## 4. What can be shown right now

Anyone can sit in front of the laptop and do all of the following:

1. **Create a real payment** in the actual format banks use (ISO 20022 or SWIFT),
   seal it, and send it over a real encrypted network connection. Every payment
   generated is different, so it cannot be dismissed as a fixed canned example.

2. **Watch the security checks run.** The receiving end performs five separate
   checks before accepting anything. The screen shows each check passing or
   failing, with the exact time it took.

3. **Attack the system.** Change a *single bit* — the smallest possible change to
   a computer file — anywhere in the sealed message, and watch the system detect
   it and refuse the payment. Or try sending the same valid payment twice; the
   second one is rejected as a duplicate.

4. **See the raw data.** A panel shows the actual bytes travelling over the
   network. You can see the readable parts (addressing information) and the
   unreadable parts (the payment itself).

5. **Run the key comparison.** Send the same card payment twice — once the
   ordinary way, once sealed in a capsule — through a computer that is
   eavesdropping. Then simulate the arrival of quantum computers. The ordinary
   payment reveals the full card number and security code. The sealed one reveals
   nothing but the address on the outside.

6. **Watch the 3D explanation**, which walks through the whole journey with
   written commentary appearing alongside it, explaining each step as it happens.

---

## 5. Being honest about what is real and what is simulated

This distinction is stated openly on the dashboard itself, because claiming more
than we have built would be the fastest way to lose credibility with an examiner.

**Genuinely real:**
- The quantum-resistant encryption (the actual approved standards)
- The encrypted network connections
- The eavesdropping computer and everything it records
- The payment message formats
- All performance measurements

**Simulated:**
- **One thing only:** the assumption that a quantum computer exists and has
  broken the recorded traffic. Quantum computers of the required capability do
  not exist yet, so this part is necessarily a projection of the expected future
  threat. It is clearly labelled as such everywhere it appears.

Everything the simulation is applied *to* is genuinely captured data.

---

## 6. Known limitation, and why it is acceptable

The quantum-resistant encryption libraries we use are written in pure Python.
They were chosen because they are readable and independently verified, which
matters for a project that needs to be inspected and trusted.

The trade-off is speed: they are considerably slower than commercial versions
written in C. Signing a message takes roughly 75 milliseconds in our system,
where an optimised commercial implementation would take under 1 millisecond.

**Why this is acceptable:** it is a property of the library we chose, not of the
method itself or of our design. The code is deliberately structured so that a
faster commercial engine can be substituted without changing anything else in the
project. We have documented this openly with measured figures rather than leaving
it to be discovered.

---

## 7. Summary of the current position

| Question | Answer |
| :--- | :--- |
| Is the concept proven? | Yes — working end to end |
| Is the cryptography real? | Yes — official NIST standards, independently verified libraries |
| Can it be demonstrated live? | Yes — roughly two minutes for the short version |
| Is it tested? | Yes — 69 automated tests, all passing |
| Is it documented? | Yes — ten documents, including a full operating guide |
| Is it production-ready? | No, and it is not intended to be. It is a working proof of concept |

---

## 8. Possible next steps

If the project continues beyond this stage, the natural directions are:

1. **Substitute a faster encryption engine** to bring performance to production
   levels. This is a contained change and the system is already designed for it.

2. **Reduce the size overhead.** A sealed payment is currently about 7 KB larger
   than an unsealed one. Roughly a third of that is avoidable by changing how the
   data is packaged.

3. **Add key management.** At present, keys are generated when the server starts.
   A real deployment would store them in dedicated security hardware.

4. **Pilot on one real message route** rather than the whole network, since the
   design is intended to be adopted gradually alongside existing systems rather
   than replacing them.

---

## 9. To see it running

```
python -m src.server.run
```

Then open `https://127.0.0.1:8443` in a browser and accept the security warning
(the certificate is one the project generates itself, which browsers correctly
flag as unfamiliar).

To stop it, press **Ctrl + C** in the terminal.

A full step-by-step guide to every screen and button is in
[docs/09_feature_guide.md](09_feature_guide.md).
