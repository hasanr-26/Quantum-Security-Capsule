/* ==========================================================================
   visualizer_3d.js - channel security vs message security, in three dimensions.

   The scene models one payment crossing an untrusted network:

     Node A (originating bank) -> edge -> reverse proxy -> broker -> Node B

   Mode A wraps the payload in a TLS tunnel. The tunnel is strong, but it
   terminates at the proxy, and it is built on ECDHE - which Shor's algorithm
   breaks. Mode A therefore fails twice: once at the hop, once retroactively.

   Mode B leaves the tunnel in place but seals the payload inside a lattice
   capsule. The tunnel can be stripped without the payload becoming readable.

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
  };

  const HOPS = [
    { x: -13, label: 'Originating Bank' },
    { x:  -6, label: 'Edge Gateway' },
    { x:   0, label: 'Reverse Proxy' },
    { x:   6, label: 'Message Broker' },
    { x:  13, label: 'Clearing House' },
  ];

  const STEP_TEXT = [
    'Key generation. ML-KEM-768 and ML-DSA-65 keypairs are established at both ends.',
    'Encapsulation. The payload is sealed before it touches the wire.',
    'Wire transit. The message crosses hops nobody controls end to end.',
    'Proxy hop. TLS terminates here - this is where channel security ends.',
    'Settlement. The receiver validates five controls before releasing plaintext.',
  ];

  let scene, camera, renderer, raf = null;
  let els = {};
  let mode = 'tls';
  let step = 2;
  let attacking = false;
  let ready = false;

  const objects = {
    tunnel: null,
    tunnelSegments: [],
    payload: null,
    capsuleShell: null,
    wave: null,
    beams: [],
    nodes: [],
  };

  let orbit = { theta: 0.42, phi: 1.16, radius: 34, dragging: false, lastX: 0, lastY: 0 };
  let payloadT = 0;

  /* ------------------------------------------------------------ scaffold -- */

  function mount(refs) {
    els = refs;
    els.timeline.addEventListener('click', (event) => {
      const button = event.target.closest('.timeline__step');
      if (button) setStep(Number(button.dataset.step));
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
    scene.fog = new THREE.Fog(COLOURS.bg, 46, 92);

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
    buildThreatActor();

    bindPointer();
    setMode('tls');
    setStep(2);
  }

  /* --------------------------------------------------------------- scene -- */

  function crispBox(w, h, d, colour, edgeColour) {
    const group = new THREE.Group();
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshStandardMaterial({
        color: colour, roughness: 0.72, metalness: 0.18,
      })
    );
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)),
      new THREE.LineBasicMaterial({ color: edgeColour })
    );
    group.add(mesh, edges);
    return group;
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
      objects.nodes.push({ group: node, hop, index });

      // Vertical marker so hops read as infrastructure, not floating boxes.
      const stalk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, endpoint ? 9 : 6),
        new THREE.MeshBasicMaterial({ color: edgeColour, transparent: true, opacity: 0.32 })
      );
      stalk.position.set(hop.x, endpoint ? 0.5 : -0.5, 0);
      scene.add(stalk);
    });
  }

  function buildTunnel() {
    // One cylinder per span, so the proxy span can be removed independently.
    for (let i = 0; i < HOPS.length - 1; i += 1) {
      const from = HOPS[i].x;
      const to = HOPS[i + 1].x;
      const length = to - from;

      const segment = new THREE.Mesh(
        new THREE.CylinderGeometry(1.5, 1.5, length, 24, 1, true),
        new THREE.MeshBasicMaterial({
          color: COLOURS.tunnel,
          transparent: true,
          opacity: 0.14,
          side: THREE.DoubleSide,
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
    // The message itself: a small slab that reads as "a document".
    objects.payload = crispBox(1.5, 0.9, 1.5, COLOURS.plaintext, COLOURS.plaintext);
    objects.payload.position.set(HOPS[0].x, -1.4, 0);
    scene.add(objects.payload);

    // The capsule armour: a module-lattice shell drawn as an icosahedral cage.
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
        color: COLOURS.capsule, transparent: true, opacity: 0.12,
        roughness: 0.25, metalness: 0.6,
      })
    );
    objects.capsuleShell.add(cage, glassShell);
    objects.capsuleShell.position.copy(objects.payload.position);
    objects.capsuleShell.visible = false;
    scene.add(objects.capsuleShell);
  }

  function buildThreatActor() {
    const threat = new THREE.Mesh(
      new THREE.OctahedronGeometry(1.5),
      new THREE.MeshBasicMaterial({ color: COLOURS.threat, wireframe: true })
    );
    threat.position.set(0, 8.5, -6);
    threat.name = 'threat';
    scene.add(threat);
    objects.threat = threat;

    // Expanding shockwave used when Shor's algorithm is applied.
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

  function setMode(next) {
    mode = next;
    attacking = false;
    payloadT = 0;

    objects.capsuleShell.visible = (mode === 'qsc');
    setPayloadColour(mode === 'qsc' ? COLOURS.capsule : COLOURS.plaintext);
    restoreTunnel();

    els.hudMode.textContent = mode === 'qsc' ? 'QSC Capsule (message security)' : 'TLS 1.3 Transport (channel security)';
    els.hudPayload.textContent = mode === 'qsc'
      ? 'sealed under ML-KEM + AES-GCM'
      : 'plaintext inside the tunnel';
    els.hudStatus.textContent = mode === 'qsc'
      ? 'Payload is armoured before transmission. The tunnel is now optional, not load-bearing.'
      : 'Payload is protected only while inside the tunnel. Protection ends wherever TLS terminates.';

    document.getElementById('btn-mode-tls').classList.toggle('btn--primary', mode === 'tls');
    document.getElementById('btn-mode-qsc').classList.toggle('btn--primary', mode === 'qsc');
  }

  function setStep(index) {
    step = index;
    [...els.timeline.children].forEach((btn, i) =>
      btn.classList.toggle('is-active', i === index));

    payloadT = [0, 0, 0.42, 0.5, 1][index] ?? 0;
    els.hudStatus.textContent = STEP_TEXT[index];

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
      segment.material.color.setHex(COLOURS.tunnel);
      ribs.material.opacity = 0.22;
      ribs.material.color.setHex(COLOURS.tunnel);
      segment.visible = true;
      ribs.visible = true;
    });
    objects.wave.material.opacity = 0;
    objects.beams.forEach((b) => scene.remove(b));
    objects.beams = [];
  }

  /** At the proxy the tunnel genuinely ends - the payload is in clear memory. */
  function highlightProxyTermination() {
    restoreTunnel();
    const proxySpan = objects.tunnelSegments[1];
    proxySpan.segment.visible = false;
    proxySpan.ribs.visible = false;

    if (mode === 'tls') {
      setPayloadColour(COLOURS.exposed);
      els.hudPayload.textContent = 'EXPOSED in proxy memory';
      els.hudStatus.textContent =
        'TLS terminated at the reverse proxy. The payment is plaintext in that process, ' +
        'readable by anyone with access to the host.';
    } else {
      els.hudPayload.textContent = 'still sealed at the hop';
      els.hudStatus.textContent =
        'TLS terminated here too - but the capsule never depended on it. The proxy ' +
        'forwards ciphertext it cannot read.';
    }
  }

  /* --------------------------------------------------------------- attack -- */

  function runAttack() {
    attacking = true;
    objects.wave.scale.set(1, 1, 1);
    objects.wave.material.opacity = 0.85;

    objects.beams.forEach((b) => scene.remove(b));
    objects.beams = [];

    const target = objects.payload.position.clone();
    for (let i = 0; i < 5; i += 1) {
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(objects.threat.position.x + (i - 2) * 1.1, objects.threat.position.y, objects.threat.position.z),
        target,
      ]);
      const beam = new THREE.Line(
        geometry,
        new THREE.LineBasicMaterial({ color: COLOURS.threat, transparent: true, opacity: 0.75 })
      );
      scene.add(beam);
      objects.beams.push(beam);
    }

    if (mode === 'tls') {
      objects.tunnelSegments.forEach(({ segment, ribs }) => {
        segment.visible = false;
        ribs.visible = false;
      });
      setPayloadColour(COLOURS.exposed);
      els.hudPayload.textContent = 'RECOVERED by the adversary';
      els.hudStatus.textContent =
        "Shor's algorithm recovered the ECDHE session keys from archived traffic. " +
        'The tunnel is gone and every historic payment recorded on this link is readable.';
    } else {
      objects.tunnelSegments.forEach(({ segment, ribs }) => {
        segment.visible = false;
        ribs.visible = false;
      });
      setPayloadColour(COLOURS.capsule);
      els.hudPayload.textContent = 'ciphertext only - attack deflected';
      els.hudStatus.textContent =
        'The tunnel fell to Shor as before. The capsule did not: recovering it means ' +
        'solving Module-LWE, which exposes no hidden subgroup for Shor to exploit.';
    }
  }

  function reset() {
    attacking = false;
    setMode(mode);
    setStep(2);
  }

  /* ------------------------------------------------------------ animation -- */

  function animate() {
    raf = requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    // Orbit camera
    camera.position.set(
      orbit.radius * Math.sin(orbit.phi) * Math.sin(orbit.theta),
      orbit.radius * Math.cos(orbit.phi),
      orbit.radius * Math.sin(orbit.phi) * Math.cos(orbit.theta)
    );
    camera.lookAt(0, -1, 0);

    // Payload glides along the corridor, easing toward its step position.
    const targetX = HOPS[0].x + (HOPS[HOPS.length - 1].x - HOPS[0].x) * payloadT;
    objects.payload.position.x += (targetX - objects.payload.position.x) * 0.06;
    objects.payload.position.y = -1.4 + Math.sin(t * 1.6) * 0.12;
    objects.payload.rotation.y = t * 0.5;

    objects.capsuleShell.position.copy(objects.payload.position);
    objects.capsuleShell.rotation.y = -t * 0.34;
    objects.capsuleShell.rotation.x = t * 0.16;

    objects.threat.rotation.y = t * 0.6;
    objects.threat.rotation.x = t * 0.25;
    objects.threat.position.x = Math.sin(t * 0.35) * 8;

    // Shockwave expansion
    if (objects.wave.material.opacity > 0) {
      objects.wave.scale.multiplyScalar(1.022);
      objects.wave.material.opacity *= 0.985;
      if (objects.wave.material.opacity < 0.02) {
        objects.wave.material.opacity = 0;
        objects.wave.scale.set(1, 1, 1);
      }
    }

    // Beams track the payload while an attack is live.
    if (attacking) {
      objects.beams.forEach((beam, i) => {
        const points = [
          new THREE.Vector3(
            objects.threat.position.x + (i - 2) * 1.1,
            objects.threat.position.y,
            objects.threat.position.z
          ),
          objects.payload.position.clone(),
        ];
        beam.geometry.setFromPoints(points);
        beam.material.opacity = 0.45 + Math.sin(t * 7 + i) * 0.3;
      });

      if (mode === 'qsc') {
        // Lattice flares as it absorbs the attack.
        const pulse = 1 + Math.sin(t * 6) * 0.06;
        objects.capsuleShell.scale.set(pulse, pulse, pulse);
      }
    } else {
      objects.capsuleShell.scale.set(1, 1, 1);
    }

    renderer.render(scene, camera);
  }

  return { mount, activate, setMode, setStep, runAttack, reset };
})();
