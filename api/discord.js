const fetch = require('node-fetch');

const DISCORD_ID = '1147221423815938179';

// ── Status colours ────────────────────────────────────────────────────────────
const STATUS_COLOR = {
  online:  '#23d18b',
  idle:    '#f0b232',
  dnd:     '#f04747',
  offline: '#747f8d',
};
const STATUS_LABEL = {
  online:  'Online',
  idle:    'Idle',
  dnd:     'Do Not Disturb',
  offline: 'Offline',
};

// ── Discord public_flags → badge SVG paths (inline) ──────────────────────────
// We use simple emoji-style text badges as SVG since external images can't load
// in GitHub's CSP. Each badge is a small pill rendered inline.
const FLAG_BADGES = [
  { flag: 1,        label: 'Discord Staff',            color: '#5865F2' },
  { flag: 2,        label: 'Partnered Server Owner',   color: '#5865F2' },
  { flag: 4,        label: 'HypeSquad Events',         color: '#f47b67' },
  { flag: 8,        label: 'Bug Hunter Lvl 1',         color: '#f47b67' },
  { flag: 64,       label: 'HypeSquad Bravery',        color: '#9c84ef' },
  { flag: 128,      label: 'HypeSquad Brilliance',     color: '#f47b67' },
  { flag: 256,      label: 'HypeSquad Balance',        color: '#43b581' },
  { flag: 512,      label: 'Early Supporter',          color: '#f47b67' },
  { flag: 16384,    label: 'Bug Hunter Lvl 2',         color: '#f47b67' },
  { flag: 131072,   label: 'Verified Bot Dev',         color: '#5865F2' },
  { flag: 262144,   label: 'Moderator Alumni',         color: '#5865F2' },
  { flag: 4194304,  label: 'Active Developer',         color: '#43b581' },
];

// Activity type labels
const ACTIVITY_TYPE = ['Playing', 'Streaming', 'Listening', 'Watching', 'Custom', 'Competing'];

// ── Fetch avatar/image as base64 data URI ─────────────────────────────────────
async function toDataURI(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const buf = await res.buffer();
    const ct  = res.headers.get('content-type') || 'image/png';
    return `data:${ct};base64,${buf.toString('base64')}`;
  } catch {
    return null;
  }
}

