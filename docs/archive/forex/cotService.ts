/**
 * cotService.ts — Real CFTC COT data fetcher
 *
 * Data source: CFTC Public Reporting Environment (Socrata API)
 * - No API key required
 * - Legacy Futures Only dataset (6dca-aqww): Non-commercial net positions
 * - TFF Futures Only dataset (gpe5-46if): Dealer / Asset Manager / Leveraged Money breakdown
 *
 * Published every Friday at 3:30 PM ET, reflecting Tuesday's open interest.
 * We fetch the latest 52 weekly rows to compute percentile rank.
 */

const SOCRATA_BASE = "https://publicreporting.cftc.gov/resource";
const LEGACY_DATASET = "6dca-aqww";
const TFF_DATASET = "gpe5-46if";

// ─── Contract map ─────────────────────────────────────────────────────────────
// Maps our internal pair names to CFTC contract_market_name values.
// NZD is excluded — CFTC stopped updating NZD in Legacy/TFF after 2022.
export const CFTC_FX_CONTRACTS: {
  pair: string;
  legacyName: string;
  tffName: string;
}[] = [
  { pair: "EUR/USD", legacyName: "EURO FX",         tffName: "EURO FX" },
  { pair: "GBP/USD", legacyName: "BRITISH POUND",   tffName: "BRITISH POUND" },
  { pair: "USD/JPY", legacyName: "JAPANESE YEN",    tffName: "JAPANESE YEN" },
  { pair: "USD/CHF", legacyName: "SWISS FRANC",     tffName: "SWISS FRANC" },
  { pair: "USD/CAD", legacyName: "CANADIAN DOLLAR", tffName: "CANADIAN DOLLAR" },
  { pair: "AUD/USD", legacyName: "AUSTRALIAN DOLLAR", tffName: "AUSTRALIAN DOLLAR" },
];

// ─── Types ────────────────────────────────────────────────────────────────────
export interface CftcLegacyRow {
  report_date_as_yyyy_mm_dd: string;
  noncomm_positions_long_all: string;
  noncomm_positions_short_all: string;
  open_interest_all: string;
  change_in_noncomm_long_all: string;
  change_in_noncomm_short_all: string;
  pct_of_oi_noncomm_long_all: string;
  pct_of_oi_noncomm_short_all: string;
}

export interface CftcTffRow {
  report_date_as_yyyy_mm_dd: string;
  dealer_positions_long_all: string;
  dealer_positions_short_all: string;
  asset_mgr_positions_long: string;
  asset_mgr_positions_short: string;
  lev_money_positions_long: string;
  lev_money_positions_short: string;
  open_interest_all: string;
}

