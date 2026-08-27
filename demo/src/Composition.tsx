import {
  AbsoluteFill,
  Audio,
  Composition,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const W = 1280;
const H = 720;

const BG = "#0d1117";
const FG = "#c9d1d9";
const DIM = "#6e7681";
const GREEN = "#3fb950";
const RED = "#f85149";
const YELLOW = "#d29922";
const BLUE = "#58a6ff";
const MONO =
  'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Monaco, "Cascadia Mono", monospace';

/* ---------------------------------------------------------------- helpers */

const useFade = (inAt = 0, len = 10) => {
  const f = useCurrentFrame();
  return interpolate(f, [inAt, inAt + len], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

/** A caption strip that names the hook event responsible for the sound. */
const Caption: React.FC<{ event: string; text: string; color?: string }> = ({
  event,
  text,
  color = BLUE,
}) => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const s = spring({ frame: f, fps, config: { damping: 200 }, durationInFrames: 14 });
  return (
    <div
      style={{
        position: "absolute",
        left: 64,
        right: 64,
        bottom: 52,
        display: "flex",
        alignItems: "center",
        gap: 16,
        opacity: s,
        transform: `translateY(${(1 - s) * 18}px)`,
      }}
    >
      <span
        style={{
          fontFamily: MONO,
          fontSize: 22,
          color: BG,
          background: color,
          padding: "6px 14px",
          borderRadius: 8,
          fontWeight: 700,
          whiteSpace: "nowrap",
        }}
      >
        {event}
      </span>
      <span style={{ fontFamily: MONO, fontSize: 26, color: FG }}>{text}</span>
    </div>
  );
};

/** Chrome of a terminal window. */
const Term: React.FC<{ children: React.ReactNode; dim?: number }> = ({
  children,
  dim = 0,
}) => (
  <div
    style={{
      position: "absolute",
      left: 64,
      right: 64,
      top: 72,
      height: 470,
      background: "#010409",
      border: "1px solid #30363d",
      borderRadius: 12,
      overflow: "hidden",
      filter: `brightness(${1 - dim * 0.55}) saturate(${1 - dim * 0.8})`,
      boxShadow: "0 24px 64px rgba(0,0,0,.6)",
    }}
  >
    <div
      style={{
        height: 38,
        background: "#161b22",
        borderBottom: "1px solid #30363d",
        display: "flex",
        alignItems: "center",
        paddingLeft: 16,
        gap: 8,
      }}
    >
      {["#ff5f57", "#febc2e", "#28c840"].map((c) => (
        <div key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />
      ))}
      <span style={{ fontFamily: MONO, fontSize: 14, color: DIM, marginLeft: 12 }}>
        claude
      </span>
    </div>
    <div style={{ padding: "22px 26px", fontFamily: MONO, fontSize: 23, lineHeight: 1.65 }}>
      {children}
    </div>
  </div>
);

/** Types text out character by character. */
const Typed: React.FC<{ text: string; start: number; cps?: number; color?: string }> = ({
  text,
  start,
  cps = 26,
  color = FG,
}) => {
  const f = useCurrentFrame();
  const n = Math.max(0, Math.floor(((f - start) / FPS) * cps));
  return <span style={{ color }}>{text.slice(0, n)}</span>;
};

const Spinner: React.FC<{ label: string }> = ({ label }) => {
  const f = useCurrentFrame();
  const frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  return (
    <div style={{ color: YELLOW }}>
      {frames[f % frames.length]} {label}
      <span style={{ color: DIM }}> ({Math.floor(f / FPS)}s)</span>
    </div>
  );
};

/* ---------------------------------------------------------------- scenes */

const Title: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const s = spring({ frame: f, fps, config: { damping: 200 }, durationInFrames: 22 });
  const out = interpolate(f, [66, 80], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center", opacity: out }}
    >
      <div style={{ fontSize: 96, opacity: s, transform: `scale(${0.9 + s * 0.1})` }}>
        🫖
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 72,
          color: FG,
          fontWeight: 700,
          marginTop: 18,
          opacity: s,
          transform: `translateY(${(1 - s) * 20}px)`,
        }}
      >
        kettle
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 30,
          color: DIM,
          marginTop: 22,
          opacity: interpolate(f, [16, 32], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        put it on. walk away.
      </div>
    </AbsoluteFill>
  );
};

