/* ==========================================================================
   visualizer_3d.js - channel security vs message security, in three dimensions.

   The scene models one payment crossing an untrusted network:

     Originating Bank -> Edge Gateway -> Reverse Proxy -> Broker -> Clearing House

   Two things can be played against that network:

     Run Full Process   walks the payment through key generation, encapsulation,
                        transit, the proxy hop where TLS terminates, and
                        settlement - narrating each phase as it happens.

     Quantum Attack     plays the harvest-now-decrypt-later timeline: the
                        eavesdropper records the link, years pass, and Shor's
                        algorithm recovers the session keys.

   Mode A protects the payload with the TLS tunnel alone. Mode B seals it in a
   lattice capsule first. Running both sequences in each mode is the whole
   argument of the project, shown rather than asserted.

   Rendering uses the vendored three.js r128 build, so the tab works offline.
   ========================================================================== */

const Visualizer3D = (() => {

  const COLOURS = {
    bg:        0x06080b,
    grid:      0x161b24,
    node:      0x1f2937,
    nodeEdge:  0x3b82f6,
    target:    0x10b981,
    hop:       0x475569,
    tunnel:    0x3b82f6,
    plaintext: 0xf59e0b,
    exposed:   0xef4444,
    capsule:   0x10b981,
    lattice:   0x34d399,
    threat:    0xef4444,
    signing:   0x8b5cf6,
  };

  const HOPS = [
    { x: -13, label: 'Originating Bank' },
    { x:  -6, label: 'Edge Gateway' },
    { x:   0, label: 'Reverse Proxy' },
    { x:   6, label: 'Message Broker' },
    { x:  13, label: 'Clearing House' },
  ];

  /* Where along the corridor the payload sits at each timeline step. */
  const STEP_POSITIONS = [0, 0.10, 0.28, 0.5, 0.92];

  const STEP_TEXT = [
    'Key generation. ML-KEM-768 and ML-DSA-65 keypairs are established at both ends.',
    'Encapsulation. The payload is sealed before it touches the wire.',
    'Wire transit. The message crosses hops nobody controls end to end.',
    'Proxy hop. TLS terminates here - this is where channel security ends.',
    'Settlement. The receiver validates five controls before releasing plaintext.',
  ];

  /* ----------------------------------------------------------------------
     Phase scripts. Each phase drives the scene and writes one narration
     entry, worded differently per mode because the two modes genuinely
     behave differently at that point in the journey.
     ---------------------------------------------------------------------- */

  const RUN_PHASES = [
    { id: 'keygen',  timeline: 0, target: 0.00, duration: 4200, node: 0 },
    { id: 'encap',   timeline: 1, target: 0.10, duration: 4200, node: 0 },
    { id: 'transit', timeline: 2, target: 0.28, duration: 3000, node: 1 },
    { id: 'proxy',   timeline: 3, target: 0.50, duration: 4200, node: 2 },
    { id: 'onward',  timeline: 3, target: 0.76, duration: 2800, node: 3 },
    { id: 'settle',  timeline: 4, target: 0.92, duration: 4000, node: 4 },
  ];

  const RUN_SCRIPT = {
    keygen: {
      tls: {
        title: '1. Key Generation',
        tone: 'step',
        body: 'The two ends perform an <b>ECDHE key exchange over NIST P-256</b>. ' +
              'Both sides derive the same session key without it ever crossing the wire, ' +
              'and the server proves its identity with an <b>ECDSA P-256</b> certificate. ' +
              'This is genuinely strong cryptography today. Its weakness is what it rests on: ' +
              'the <b>elliptic-curve discrete logarithm problem</b>, which is exactly what ' +
              "Shor's algorithm solves.",
        tag: 'TLS 1.3 handshake',
      },
      qsc: {
        title: '1. Key Generation',
        tone: 'good',
        body: 'The <b>Clearing House</b> generates an ML-KEM-768 keypair: a 1184-byte public ' +
              'encapsulation key and a 2400-byte private key. The <b>Originating Bank</b> ' +
              'generates an ML-DSA-65 signing keypair: 1952 bytes public, 4032 private. ' +
              'Only the public keys are exchanged. Both private keys stay inside their own ' +
              'node and never touch the network.',
        tag: 'FIPS 203 + FIPS 204',
      },
    },
    encap: {
      tls: {
        title: '2. Serialisation',
        tone: 'warn',
        body: 'The payment is serialised as <b>plaintext JSON</b> and handed straight to the ' +
              'TLS layer. There is no message-level protection applied at all &mdash; from ' +
              'this point on, the only thing standing between the account numbers and an ' +
              'observer is the tunnel.',
        tag: 'no message-layer protection',
      },
      qsc: {
        title: '2. Encapsulation',
        tone: 'good',
        body: 'Five operations, in order:<br>' +
              '<b>1.</b> ML-KEM-768 encapsulation against the receiver public key produces a ' +
              '32-byte shared secret and a 1088-byte ciphertext.<br>' +
              '<b>2.</b> <code>HKDF-SHA3-512</code> derives the AES key from that secret, ' +
              'salted with the capsule id.<br>' +
              '<b>3.</b> AES-256-GCM seals the payload and produces a 128-bit tag.<br>' +
              '<b>4.</b> SHA3-512 locks every field into one digest.<br>' +
              '<b>5.</b> ML-DSA-65 signs that digest &mdash; 3309 bytes of lattice signature.<br>' +
              'The payment is now armoured <b>before</b> it reaches the wire.',
        tag: 'sealed at the message layer',
      },
    },
    transit: {
      tls: {
        title: '3. Wire Transit',
        tone: 'step',
        body: 'The message reaches the <b>Edge Gateway</b> &mdash; a CDN point of presence, ' +
              'not equipment the bank owns. The tunnel is intact here, so the payload is ' +
              'protected in flight. Note what that protection depends on: the gateway ' +
              'behaving, and the session key staying secret forever.',
        tag: 'hop 1 of 3',
      },
      qsc: {
        title: '3. Wire Transit',
        tone: 'step',
        body: 'The capsule reaches the <b>Edge Gateway</b>. The TLS tunnel still wraps it, ' +
              'which is fine &mdash; defence in depth. But the tunnel is no longer doing the ' +
              'load-bearing work. Strip it away at any point and the payment is still sealed.',
        tag: 'hop 1 of 3',
      },
    },
    proxy: {
      tls: {
        title: '4. Proxy Hop  &mdash;  TLS TERMINATES',
        tone: 'bad',
        body: 'This is the moment that matters. The <b>Reverse Proxy</b> terminates TLS to ' +
              'inspect, route and re-encrypt. To do that it must decrypt &mdash; so the ' +
              'payment now exists as <b>plaintext in this process&rsquo;s memory</b>.<br><br>' +
              'Anyone with access to that host reads the full payment: an operator, a ' +
              'compromised sidecar, a memory dump, a lawful intercept order. This is not an ' +
              'attack. It is how the infrastructure is designed to work.',
        tag: 'payload exposed at the hop',
      },
      qsc: {
        title: '4. Proxy Hop  &mdash;  TLS TERMINATES',
        tone: 'good',
        body: 'The same proxy terminates TLS in exactly the same way. It decrypts the tunnel ' +
              'and finds&hellip; a capsule it cannot open. It reads the routing metadata it ' +
              'genuinely needs &mdash; <b>sender, recipient, capsule id, expiry</b> &mdash; ' +
              'forwards the message, and never sees the amount, the IBANs or the counterparties.<br><br>' +
              'The proxy still does its job. It just cannot read the payment.',
        tag: 'metadata visible, payload sealed',
      },
    },
    onward: {
      tls: {
        title: '5. Message Broker',
        tone: 'warn',
        body: 'The <b>Message Broker</b> (Kafka, MQ) persists the message to disk for ' +
              'durability and replay. In this mode that means the plaintext payment is now ' +
              'written to a log file, retained for however long the topic policy says &mdash; ' +
              'often days or weeks.',
        tag: 'plaintext at rest',
      },
      qsc: {
        title: '5. Message Broker',
        tone: 'good',
        body: 'The broker persists the message to disk as usual. What lands in the log is ' +
              'the <b>capsule</b>, not the payment. Encryption at rest comes for free, ' +
              'because the message was never decrypted in the first place.',
        tag: 'ciphertext at rest',
      },
    },
    settle: {
      tls: {
        title: '6. Settlement',
        tone: 'warn',
        body: 'The settlement engine receives plaintext and <b>trusts it because TLS ' +
              'delivered it</b>. There is no signature to check, no integrity digest, no ' +
              'replay token. If the proxy had altered a single digit of the amount, nothing ' +
              'downstream would notice.',
        tag: 'implicit trust in the channel',
      },
      qsc: {
        title: '6. Settlement',
        tone: 'good',
        body: 'Five controls run in order, cheapest first:<br>' +
              '<b>1.</b> Protocol version &mdash; ~1&micro;s<br>' +
              '<b>2.</b> Freshness window &mdash; ~7&micro;s<br>' +
              '<b>3.</b> Replay token, single use &mdash; ~2&micro;s<br>' +
              '<b>4.</b> SHA3-512 integrity lock &mdash; ~60&micro;s<br>' +
              '<b>5.</b> ML-DSA-65 signature &mdash; ~17ms<br>' +
              'Only after all five pass is the replay token consumed and the payload ' +
              'decrypted. The ordering is deliberate: junk traffic is rejected in ' +
              'microseconds and never reaches the expensive verifier.',
        tag: 'zero-trust pipeline',
      },
    },
  };

  const ATTACK_PHASES = [
    { id: 'harvest', duration: 4200 },
    { id: 'archive', duration: 3400 },
    { id: 'shor',    duration: 3800 },
    { id: 'verdict', duration: 1000 },
  ];

  const ATTACK_SCRIPT = {
    harvest: {
      both: {
        title: 'Attack 1. Harvest',
        tone: 'warn',
        body: 'The eavesdropper sits on the link and <b>copies every frame to storage</b>. ' +
              'It cannot read any of it today &mdash; the TLS encryption holds. It does not ' +
              'need to. Storage is cheap and the adversary is patient.<br><br>' +
              'This is a <b>passive</b> attack. Nothing is altered, no alarm fires, and ' +
              'neither endpoint can detect it.',
        tag: 'passive recording, undetectable',
      },
    },
    archive: {
      both: {
        title: 'Attack 2. The Archive Waits',
        tone: 'note',
        body: 'Years pass. The recording sits in an archive.<br><br>' +
              'This is why the threat is urgent <b>now</b> rather than when quantum ' +
              'computers arrive. A payment sent today with a 25-year confidentiality ' +
              'requirement &mdash; a mortgage, a bond, a corporate treasury position &mdash; ' +
              'is already at risk, because the ciphertext is already in someone else&rsquo;s ' +
              'possession.',
        tag: 'harvest now, decrypt later',
      },
    },
    shor: {
      both: {
        title: 'Attack 3. Shor&rsquo;s Algorithm',
        tone: 'bad',
        body: 'A cryptographically relevant quantum computer runs <b>Shor&rsquo;s algorithm</b> ' +
              'against the archived ECDHE handshakes. Elliptic-curve discrete logarithms are a ' +
              'hidden subgroup problem over an abelian group, which is precisely the structure ' +
              'Shor exploits.<br><br>' +
              'Every recorded session key is recovered. <b>The tunnel is gone</b> &mdash; not ' +
              'just for future traffic, but retroactively, for everything ever recorded.',
        tag: 'TLS layer stripped',
      },
    },
    verdict: {
      tls: {
        title: 'Result: Total Compromise',
        tone: 'bad',
        body: 'With the tunnel stripped, the plaintext underneath is simply readable. ' +
              '<b>Account numbers, counterparties, amounts, BICs</b> &mdash; every payment ' +
              'ever carried on this link, going back years.<br><br>' +
              'The payload had no protection of its own. It never needed any, so long as the ' +
              'tunnel held. The tunnel did not hold.',
        tag: 'historic traffic exposed',
      },
      qsc: {
        title: 'Result: Attack Deflected',
        tone: 'good',
        body: 'The tunnel fell to Shor in exactly the same way &mdash; that part is identical. ' +
              'What the adversary finds inside is a <b>capsule</b>.<br><br>' +
              'Opening it means recovering the ML-KEM shared secret, which means solving ' +
              '<b>Module Learning With Errors</b> over ' +
              'R<sub>q</sub> = Z<sub>q</sub>[X]/(X<sup>256</sup>+1). Lattice problems expose no ' +
              'hidden subgroup structure, so Shor&rsquo;s algorithm simply does not apply. The ' +
              'best known quantum attack is Grover-accelerated sieving &mdash; a sub-quadratic ' +
              'speed-up, already accounted for in the parameter choice.<br><br>' +
              'The adversary holds 1088 bytes of KEM ciphertext and an AES-GCM blob. That is all.',
        tag: 'Module-LWE holds',
      },
    },
  };

  /* ---------------------------------------------------------------- state -- */

  let scene, camera, renderer, raf = null;
  let els = {};
  let mode = 'tls';
  let step = 0;
  let attacking = false;
  let harvesting = false;
  let ready = false;
  let running = false;
  let runClock = 0;

  let timers = [];

  const objects = {
    tunnelSegments: [],
    payload: null,
    capsuleShell: null,
    wave: null,
    beams: [],
    nodes: [],
    keyGlyphs: { qsc: [], tls: [] },
    pulses: [],
    trail: [],
    ghosts: [],
    threat: null,
    recordBeam: null,
  };

  let orbit = { theta: 0.38, phi: 1.04, radius: 37, dragging: false, lastX: 0, lastY: 0 };
  let payloadT = 0;

  /* ------------------------------------------------------------ narration -- */

  function narrate(entry) {
    if (!els.log) return;
    const empty = els.log.querySelector('.empty');
    if (empty) empty.remove();

    const div = document.createElement('div');
    div.className = `narrate__entry narrate__entry--${entry.tone || 'step'}`;
    div.innerHTML =
      `<div class="narrate__head">
         <span class="narrate__title">${entry.title}</span>
         <span class="narrate__clock">+${(runClock / 1000).toFixed(1)}s</span>
       </div>
       <div class="narrate__body">${entry.body}</div>` +
      (entry.tag ? `<span class="narrate__tag">${entry.tag}</span>` : '');

    els.log.appendChild(div);
    while (els.log.childElementCount > 60) els.log.removeChild(els.log.firstChild);
    els.log.parentElement.scrollTop = els.log.parentElement.scrollHeight;
  }

  function clearNarration() {
    if (els.log) els.log.innerHTML = '';
  }

  /* ------------------------------------------------------------- sequencer -- */

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  function schedule(fn, delay) {
    timers.push(setTimeout(fn, delay));
  }

  function setPhaseLabel(text) {
    if (els.hudPhase) els.hudPhase.textContent = text;
  }

  /* ------------------------------------------------------------- scaffold -- */

  function mount(refs) {
    els = refs;
    els.timeline.addEventListener('click', (event) => {
      const button = event.target.closest('.timeline__step');
      if (button) {
        stopSequences();
        setStep(Number(button.dataset.step));
      }
    });
  }

  /** Builds the scene lazily, the first time the tab is opened. */
  function activate() {
    if (!ready) {
      if (typeof THREE === 'undefined') {
        els.container.innerHTML =
          '<div class="empty">three.js failed to load. Check src/frontend/js/vendor/three.min.js.</div>';
        return;
      }
      build();
      ready = true;
    }
    resize();
    if (!raf) animate();
  }

  function build() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(COLOURS.bg);
    scene.fog = new THREE.Fog(COLOURS.bg, 48, 96);

    camera = new THREE.PerspectiveCamera(42, 1, 0.1, 400);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    els.container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.45));

    const key = new THREE.DirectionalLight(0xffffff, 0.85);
    key.position.set(12, 22, 14);
    scene.add(key);

    const rim = new THREE.DirectionalLight(0x3b82f6, 0.4);
    rim.position.set(-18, 8, -12);
    scene.add(rim);

    const grid = new THREE.GridHelper(90, 45, COLOURS.grid, COLOURS.grid);
    grid.position.y = -5;
    scene.add(grid);

    buildNodes();
    buildTunnel();
    buildPayload();
    buildKeyGlyphs();
    buildThreatActor();

    bindPointer();
    setMode('tls', { silent: true });
    setStep(0);
  }

  /* --------------------------------------------------------------- scene -- */

  function crispBox(w, h, d, colour, edgeColour) {
    const group = new THREE.Group();
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshStandardMaterial({ color: colour, roughness: 0.72, metalness: 0.18 })
    );
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)),
      new THREE.LineBasicMaterial({ color: edgeColour })
    );
    group.add(mesh, edges);
    return group;
  }

  /** Builds a text sprite so each node states what it is. */
  function makeLabel(text, colourHex, scale = 9) {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 96;
    const ctx = canvas.getContext('2d');
    ctx.font = '600 40px Consolas, ui-monospace, monospace';
    ctx.fillStyle = colourHex;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text.toUpperCase(), canvas.width / 2, canvas.height / 2);

    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(canvas),
      transparent: true,
      depthTest: false,
    }));
    sprite.scale.set(scale, scale * 0.19, 1);
    return sprite;
  }

  function buildNodes() {
    HOPS.forEach((hop, index) => {
      const endpoint = index === 0 || index === HOPS.length - 1;
      const height = endpoint ? 6 : 3;
      const edgeColour = index === HOPS.length - 1 ? COLOURS.target
                       : endpoint ? COLOURS.nodeEdge : COLOURS.hop;

      const node = crispBox(endpoint ? 4 : 2.6, height, endpoint ? 4 : 2.6,
                            COLOURS.node, edgeColour);
      node.position.set(hop.x, height / 2 - 5, 0);
      scene.add(node);

      const stalk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, endpoint ? 9 : 6),
        new THREE.MeshBasicMaterial({ color: edgeColour, transparent: true, opacity: 0.32 })
      );
      stalk.position.set(hop.x, endpoint ? 0.5 : -0.5, 0);
      scene.add(stalk);

      const label = makeLabel(hop.label, `#${edgeColour.toString(16).padStart(6, '0')}`);
      label.position.set(hop.x, endpoint ? 5.6 : 2.9, 0);
      scene.add(label);

      objects.nodes.push({ group: node, hop, index, edgeColour, height });
    });
  }

  function buildTunnel() {
    for (let i = 0; i < HOPS.length - 1; i += 1) {
      const from = HOPS[i].x;
      const length = HOPS[i + 1].x - from;

      const segment = new THREE.Mesh(
        new THREE.CylinderGeometry(1.5, 1.5, length, 24, 1, true),
        new THREE.MeshBasicMaterial({
          color: COLOURS.tunnel, transparent: true, opacity: 0.14, side: THREE.DoubleSide,
        })
      );
      segment.rotation.z = Math.PI / 2;
      segment.position.set(from + length / 2, -1.4, 0);
      scene.add(segment);

      const ribs = new THREE.Mesh(
        new THREE.CylinderGeometry(1.52, 1.52, length, 16, 1, true),
        new THREE.MeshBasicMaterial({
          color: COLOURS.tunnel, wireframe: true, transparent: true, opacity: 0.22,
        })
      );
      ribs.rotation.z = Math.PI / 2;
      ribs.position.copy(segment.position);
      scene.add(ribs);

      objects.tunnelSegments.push({ segment, ribs, index: i });
    }
  }

  function buildPayload() {
    objects.payload = crispBox(1.5, 0.9, 1.5, COLOURS.plaintext, COLOURS.plaintext);
    objects.payload.position.set(HOPS[0].x, -1.4, 0);
    objects.payload.visible = false;
    scene.add(objects.payload);

    objects.capsuleShell = new THREE.Group();
    const cage = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.9, 1),
      new THREE.MeshBasicMaterial({
        color: COLOURS.lattice, wireframe: true, transparent: true, opacity: 0.85,
      })
    );
    const glassShell = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.86, 1),
      new THREE.MeshStandardMaterial({
        color: COLOURS.capsule, transparent: true, opacity: 0.12, roughness: 0.25, metalness: 0.6,
      })
    );
    objects.capsuleShell.add(cage, glassShell);
    objects.capsuleShell.position.copy(objects.payload.position);
    objects.capsuleShell.visible = false;
    scene.add(objects.capsuleShell);
  }

  /**
   * Key glyphs shown during the key-generation phase.
   *
   * A torus reads as a "key" at a glance: the signing key at the originating
   * bank, the encapsulation key at the clearing house.
   */
  function buildKeyGlyphs() {
    const specs = {
      qsc: [
        { x: HOPS[0].x, colour: COLOURS.signing, text: 'ML-DSA-65 signing key' },
        { x: HOPS[4].x, colour: COLOURS.capsule, text: 'ML-KEM-768 encapsulation key' },
      ],
      tls: [
        { x: HOPS[0].x, colour: COLOURS.plaintext, text: 'ECDHE P-256 share' },
        { x: HOPS[4].x, colour: COLOURS.plaintext, text: 'ECDHE P-256 share' },
      ],
    };

    objects.keyGlyphs = { qsc: [], tls: [] };

    Object.entries(specs).forEach(([key, list]) => {
      list.forEach((spec) => {
        const group = new THREE.Group();

        const ring = new THREE.Mesh(
          new THREE.TorusGeometry(0.85, 0.14, 10, 32),
          new THREE.MeshBasicMaterial({ color: spec.colour, wireframe: true })
        );
        const core = new THREE.Mesh(
          new THREE.OctahedronGeometry(0.42),
          new THREE.MeshBasicMaterial({ color: spec.colour, transparent: true, opacity: 0.55 })
        );
        const caption = makeLabel(spec.text, `#${spec.colour.toString(16).padStart(6, '0')}`, 8);
        caption.position.set(0, 1.6, 0);

        group.add(ring, core, caption);
        group.position.set(spec.x, 3.2, 0);
        group.visible = false;
        scene.add(group);
        objects.keyGlyphs[key].push(group);
      });
    });
  }

  /** Shows the keypair glyphs for one mode, or hides every set. */
  function showKeyGlyphs(which) {
    ['qsc', 'tls'].forEach((key) => {
      objects.keyGlyphs[key].forEach((g) => { g.visible = (key === which); });
    });
  }

  function allKeyGlyphs() {
    return [...objects.keyGlyphs.qsc, ...objects.keyGlyphs.tls];
  }

  function buildThreatActor() {
    const threat = new THREE.Mesh(
      new THREE.OctahedronGeometry(1.5),
      new THREE.MeshBasicMaterial({ color: COLOURS.threat, wireframe: true })
    );
    threat.position.set(0, 8.5, -6);
    scene.add(threat);
    objects.threat = threat;

    const caption = makeLabel('Quantum Eavesdropper', '#ef4444', 10);
    caption.position.set(0, 2.4, 0);
    threat.add(caption);

    objects.wave = new THREE.Mesh(
      new THREE.RingGeometry(1, 1.18, 64),
      new THREE.MeshBasicMaterial({
        color: COLOURS.threat, transparent: true, opacity: 0, side: THREE.DoubleSide,
      })
    );
    objects.wave.rotation.x = -Math.PI / 2;
    objects.wave.position.set(0, -4.9, 0);
    scene.add(objects.wave);
  }

  /* ------------------------------------------------------------- effects -- */

  /** Expanding ring at a node, to show which hop is currently handling the message. */
  function pulseAt(nodeIndex, colour) {
    const node = objects.nodes[nodeIndex];
    if (!node) return;

    const ring = new THREE.Mesh(
      new THREE.RingGeometry(1.4, 1.62, 48),
      new THREE.MeshBasicMaterial({
        color: colour, transparent: true, opacity: 0.9, side: THREE.DoubleSide,
      })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(node.hop.x, -4.85, 0);
    scene.add(ring);
    objects.pulses.push(ring);
  }

  /** Drops a fading marker behind the moving payload so its path is legible. */
  function dropTrail() {
    const dot = new THREE.Mesh(
      new THREE.SphereGeometry(0.13, 8, 8),
      new THREE.MeshBasicMaterial({
        color: mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext,
        transparent: true,
        opacity: 0.7,
      })
    );
    dot.position.copy(objects.payload.position);
    scene.add(dot);
    objects.trail.push(dot);
  }

  /** A copy of the message flying off to the eavesdropper's archive. */
  function spawnGhost() {
    const ghost = new THREE.Mesh(
      new THREE.BoxGeometry(0.6, 0.4, 0.6),
      new THREE.MeshBasicMaterial({
        color: COLOURS.threat, wireframe: true, transparent: true, opacity: 0.9,
      })
    );
    ghost.position.copy(objects.payload.position);
    ghost.userData.progress = 0;
    ghost.userData.from = objects.payload.position.clone();
    scene.add(ghost);
    objects.ghosts.push(ghost);
  }

  function clearEffects() {
    [...objects.pulses, ...objects.trail, ...objects.ghosts, ...objects.beams]
      .forEach((obj) => scene.remove(obj));
    objects.pulses = [];
    objects.trail = [];
    objects.ghosts = [];
    objects.beams = [];
    objects.wave.material.opacity = 0;
    objects.wave.scale.set(1, 1, 1);
  }

  /* ---------------------------------------------------------- interaction -- */

  function bindPointer() {
    const canvas = renderer.domElement;

    canvas.addEventListener('pointerdown', (e) => {
      orbit.dragging = true;
      orbit.lastX = e.clientX;
      orbit.lastY = e.clientY;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointerup', (e) => {
      orbit.dragging = false;
      canvas.releasePointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!orbit.dragging) return;
      orbit.theta -= (e.clientX - orbit.lastX) * 0.006;
      orbit.phi = Math.min(1.52, Math.max(0.22, orbit.phi - (e.clientY - orbit.lastY) * 0.005));
      orbit.lastX = e.clientX;
      orbit.lastY = e.clientY;
    });
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      orbit.radius = Math.min(72, Math.max(16, orbit.radius + e.deltaY * 0.02));
    }, { passive: false });

    window.addEventListener('resize', resize);
  }

  function resize() {
    if (!renderer) return;
    const { clientWidth: w, clientHeight: h } = els.container;
    if (w === 0 || h === 0) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  /* ---------------------------------------------------------------- modes -- */

  function stopSequences() {
    clearTimers();
    running = false;
    attacking = false;
    harvesting = false;
  }

  function setMode(next, options = {}) {
    const changed = mode !== next;
    mode = next;
    stopSequences();
    clearEffects();

    objects.capsuleShell.visible = (mode === 'qsc') && objects.payload.visible;
    setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
    restoreTunnel();
    payloadT = STEP_POSITIONS[step] ?? 0;

    els.hudMode.textContent = mode === 'qsc'
      ? 'QSC Capsule (message security)'
      : 'TLS 1.3 Transport (channel security)';
    els.hudPayload.textContent = mode === 'qsc'
      ? 'sealed under ML-KEM + AES-GCM'
      : 'plaintext inside the tunnel';
    els.hudStatus.textContent = mode === 'qsc'
      ? 'Payload is armoured before transmission. The tunnel is now optional, not load-bearing.'
      : 'Payload is protected only while inside the tunnel. Protection ends wherever TLS terminates.';
    setPhaseLabel('idle');

    document.getElementById('btn-mode-tls').classList.toggle('btn--primary', mode === 'tls');
    document.getElementById('btn-mode-qsc').classList.toggle('btn--primary', mode === 'qsc');

    if (changed && !options.silent) {
      runClock = 0;
      narrate({
        title: mode === 'qsc' ? 'Mode B &mdash; QSC Capsule' : 'Mode A &mdash; TLS 1.3 Only',
        tone: mode === 'qsc' ? 'good' : 'warn',
        body: mode === 'qsc'
          ? 'The payment will be sealed in a post-quantum capsule <b>before</b> it enters the ' +
            'network. TLS still wraps the connection, but it is no longer what protects the ' +
            'payment. Press <b>Run Full Process</b> to watch it travel.'
          : 'The payment will travel as plaintext inside a TLS 1.3 tunnel &mdash; the way ' +
            'essentially every production banking API works today. Press <b>Run Full ' +
            'Process</b> to watch what happens at each hop.',
        tag: 'mode selected',
      });
    }
  }

  function setStep(index) {
    step = index;
    [...els.timeline.children].forEach((btn, i) =>
      btn.classList.toggle('is-active', i === index));

    payloadT = STEP_POSITIONS[index] ?? 0;
    objects.payload.visible = index >= 1;
    objects.capsuleShell.visible = (mode === 'qsc') && index >= 1;
    showKeyGlyphs(index === 0 ? mode : null);
    els.hudStatus.textContent = STEP_TEXT[index];
    setPhaseLabel(`step ${index + 1} of 5`);

    if (index === 3) highlightProxyTermination();
    else if (!attacking) restoreTunnel();
  }

  function setPayloadColour(colour) {
    objects.payload.children.forEach((child) => {
      if (child.material) child.material.color.setHex(colour);
    });
  }

  function restoreTunnel() {
    objects.tunnelSegments.forEach(({ segment, ribs }) => {
      segment.material.opacity = 0.14;
      ribs.material.opacity = 0.22;
      segment.visible = true;
      ribs.visible = true;
    });
  }

  function highlightProxyTermination() {
    restoreTunnel();
    const proxySpan = objects.tunnelSegments[1];
    proxySpan.segment.visible = false;
    proxySpan.ribs.visible = false;

    if (mode === 'tls') {
      setPayloadColour(COLOURS.exposed);
      els.hudPayload.textContent = 'EXPOSED in proxy memory';
    } else {
      setPayloadColour(COLOURS.capsule);
      els.hudPayload.textContent = 'still sealed at the hop';
    }
  }

  /* ------------------------------------------------------- full process -- */

  function runFullProcess() {
    stopSequences();
    clearEffects();
    clearNarration();

    running = true;
    runClock = 0;
    payloadT = 0;
    objects.payload.visible = false;
    objects.capsuleShell.visible = false;
    showKeyGlyphs(null);
    setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
    restoreTunnel();

    narrate({
      title: mode === 'qsc' ? 'Running: QSC Capsule' : 'Running: TLS 1.3 Only',
      tone: 'note',
      body: 'One high-value payment, five hops, end to end. Watch the <b>Reverse Proxy</b> ' +
            'step in particular &mdash; that is where the two modes diverge.',
      tag: 'sequence started',
    });

    let offset = 0;
    RUN_PHASES.forEach((phase) => {
      schedule(() => enterRunPhase(phase), offset);
      offset += phase.duration;
    });

    schedule(() => {
      running = false;
      setPhaseLabel('complete');
      narrate({
        title: 'Sequence Complete',
        tone: mode === 'qsc' ? 'good' : 'warn',
        body: mode === 'qsc'
          ? 'The payment crossed four hops it did not control and was readable at none of ' +
            'them. Now press <b>Run Quantum Attack</b> to see what a future adversary gets ' +
            'from a recording of that journey.'
          : 'The payment was exposed in plaintext at the proxy and written to disk at the ' +
            'broker, and the settlement engine had no way to verify it. Now press <b>Run ' +
            'Quantum Attack</b>, then switch to <b>Mode B</b> and compare.',
        tag: 'try the attack next',
      });
    }, offset);
  }

  function enterRunPhase(phase) {
    runClock += phase.duration;
    payloadT = phase.target;
    setStep(phase.timeline);
    setPhaseLabel(phase.id);

    const script = RUN_SCRIPT[phase.id][mode];

    switch (phase.id) {
      case 'keygen':
        showKeyGlyphs(mode);
        objects.payload.visible = false;
        objects.capsuleShell.visible = false;
        pulseAt(0, COLOURS.signing);
        pulseAt(4, COLOURS.capsule);
        break;

      case 'encap':
        showKeyGlyphs(null);
        objects.payload.visible = true;
        objects.capsuleShell.visible = (mode === 'qsc');
        setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
        pulseAt(0, mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
        break;

      case 'proxy':
        highlightProxyTermination();
        pulseAt(2, mode === 'qsc' ? COLOURS.capsule : COLOURS.exposed);
        break;

      case 'settle':
        restoreTunnel();
        setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
        els.hudPayload.textContent = mode === 'qsc'
          ? 'validated and decrypted'
          : 'accepted on trust';
        pulseAt(4, COLOURS.target);
        break;

      default:
        pulseAt(phase.node, mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
        break;
    }

    els.hudStatus.textContent = script.title.replace(/&mdash;/g, '-').replace(/<[^>]+>/g, '');
    narrate(script);
  }

  /* --------------------------------------------------------------- attack -- */

  function runAttack() {
    stopSequences();
    clearEffects();

    attacking = true;
    runClock = 0;

    // The attack needs a message on the wire to record.
    if (!objects.payload.visible) {
      objects.payload.visible = true;
      objects.capsuleShell.visible = (mode === 'qsc');
      payloadT = 0.42;
      setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
    }

    let offset = 0;
    ATTACK_PHASES.forEach((phase) => {
      schedule(() => enterAttackPhase(phase), offset);
      offset += phase.duration;
    });

    schedule(() => { setPhaseLabel('attack complete'); }, offset);
  }

  function enterAttackPhase(phase) {
    runClock += phase.duration;
    setPhaseLabel(phase.id);

    const script = (ATTACK_SCRIPT[phase.id].both || ATTACK_SCRIPT[phase.id][mode]);

    switch (phase.id) {
      case 'harvest':
        harvesting = true;
        els.hudPayload.textContent = 'being recorded off the wire';
        els.hudStatus.textContent =
          'Passive interception. The adversary copies the encrypted stream to long-term storage.';
        break;

      case 'archive':
        harvesting = false;
        els.hudStatus.textContent =
          'The archive waits. The ciphertext is already out of the bank\'s control.';
        break;

      case 'shor':
        objects.wave.scale.set(1, 1, 1);
        objects.wave.material.opacity = 0.9;
        fireBeams();
        objects.tunnelSegments.forEach(({ segment, ribs }) => {
          segment.visible = false;
          ribs.visible = false;
        });
        els.hudStatus.textContent = "Shor's algorithm recovers the archived ECDHE session keys.";
        break;

      case 'verdict':
        if (mode === 'tls') {
          setPayloadColour(COLOURS.exposed);
          els.hudPayload.textContent = 'RECOVERED by the adversary';
          els.hudStatus.textContent =
            'Tunnel stripped. Every payment recorded on this link is now readable.';
        } else {
          setPayloadColour(COLOURS.capsule);
          els.hudPayload.textContent = 'ciphertext only - attack deflected';
          els.hudStatus.textContent =
            'Tunnel stripped, capsule intact. Recovering it means solving Module-LWE.';
        }
        break;
    }

    narrate(ATTACK_SCRIPT[phase.id].both || ATTACK_SCRIPT[phase.id][mode]);
  }

  function fireBeams() {
    const target = objects.payload.position.clone();
    for (let i = 0; i < 5; i += 1) {
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(
          objects.threat.position.x + (i - 2) * 1.1,
          objects.threat.position.y,
          objects.threat.position.z
        ),
        target,
      ]);
      const beam = new THREE.Line(
        geometry,
        new THREE.LineBasicMaterial({ color: COLOURS.threat, transparent: true, opacity: 0.75 })
      );
      scene.add(beam);
      objects.beams.push(beam);
    }
  }

  function reset() {
    stopSequences();
    clearEffects();
    clearNarration();
    objects.payload.visible = false;
    objects.capsuleShell.visible = false;
    setMode(mode, { silent: true });
    setStep(0);
    els.hudStatus.textContent = 'Idle. Pick a mode, then press Run Full Process.';
  }

  /* ------------------------------------------------------------ animation -- */

  let lastTrailDrop = 0;
  let lastGhostSpawn = 0;

  function animate() {
    raf = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;
    const now = performance.now();

    camera.position.set(
      orbit.radius * Math.sin(orbit.phi) * Math.sin(orbit.theta),
      orbit.radius * Math.cos(orbit.phi),
      orbit.radius * Math.sin(orbit.phi) * Math.cos(orbit.theta)
    );
    camera.lookAt(0, -1, 0);

    // Payload eases toward its phase position.
    const targetX = HOPS[0].x + (HOPS[HOPS.length - 1].x - HOPS[0].x) * payloadT;
    const before = objects.payload.position.x;
    objects.payload.position.x += (targetX - before) * 0.045;
    objects.payload.position.y = -1.4 + Math.sin(t * 1.6) * 0.12;
    objects.payload.rotation.y = t * 0.5;

    // Leave a trail only while the message is actually moving.
    if (objects.payload.visible && Math.abs(targetX - before) > 0.06 && now - lastTrailDrop > 70) {
      dropTrail();
      lastTrailDrop = now;
    }

    objects.capsuleShell.position.copy(objects.payload.position);
    objects.capsuleShell.rotation.y = -t * 0.34;
    objects.capsuleShell.rotation.x = t * 0.16;

    allKeyGlyphs().forEach((glyph, i) => {
      if (!glyph.visible) return;
      glyph.rotation.y = t * (i % 2 ? -0.9 : 0.9);
      glyph.children[0].rotation.x = t * 1.4;
      glyph.position.y = 3.2 + Math.sin(t * 1.5 + i) * 0.18;
    });

    objects.threat.rotation.y = t * 0.6;
    objects.threat.rotation.x = t * 0.25;
    objects.threat.position.x = Math.sin(t * 0.35) * 8;

    // Harvest: copies of the message peel off toward the archive.
    if (harvesting && objects.payload.visible && now - lastGhostSpawn > 320) {
      spawnGhost();
      lastGhostSpawn = now;
    }

    for (let i = objects.ghosts.length - 1; i >= 0; i -= 1) {
      const ghost = objects.ghosts[i];
      ghost.userData.progress += 0.016;
      ghost.position.lerpVectors(ghost.userData.from, objects.threat.position, ghost.userData.progress);
      ghost.rotation.x += 0.06;
      ghost.material.opacity = 0.9 * (1 - ghost.userData.progress);
      if (ghost.userData.progress >= 1) {
        scene.remove(ghost);
        objects.ghosts.splice(i, 1);
      }
    }

    for (let i = objects.trail.length - 1; i >= 0; i -= 1) {
      const dot = objects.trail[i];
      dot.material.opacity -= 0.012;
      dot.scale.multiplyScalar(0.992);
      if (dot.material.opacity <= 0) {
        scene.remove(dot);
        objects.trail.splice(i, 1);
      }
    }

    for (let i = objects.pulses.length - 1; i >= 0; i -= 1) {
      const ring = objects.pulses[i];
      ring.scale.multiplyScalar(1.028);
      ring.material.opacity -= 0.016;
      if (ring.material.opacity <= 0) {
        scene.remove(ring);
        objects.pulses.splice(i, 1);
      }
    }

    if (objects.wave.material.opacity > 0) {
      objects.wave.scale.multiplyScalar(1.02);
      objects.wave.material.opacity *= 0.986;
      if (objects.wave.material.opacity < 0.02) {
        objects.wave.material.opacity = 0;
        objects.wave.scale.set(1, 1, 1);
      }
    }

    if (attacking && objects.beams.length) {
      objects.beams.forEach((beam, i) => {
        beam.geometry.setFromPoints([
          new THREE.Vector3(
            objects.threat.position.x + (i - 2) * 1.1,
            objects.threat.position.y,
            objects.threat.position.z
          ),
          objects.payload.position.clone(),
        ]);
        beam.material.opacity = 0.45 + Math.sin(t * 7 + i) * 0.3;
      });

      if (mode === 'qsc') {
        const pulse = 1 + Math.sin(t * 6) * 0.06;
        objects.capsuleShell.scale.set(pulse, pulse, pulse);
      }
    } else {
      objects.capsuleShell.scale.set(1, 1, 1);
    }

    renderer.render(scene, camera);
  }

  return {
    mount, activate, setMode, setStep, runAttack, runFullProcess, reset,
    clearNarration,
  };
})();