export interface RealCotResult {
  pair: string;
  dataDate: string;          // ISO date of the CFTC report (Tuesday's data)
  isRealData: boolean;       // true = CFTC API, false = price proxy fallback
  // Non-commercial (speculator) positions
  noncommLong: number;
  noncommShort: number;
  netPosition: number;       // noncommLong - noncommShort (positive = net long)
  openInterest: number;
  pctOfOiLong: number;       // % of OI held long by non-commercials
  pctOfOiShort: number;
  // Week-on-week change in net position
  wowChangeLong: number;
  wowChangeShort: number;
  wowChangeNet: number;      // positive = more bullish this week
  // TFF breakdown (institutional categories)
  dealerNet: number;         // Dealer/Intermediary net (banks)
  assetMgrNet: number;       // Asset Manager net (real money, trend followers)
  levMoneyNet: number;       // Leveraged Money net (hedge funds)
  // Derived signals
  percentile52w: number;     // 0–100 rank of netPosition in last 52 weekly readings
  percentile26w: number;     // 0–100 rank in last 26 weekly readings
  crowdedLong: boolean;      // percentile52w > 80
  crowdedShort: boolean;     // percentile52w < 20
  positionTrend: "INCREASING_LONG" | "DECREASING_LONG" | "INCREASING_SHORT" | "DECREASING_SHORT" | "FLAT";
  notes: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function percentileRank(series: number[], value: number): number {
  if (!series.length) return 50;
  const below = series.filter(v => v < value).length;
  return Math.round((below / series.length) * 100);
}

function n(s: string | undefined): number {
  const v = parseFloat(s ?? "0");
  return isNaN(v) ? 0 : v;
}

async function fetchSocrataJson<T>(url: string): Promise<T[]> {
  const res = await fetch(url, {
    headers: { "Accept": "application/json" },
    signal: AbortSignal.timeout(15_000),
  });
  if (!res.ok) throw new Error(`CFTC API error ${res.status}: ${url}`);
  return res.json() as Promise<T[]>;
}

// ─── Main fetcher ─────────────────────────────────────────────────────────────
/**
 * Fetch real CFTC COT data for all 6 supported FX pairs.
 * Fetches last 52 Legacy rows + last 2 TFF rows per contract.
 * Returns one RealCotResult per pair.
 * On any per-pair failure, returns a fallback stub (isRealData: false).
 */
export async function fetchRealCotData(): Promise<RealCotResult[]> {
  const results: RealCotResult[] = [];

  for (const contract of CFTC_FX_CONTRACTS) {
    try {
      // ── Legacy: last 52 weeks (for percentile) ──────────────────────────
      const legacyUrl = [
        `${SOCRATA_BASE}/${LEGACY_DATASET}.json`,
        `?$where=contract_market_name='${encodeURIComponent(contract.legacyName)}'`,
        `&$order=report_date_as_yyyy_mm_dd DESC`,
        `&$limit=52`,
        `&$select=report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all,`,
        `open_interest_all,change_in_noncomm_long_all,change_in_noncomm_short_all,`,
        `pct_of_oi_noncomm_long_all,pct_of_oi_noncomm_short_all`,
      ].join("");

      const legacyRows = await fetchSocrataJson<CftcLegacyRow>(legacyUrl);

      if (!legacyRows.length) {
        results.push(buildFallback(contract.pair, "No CFTC data returned"));
        continue;
      }

      // Rows are newest-first; latest = index 0
      const latest = legacyRows[0];
      const prev    = legacyRows[1]; // previous week for WoW change

      const noncommLong  = n(latest.noncomm_positions_long_all);
      const noncommShort = n(latest.noncomm_positions_short_all);
      const netPosition  = noncommLong - noncommShort;
      const openInterest = n(latest.open_interest_all);
      const pctOfOiLong  = n(latest.pct_of_oi_noncomm_long_all);
      const pctOfOiShort = n(latest.pct_of_oi_noncomm_short_all);

      // WoW change: use the CFTC-provided change fields for the latest week
      const wowChangeLong  = n(latest.change_in_noncomm_long_all);
      const wowChangeShort = n(latest.change_in_noncomm_short_all);
      const wowChangeNet   = wowChangeLong - wowChangeShort;

      // 52-week net position series (newest-first → reverse for chronological)
      const netSeries52 = legacyRows.map(r => n(r.noncomm_positions_long_all) - n(r.noncomm_positions_short_all));
      const netSeries26 = netSeries52.slice(0, 26);

      const percentile52w = percentileRank(netSeries52, netPosition);
      const percentile26w = percentileRank(netSeries26, netPosition);
      const crowdedLong   = percentile52w > 80;
      const crowdedShort  = percentile52w < 20;

      // Position trend: compare this week's net to last week's net
      const prevNet = prev ? n(prev.noncomm_positions_long_all) - n(prev.noncomm_positions_short_all) : netPosition;
      const netDelta = netPosition - prevNet;
      let positionTrend: RealCotResult["positionTrend"] = "FLAT";
      if (netDelta > 5000 && netPosition > 0)  positionTrend = "INCREASING_LONG";
      else if (netDelta > 5000 && netPosition < 0) positionTrend = "DECREASING_SHORT";
      else if (netDelta < -5000 && netPosition < 0) positionTrend = "INCREASING_SHORT";
      else if (netDelta < -5000 && netPosition > 0) positionTrend = "DECREASING_LONG";

      // ── TFF: latest 2 weeks (for institutional breakdown) ───────────────
      let dealerNet = 0, assetMgrNet = 0, levMoneyNet = 0;
      try {
        const tffUrl = [
          `${SOCRATA_BASE}/${TFF_DATASET}.json`,
          `?$where=contract_market_name='${encodeURIComponent(contract.tffName)}'`,
          `&$order=report_date_as_yyyy_mm_dd DESC`,
          `&$limit=1`,
          `&$select=report_date_as_yyyy_mm_dd,dealer_positions_long_all,dealer_positions_short_all,`,
          `asset_mgr_positions_long,asset_mgr_positions_short,lev_money_positions_long,lev_money_positions_short`,
        ].join("");

        const tffRows = await fetchSocrataJson<CftcTffRow>(tffUrl);
        if (tffRows.length) {
          const t = tffRows[0];
          dealerNet   = n(t.dealer_positions_long_all)   - n(t.dealer_positions_short_all);
          assetMgrNet = n(t.asset_mgr_positions_long)    - n(t.asset_mgr_positions_short);
          levMoneyNet = n(t.lev_money_positions_long)    - n(t.lev_money_positions_short);
        }
      } catch {
        // TFF failure is non-fatal — we still have Legacy data
      }

      // ── Notes ────────────────────────────────────────────────────────────
      const netFmt = netPosition > 0
        ? `+${(netPosition / 1000).toFixed(1)}k net long`
        : `${(netPosition / 1000).toFixed(1)}k net short`;

      const wowFmt = wowChangeNet > 0
        ? `+${(wowChangeNet / 1000).toFixed(1)}k WoW`
        : `${(wowChangeNet / 1000).toFixed(1)}k WoW`;

      const notes = crowdedLong
        ? `${netFmt} (${wowFmt}) — ${percentile52w}th pctile: CROWDED LONG, contrarian risk`
        : crowdedShort
        ? `${netFmt} (${wowFmt}) — ${percentile52w}th pctile: CROWDED SHORT, squeeze risk`
        : `${netFmt} (${wowFmt}) — ${percentile52w}th pctile, no extreme crowding`;

      results.push({
        pair: contract.pair,
        dataDate: latest.report_date_as_yyyy_mm_dd.slice(0, 10),
        isRealData: true,
        noncommLong, noncommShort, netPosition, openInterest,
        pctOfOiLong, pctOfOiShort,
        wowChangeLong, wowChangeShort, wowChangeNet,
        dealerNet, assetMgrNet, levMoneyNet,
        percentile52w, percentile26w,
        crowdedLong, crowdedShort, positionTrend, notes,
      });

    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      results.push(buildFallback(contract.pair, `CFTC fetch failed: ${msg}`));
    }
  }

  // NZD/USD — CFTC data unavailable; always use stub
  results.push(buildFallback("NZD/USD", "CFTC data not available for NZD/USD — using price proxy"));

  return results;
}

function buildFallback(pair: string, reason: string): RealCotResult {
  return {
    pair,
    dataDate: new Date().toISOString().slice(0, 10),
    isRealData: false,
    noncommLong: 0, noncommShort: 0, netPosition: 0, openInterest: 0,
    pctOfOiLong: 0, pctOfOiShort: 0,
    wowChangeLong: 0, wowChangeShort: 0, wowChangeNet: 0,
    dealerNet: 0, assetMgrNet: 0, levMoneyNet: 0,
    percentile52w: 50, percentile26w: 50,
    crowdedLong: false, crowdedShort: false,
    positionTrend: "FLAT",
    notes: reason,
  };
}

/**
 * Summarise COT positioning as a factual context string.
 *
 * COT positioning is genuinely ambiguous: crowded positioning can mean
 * either a squeeze is coming (contrarian) OR smart money is positioned
 * for a reason (trend-following). This function surfaces the raw fact
 * without picking a side. It is NOT a directional vote.
 *
 * Returns a human-readable string for use in setup card reasons and UI.
 * The _pairDirection parameter is accepted for API compatibility but
 * is intentionally not used in the output — COT does not vote.
 */
export function cotMacroSignal(cot: RealCotResult, _pairDirection: "LONG" | "SHORT"): string {
  if (!cot.isRealData) return "COT: proxy data only — context not available";

  const netK = (cot.netPosition / 1000).toFixed(1);
  const sign = cot.netPosition >= 0 ? "+" : "";
  const pctile = cot.percentile52w != null ? ` (${cot.percentile52w}th pct 52w)` : "";

  if (cot.crowdedLong) {
    return `ℹ CFTC: Speculators net long ${sign}${netK}k${pctile} — crowded long. Argues both ways: squeeze risk vs institutional conviction.`;
  }
  if (cot.crowdedShort) {
    return `ℹ CFTC: Speculators net short ${netK}k${pctile} — crowded short. Argues both ways: squeeze risk vs institutional conviction.`;
  }
  return `ℹ CFTC: Speculators net ${sign}${netK}k${pctile} — no extreme crowding. Context only.`;
}