/** Long task finishes while you're away → Stop. */
const SceneDone: React.FC = () => {
  const f = useCurrentFrame();
  const away = f >= 40 && f < 118;                       // you left the desk
  const dim = interpolate(f, [40, 55, 112, 120], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ opacity: useFade(0, 8) }}>
      <Term dim={dim}>
        <div style={{ color: DIM }}>
          <span style={{ color: GREEN }}>&gt;</span>{" "}
          <Typed text="refactor the auth module and run the tests" start={2} />
        </div>
        <div style={{ marginTop: 14 }}>{f < 118 ? <Spinner label="Running tests…" /> : null}</div>
        {f >= 118 ? (
          <div style={{ marginTop: 14, color: GREEN }}>
            ✓ 24 tests passed — auth module refactored
          </div>
        ) : null}
      </Term>

      {away ? (
        <div
          style={{
            position: "absolute",
            top: 250,
            width: "100%",
            textAlign: "center",
            fontFamily: MONO,
            fontSize: 34,
            color: FG,
            opacity: interpolate(f, [46, 58, 106, 116], [0, 1, 1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          ☕️ &nbsp;you walked away
        </div>
      ) : null}

      {f >= 118 ? (
        <>
          <Sequence from={118}>
            <Audio src={staticFile("glass.mp3")} />
          </Sequence>
          <Caption event="Stop" text="it finished — you heard it from the kitchen" color={GREEN} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

/** A permission prompt is waiting → Notification:permission_prompt. */
const ScenePermission: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: useFade(0, 8) }}>
      <Term>
        <div style={{ color: DIM }}>
          <span style={{ color: GREEN }}>&gt;</span> deploy to staging
        </div>
        {f >= 12 ? (
          <div
            style={{
              marginTop: 20,
              border: `1px solid ${YELLOW}`,
              borderRadius: 8,
              padding: "16px 20px",
              background: "rgba(210,153,34,.08)",
            }}
          >
            <div style={{ color: YELLOW }}>Allow this command?</div>
            <div style={{ color: FG, marginTop: 8 }}>$ ssh prod-01 &apos;./deploy.sh&apos;</div>
            <div style={{ color: DIM, marginTop: 12, fontSize: 20 }}>
              1. Yes &nbsp; 2. Yes, and don&apos;t ask again &nbsp; 3. No
            </div>
          </div>
        ) : null}
      </Term>
      {f >= 12 ? (
        <>
          <Sequence from={12}>
            <Audio src={staticFile("funk.mp3")} />
          </Sequence>
          <Caption event="Notification" text="it needs you — not five minutes from now" color={YELLOW} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

/** The turn died on a rate limit → StopFailure. The one nobody sets up. */
const SceneError: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: useFade(0, 8) }}>
      <Term>
        <div style={{ color: DIM }}>
          <span style={{ color: GREEN }}>&gt;</span> migrate the database schema
        </div>
        <div style={{ marginTop: 14 }}>
          {f < 20 ? <Spinner label="Thinking…" /> : null}
        </div>
        {f >= 20 ? (
          <div
            style={{
              marginTop: 14,
              border: `1px solid ${RED}`,
              borderRadius: 8,
              padding: "16px 20px",
              background: "rgba(248,81,73,.08)",
              color: RED,
            }}
          >
            ✗ API error: rate_limit_exceeded
            <div style={{ color: DIM, marginTop: 8, fontSize: 20 }}>
              turn ended. nothing is running.
            </div>
          </div>
        ) : null}
      </Term>
      {f >= 20 ? (
        <>
          <Sequence from={20}>
            <Audio src={staticFile("basso.mp3")} />
          </Sequence>
          <Caption event="StopFailure" text="the one nobody sets up — and misses the most" color={RED} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

/** What the CLI looks like + how to install. */
const SceneCli: React.FC = () => {
  const f = useCurrentFrame();
  const rows: [string, string, string, string][] = [
    ["stop", "done,up", GREEN, "it finished"],
    ["ask", "alert", YELLOW, "needs permission"],
    ["idle", "hmm", BLUE, "waiting on you"],
    ["sub", "soft", DIM, "subagent done"],
    ["error", "boom say:…", RED, "the turn died"],
  ];
  return (
    <AbsoluteFill style={{ opacity: useFade(0, 8) }}>
      <Term>
        <div style={{ color: DIM }}>
          <span style={{ color: GREEN }}>&gt;</span> <Typed text="/kettle" start={2} cps={12} />
        </div>
        <div style={{ marginTop: 16, color: DIM, fontSize: 21 }}>
          EVENT&nbsp;&nbsp;&nbsp; STATE&nbsp; SOUND&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; FIRES WHEN
        </div>
        {rows.map(([ev, snd, c, when], i) =>
          f >= 22 + i * 5 ? (
            <div key={ev} style={{ fontSize: 22, color: FG }}>
              <span style={{ display: "inline-block", width: 110, color: c }}>{ev}</span>
              <span style={{ display: "inline-block", width: 80, color: GREEN }}>on</span>
              <span style={{ display: "inline-block", width: 220, color: DIM }}>{snd}</span>
              <span style={{ color: FG }}>{when}</span>
            </div>
          ) : null,
        )}
        {f >= 62 ? (
          <div style={{ marginTop: 18, color: FG }}>
            <span style={{ color: GREEN }}>&gt;</span>{" "}
            <Typed text="/kettle stop done,up" start={62} cps={14} />
          </div>
        ) : null}
      </Term>
      <Sequence from={66}>
        <Audio src={staticFile("pop.mp3")} volume={0.6} />
      </Sequence>
      <Caption event="one CLI" text="every event on/off, volume, quiet hours, your own files" />
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const s = spring({ frame: f, fps, config: { damping: 200 }, durationInFrames: 20 });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 26,
          color: BG,
          background: FG,
          padding: "18px 28px",
          lineHeight: 1.5,
          borderRadius: 10,
          opacity: s,
          transform: `translateY(${(1 - s) * 16}px)`,
        }}
      >
        <div>claude plugin marketplace add ChiHanLu/kettle</div>
        <div style={{ marginTop: 8 }}>claude plugin install kettle@kettle</div>
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 24,
          color: DIM,
          marginTop: 26,
          opacity: interpolate(f, [14, 30], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        macOS · Windows · Linux &nbsp;·&nbsp; zero dependencies &nbsp;·&nbsp; MIT
      </div>
      <div
        style={{
          fontFamily: MONO,
          fontSize: 22,
          color: BLUE,
          marginTop: 14,
          opacity: interpolate(f, [20, 36], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        github.com/ChiHanLu/kettle
      </div>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- root */

const T = { title: 80, done: 150, perm: 105, err: 110, cli: 120, outro: 95 };
const TOTAL = Object.values(T).reduce((a, b) => a + b, 0);

export const Demo: React.FC = () => {
  let at = 0;
  const next = (n: number) => {
    const from = at;
    at += n;
    return from;
  };
  return (
    <AbsoluteFill style={{ background: BG }}>
      <Sequence from={next(T.title)} durationInFrames={T.title}>
        <Title />
      </Sequence>
      <Sequence from={next(T.done)} durationInFrames={T.done}>
        <SceneDone />
      </Sequence>
      <Sequence from={next(T.perm)} durationInFrames={T.perm}>
        <ScenePermission />
      </Sequence>
      <Sequence from={next(T.err)} durationInFrames={T.err}>
        <SceneError />
      </Sequence>
      <Sequence from={next(T.cli)} durationInFrames={T.cli}>
        <SceneCli />
      </Sequence>
      <Sequence from={next(T.outro)} durationInFrames={T.outro}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};

export const MyComposition = () => (
  <Composition
    id="Demo"
    component={Demo}
    durationInFrames={TOTAL}
    fps={FPS}
    width={W}
    height={H}
  />
);