// ── Escape XML special chars ──────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Truncate long strings ─────────────────────────────────────────────────────
function trunc(s, n) {
  s = String(s || '');
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

// ── Duration since timestamp ──────────────────────────────────────────────────
function elapsed(ms) {
  const s = Math.floor((Date.now() - ms) / 1000);
  if (s < 60)  return `${s}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m ${s % 60}s`;
  return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
}

// ── Build badge pills SVG ─────────────────────────────────────────────────────
function buildBadges(publicFlags) {
  const earned = FLAG_BADGES.filter(b => (publicFlags & b.flag) !== 0);
  if (!earned.length) return { svg: '', height: 0 };

  let x = 0;
  const pills = earned.map(b => {
    const w = b.label.length * 7.5 + 16;
    const pill = `
      <rect x="${x}" y="0" width="${w}" height="22" rx="11" fill="${b.color}" opacity="0.85"/>
      <text x="${x + w / 2}" y="15" font-family="'Segoe UI',Arial,sans-serif" font-size="11"
            font-weight="600" fill="#fff" text-anchor="middle">${esc(b.label)}</text>`;
    x += w + 6;
    return pill;
  });

  return {
    svg: `<g>${pills.join('')}</g>`,
    height: 28,
    totalWidth: x,
  };
}

// ── Build one activity block ──────────────────────────────────────────────────
async function buildActivity(act, yStart) {
  const type    = act.type;
  const name    = act.name || '';
  const details = act.details || '';
  const state   = act.state || '';
  const emoji   = act.emoji ? act.emoji.name || '' : '';
  const since   = act.created_at ? elapsed(act.created_at) : '';

  // Fetch small icon if present (application_id → Discord CDN)
  let iconURI = null;
  if (act.assets && act.assets.large_image) {
    let imgUrl = act.assets.large_image;
    if (imgUrl.startsWith('mp:external/')) {
      // External image (e.g. Spotify album art)
      imgUrl = 'https://media.discordapp.net/' + imgUrl.replace(/^mp:/, '');
    } else if (act.application_id) {
      imgUrl = `https://cdn.discordapp.com/app-assets/${act.application_id}/${imgUrl}.png`;
    }
    iconURI = await toDataURI(imgUrl);
  }

  // Small overlay icon
  let smallIconURI = null;
  if (act.assets && act.assets.small_image && act.application_id) {
    const si = act.assets.small_image;
    const siUrl = `https://cdn.discordapp.com/app-assets/${act.application_id}/${si}.png`;
    smallIconURI = await toDataURI(siUrl);
  }

  const iconSize = 50;
  const textX    = iconURI ? 78 : 10;
  let lines = [];

  if (type === 4) {
    // Custom status
    lines.push({ text: `${emoji} ${state}`.trim(), size: 13, color: '#dcddde', bold: false });
  } else {
    const typeLabel = ACTIVITY_TYPE[type] || 'Activity';
    lines.push({ text: `${typeLabel} ${name}`, size: 13, color: '#b9bbbe', bold: false });
    if (details) lines.push({ text: trunc(details, 48), size: 13, color: '#dcddde', bold: true });
    if (state)   lines.push({ text: trunc(state, 48),   size: 12, color: '#b9bbbe', bold: false });
    if (since)   lines.push({ text: `${since} elapsed`, size: 11, color: '#72767d', bold: false });
  }

  const blockH = Math.max(iconURI ? iconSize + 10 : 0, lines.length * 18 + 10);

  let svg = `\n  <!-- activity block -->\n  <g transform="translate(12, ${yStart})">`;

  // Icon
  if (iconURI) {
    svg += `\n    <image href="${iconURI}" x="0" y="0" width="${iconSize}" height="${iconSize}" clip-path="url(#roundIcon)"/>`;
    if (smallIconURI) {
      svg += `\n    <image href="${smallIconURI}" x="${iconSize - 16}" y="${iconSize - 16}" width="18" height="18" clip-path="url(#roundSmall)"/>`;
    }
  }

  // Text lines
  lines.forEach((l, i) => {
    svg += `\n    <text x="${textX}" y="${14 + i * 18}" font-family="'Segoe UI',Arial,sans-serif"
      font-size="${l.size}" font-weight="${l.bold ? 700 : 400}" fill="${l.color}">${esc(l.text)}</text>`;
  });

  svg += `\n  </g>`;
  return { svg, height: blockH + 8 };
}

// ── Main SVG builder ──────────────────────────────────────────────────────────
async function buildCard(data) {
  const user        = data.discord_user;
  const status      = data.discord_status || 'offline';
  const activities  = data.activities || [];
  const spotify     = data.spotify;
  const listeningSp = data.listening_to_spotify;

  // Avatar
  const avatarUrl  = `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=128`;
  const avatarData = await toDataURI(avatarUrl);

  // Decoration overlay
  let decoData = null;
  if (user.avatar_decoration_data) {
    const decoUrl = `https://cdn.discordapp.com/avatar-decoration-presets/${user.avatar_decoration_data.asset}.png?size=128&passthrough=true`;
    decoData = await toDataURI(decoUrl);
  }

  // Badges
  const { svg: badgeSVG, height: badgeH } = buildBadges(user.public_flags || 0);

  // Platform dots
  const platforms = [];
  if (data.active_on_discord_desktop) platforms.push('Desktop');
  if (data.active_on_discord_mobile)  platforms.push('Mobile');
  if (data.active_on_discord_web)     platforms.push('Web');

  // Build activity blocks
  let actSVG  = '';
  let actH    = 0;
  const nonCustom = activities.filter(a => a.type !== 4);
  const customAct = activities.find(a => a.type === 4);

  for (const act of nonCustom) {
    const { svg, height } = await buildActivity(act, actH);
    actSVG += svg;
    actH   += height;
  }

  // Spotify block
  let spotifySVG = '';
  let spotifyH   = 0;
  if (listeningSp && spotify) {
    const albumData = spotify.album_art_url ? await toDataURI(spotify.album_art_url) : null;
    const elapsed_ms = spotify.timestamps
      ? Math.min(Date.now() - spotify.timestamps.start, spotify.timestamps.end - spotify.timestamps.start)
      : 0;
    const total_ms = spotify.timestamps
      ? spotify.timestamps.end - spotify.timestamps.start
      : 0;
    const pct = total_ms > 0 ? Math.min(elapsed_ms / total_ms, 1) : 0;
    const barW = 260;

    spotifySVG = `
  <!-- Spotify block -->
  <g transform="translate(12, ${actH})">
    ${albumData ? `<image href="${albumData}" x="0" y="0" width="50" height="50" clip-path="url(#roundIcon)"/>` : ''}
    <text x="60" y="14" font-family="'Segoe UI',Arial,sans-serif" font-size="11" fill="#1DB954" font-weight="700">🎵 LISTENING TO SPOTIFY</text>
    <text x="60" y="30" font-family="'Segoe UI',Arial,sans-serif" font-size="13" fill="#fff" font-weight="700">${esc(trunc(spotify.song || '', 38))}</text>
    <text x="60" y="46" font-family="'Segoe UI',Arial,sans-serif" font-size="12" fill="#b9bbbe">by ${esc(trunc(spotify.artist || '', 38))}</text>
    <rect x="60" y="54" width="${barW}" height="3" rx="2" fill="#4f545c"/>
    <rect x="60" y="54" width="${Math.round(barW * pct)}" height="3" rx="2" fill="#1DB954"/>
  </g>`;
    spotifyH = 72;
  }

  // Custom status row
  let customSVG = '';
  let customH   = 0;
  if (customAct) {
    const emoji = customAct.emoji ? customAct.emoji.name || '' : '';
    const state = customAct.state || '';
    const text  = `${emoji} ${state}`.trim();
    if (text) {
      customSVG = `
  <text x="84" y="82" font-family="'Segoe UI',Arial,sans-serif" font-size="12" fill="#b9bbbe">${esc(trunc(text, 42))}</text>`;
      customH = 0; // inline under username
    }
  }

  // Platform indicator text
  const platformText = platforms.length ? `on ${platforms.join(' & ')}` : '';

  // Total height calculation
  const headerH  = 110;
  const badgePad = badgeH > 0 ? badgeH + 8 : 0;
  const dividerH = 8;
  const totalActH = actH + spotifyH;
  const hasActs  = totalActH > 0;
  const actSection = hasActs ? totalActH + 16 : 0;

  const W = 380;
  const H = headerH + badgePad + dividerH + actSection + 16;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <clipPath id="avatarClip">
      <circle cx="40" cy="40" r="38"/>
    </clipPath>
    <clipPath id="roundIcon">
      <rect width="50" height="50" rx="10"/>
    </clipPath>
    <clipPath id="roundSmall">
      <circle cx="9" cy="9" r="9"/>
    </clipPath>
  </defs>

  <!-- Card background -->
  <rect width="${W}" height="${H}" rx="16" fill="#010102"/>

  <!-- Avatar -->
  ${avatarData
    ? `<image href="${avatarData}" x="12" y="12" width="76" height="76" clip-path="url(#avatarClip)"/>`
    : `<circle cx="50" cy="50" r="38" fill="#5865F2"/>`
  }

  <!-- Avatar decoration overlay -->
  ${decoData ? `<image href="${decoData}" x="4" y="4" width="92" height="92"/>` : ''}

  <!-- Status dot -->
  <circle cx="80" cy="80" r="10" fill="#1e1f22"/>
  <circle cx="80" cy="80" r="7" fill="${STATUS_COLOR[status] || STATUS_COLOR.offline}"/>

  <!-- Display name -->
  <text x="100" y="36" font-family="'Segoe UI',Arial,sans-serif" font-size="17"
        font-weight="700" fill="#fff">${esc(user.display_name || user.global_name || user.username)}</text>

  <!-- Username -->
  <text x="100" y="55" font-family="'Segoe UI',Arial,sans-serif" font-size="12" fill="#b9bbbe">@${esc(user.username)}</text>

  <!-- Status label + platform -->
  <text x="100" y="72" font-family="'Segoe UI',Arial,sans-serif" font-size="12"
        fill="${STATUS_COLOR[status] || STATUS_COLOR.offline}" font-weight="600">${esc(STATUS_LABEL[status] || status)}<tspan fill="#72767d" font-weight="400"> ${esc(platformText)}</tspan></text>

  <!-- Custom status -->
  ${customSVG}

  <!-- Divider -->
  <line x1="12" y1="96" x2="${W - 12}" y2="96" stroke="#3f4147" stroke-width="1"/>

  <!-- Badges -->
  ${badgeH > 0 ? `<g transform="translate(12, 104)">${badgeSVG}</g>` : ''}

  <!-- Activities + Spotify -->
  ${hasActs ? `
  <line x1="12" y1="${headerH + badgePad}" x2="${W - 12}" y2="${headerH + badgePad}" stroke="#3f4147" stroke-width="1"/>
  <g transform="translate(0, ${headerH + badgePad + 8})">
    ${actSVG}
    ${spotifySVG}
  </g>` : ''}

</svg>`;
}

// ── Vercel handler ────────────────────────────────────────────────────────────
module.exports = async (req, res) => {
  try {
    const apiRes = await fetch(`https://api.lanyard.rest/v1/users/${DISCORD_ID}`, {
      headers: process.env.DC ? { Authorization: process.env.DC } : {},
    });

    if (!apiRes.ok) throw new Error(`Lanyard ${apiRes.status}`);
    const json = await apiRes.json();
    if (!json.success) throw new Error('Lanyard success=false');

    const svg = await buildCard(json.data);

    res.setHeader('Content-Type', 'image/svg+xml');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).send(svg);
  } catch (err) {
    // Fallback error card
    res.setHeader('Content-Type', 'image/svg+xml');
    res.setHeader('Cache-Control', 'no-cache');
    res.status(200).send(`<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="380" height="60" viewBox="0 0 380 60">
  <rect width="380" height="60" rx="8" fill="#1e1f22"/>
  <text x="16" y="36" font-family="sans-serif" font-size="13" fill="#f04747">Discord presence unavailable: ${esc(err.message)}</text>
</svg>`);
  }
};
