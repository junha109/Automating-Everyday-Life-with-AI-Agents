/* 오늘의 GitHub 한국어판 — 정적 페이지. data/ 아래 JSON만 읽는다 (서버 없음).
   하루 보기: 그날 파일 하나를 그대로 보여준다.
   일주일 보기: 월~일 사이 날짜 파일을 모두 읽어 코드로 합친다 (AI 호출 없음). */
(() => {
  "use strict";

  const S = {
    index: null,
    tab: "trending",
    mode: "day",        // day | week
    date: null,         // 하루 보기의 날짜 / 일주일 보기에서는 그 주 안의 아무 날짜
    view: null,         // 화면에 그릴 데이터 (하루든 일주일이든 같은 모양)
    category: null,
    query: "",
    lang: "ko",
    flipped: new Set(),
    chart: null,
    cache: new Map(),
  };
  const $ = (id) => document.getElementById(id);
  const WEEK = ["일", "월", "화", "수", "목", "금", "토"];

  // 외부(README 등)에서 온 텍스트는 반드시 이스케이프해서 넣는다
  const h = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => (n ?? 0).toLocaleString("ko-KR");
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  // ---------- 날짜 ----------
  const parse = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
  const iso = (dt) => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
  const addDays = (s, n) => { const d = parse(s); d.setDate(d.getDate() + n); return iso(d); };
  const monday = (s) => { const d = parse(s); return addDays(s, -((d.getDay() + 6) % 7)); };
  function fmtDate(s, style = "long") {
    const d = parse(s), w = WEEK[d.getDay()];
    if (style === "long") return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 ${w}요일`;
    if (style === "md") return `${d.getMonth() + 1}/${d.getDate()}`;
    return `${d.getMonth() + 1}/${d.getDate()}(${w})`;
  }
  const weekLabel = (mon) => `${fmtDate(mon, "mdw")} ~ ${fmtDate(addDays(mon, 6), "mdw")}`;

  // ---------- 상태 ↔ 주소창: #탭/날짜[/week] ----------
  function readHash() {
    const [tab, date, mode] = location.hash.replace(/^#/, "").split("/");
    if (tab === "trending" || tab === "interest") S.tab = tab;
    if (date && /^\d{4}-\d{2}-\d{2}$/.test(date)) S.date = date;
    S.mode = mode === "week" ? "week" : "day";
  }
  const writeHash = () => history.replaceState(null, "", `#${S.tab}/${S.date}${S.mode === "week" ? "/week" : ""}`);

  // ---------- 데이터 ----------
  async function getJSON(path) {
    if (S.cache.has(path)) return S.cache.get(path);
    const r = await fetch(path, { cache: "no-cache" });
    if (!r.ok) throw new Error(`${path} (${r.status})`);
    const j = await r.json();
    S.cache.set(path, j);
    return j;
  }
  const tabInfo = () => S.index.tabs[S.tab] || { dates: [], counts: {}, status: {} };
  const categories = () => S.index.categories[S.tab];
  const okDates = () => tabInfo().dates.filter((d) => tabInfo().status[d] === "ok");
  const weekDates = (mon) => okDates().filter((d) => d >= mon && d <= addDays(mon, 6));
  const isRel = (r) => S.tab !== "interest" || r.ai.relevant;
  function countBy(repos) {
    const c = Object.fromEntries(categories().map((k) => [k, 0]));
    repos.filter(isRel).forEach((r) => { c[r.ai.category] = (c[r.ai.category] || 0) + 1; });
    return c;
  }

  async function loadDayView() {
    const dates = tabInfo().dates;
    if (!dates.length) return null;
    if (!dates.includes(S.date)) S.date = dates[dates.length - 1];
    const day = await getJSON(`data/${S.tab}/${S.date}.json`);
    const rel = day.repos.filter(isRel);
    const relRank = new Map(rel.map((r, i) => [r.full_name, i + 1]));
    return {
      kind: "day", status: day.status, model: day.model, prompt: day.prompt_version || "v1",
      candidates: day.candidates, compared_with: day.compared_with,
      counts: day.category_counts,
      // 관심 분야는 관련 있다고 판단된 레포끼리 순위를 다시 매긴다
      repos: day.repos.map((r) => ({ ...r, shownRank: S.tab === "interest" && r.ai.relevant ? relRank.get(r.full_name) : r.rank })),
    };
  }

  async function aggregateWeek(mon) {
    const dates = weekDates(mon);
    const days = await Promise.all(dates.map((d) => getJSON(`data/${S.tab}/${d}.json`)));
    const by = new Map();
    days.forEach((day) => day.repos.forEach((r) => {
      const a = by.get(r.full_name) || { days: [], stars: 0, cats: new Set(), latest: null, bestRank: Infinity };
      a.days.push(day.date);
      a.stars += (S.tab === "interest" ? r.stars_delta : r.stars_today) || 0;
      a.cats.add(r.ai.category);
      a.bestRank = Math.min(a.bestRank, r.rank);
      a.latest = r;                       // 날짜 오름차순이므로 마지막이 가장 최근
      by.set(r.full_name, a);
    }));
    const repos = [...by.values()].map((a) => ({
      ...a.latest,
      week: { days: a.days.length, total: dates.length, stars: a.stars, cats: [...a.cats], bestRank: a.bestRank },
    }));
    // 전체 Trending: 며칠 등장했나 → 그 주 받은 스타 합계 / 관심 분야: 그 주 스타 증가 합계
    repos.sort(S.tab === "interest"
      ? (x, y) => y.week.stars - x.week.stars
      : (x, y) => y.week.days - x.week.days || y.week.stars - x.week.stars);
    let n = 0;
    repos.forEach((r) => { r.shownRank = isRel(r) ? ++n : "–"; });
    const last = days[days.length - 1];
    return { dates, repos, counts: countBy(repos), model: last?.model, prompt: last?.prompt_version || "v1",
      candidates: last?.candidates };
  }

  async function loadWeekView() {
    const all = okDates();
    if (!S.date) S.date = tabInfo().dates[tabInfo().dates.length - 1];
    if (!S.date) return null;
    const mon = monday(S.date);
    const w = await aggregateWeek(mon);
    // 지난주와 비교 (지난주 데이터가 있을 때만)
    const prevMon = addDays(mon, -7);
    const prev = weekDates(prevMon).length ? await aggregateWeek(prevMon) : null;
    return {
      kind: "week", mon, status: w.dates.length ? "ok" : "empty", ...w,
      prevCounts: prev ? prev.counts : null,
      isLatestWeek: all.length ? monday(all[all.length - 1]) === mon : true,
    };
  }

  // ---------- 렌더 ----------
  function renderHeader() {
    document.querySelectorAll(".tab").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.tab === S.tab)));
    document.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === S.mode)));
    const sel = $("date-select");
    const dates = tabInfo().dates;
    if (S.mode === "day") {
      sel.innerHTML = [...dates].reverse().map((d) => `<option value="${d}">${fmtDate(d)}</option>`).join("");
      sel.value = S.date || "";
    } else {
      const mons = [...new Set(dates.map(monday))].reverse();
      sel.innerHTML = mons.map((m) => `<option value="${m}">${weekLabel(m)}</option>`).join("");
      sel.value = S.date ? monday(S.date) : "";
    }
    sel.disabled = dates.length === 0;
  }

  function biggestChange(counts, prev) {
    let best = null;
    for (const k of Object.keys(counts)) {
      const d = counts[k] - (prev[k] || 0);
      if (d !== 0 && (!best || Math.abs(d) > Math.abs(best.d))) best = { k, d };
    }
    return best;
  }

  function renderHero() {
    const v = S.view, line = $("hero-line"), note = $("hero-note");
    if (!v) {
      $("hero-date").textContent = "";
      line.textContent = "아직 수집된 데이터가 없어요";
      note.textContent = "매일 아침 자동으로 수집되면 여기에 표시돼요.";
      return;
    }
    const counts = v.counts;
    const max = Math.max(0, ...Object.values(counts));
    const tops = Object.keys(counts).filter((k) => counts[k] === max && max > 0);
    const topText = tops.length === 1 ? tops[0] : tops.join(", ");

    if (v.kind === "week") {
      $("hero-date").textContent = `${weekLabel(v.mon)} · ${S.tab === "interest" ? `순위를 낸 날 ${v.dates.length}일` : `${v.dates.length}일치 수집`}`;
      const when = v.isLatestWeek ? "이번 주" : "이 주";
      if (v.status === "empty") {
        line.textContent = S.tab === "interest" ? `${when}는 아직 순위가 나온 날이 없어요` : `${when}에 수집된 데이터가 없어요`;
        note.textContent = S.tab === "interest" ? "관심 분야는 첫 수집 다음 날부터 순위가 나와요." : "";
        return;
      }
      const rel = v.repos.filter(isRel);
      if (S.tab === "trending") {
        line.textContent = `${when} Trending에 오른 레포 ${rel.length}개, 가장 많은 분야는 ${topText}`;
      } else {
        const best = rel[0];
        line.textContent = best
          ? `${when} 관심 분야 ${rel.length}개, 스타가 가장 많이 늘어난 건 ${best.full_name.split("/")[1]}`
          : `${when}에는 관심 분야로 판단된 레포가 없어요`;
      }
      const ch = v.prevCounts && biggestChange(counts, v.prevCounts);
      note.textContent = v.prevCounts
        ? (ch ? `지난주보다 ${ch.k} 분야 레포가 ${Math.abs(ch.d)}개 ${ch.d > 0 ? "늘었어요" : "줄었어요"}. ` : "지난주와 분야별 개수가 같아요. ")
          + "같은 레포가 여러 날 올라와도 한 번만 셌어요."
        : "같은 레포가 여러 날 올라와도 한 번만 셌어요. 지난주 기록이 생기면 지난주와 비교해 보여줘요.";
      return;
    }

    $("hero-date").textContent = fmtDate(S.date);
    if (S.tab === "interest" && v.status === "baseline") {
      line.textContent = `관심 분야 레포 ${num(v.candidates)}개를 지켜보기 시작했어요`;
      note.textContent = "관심 분야 순위는 전날 대비 스타 증가량으로 매겨요. 오늘은 첫 수집일이라 비교할 기록이 없어서, 다음 수집부터 순위가 나와요.";
      return;
    }
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    if (S.tab === "trending") {
      line.textContent = tops.length === 1 ? `Trending ${total}개 중 ${max}개가 ${topText}`
        : `Trending ${total}개 중 ${topText}가 각각 ${max}개`;
    } else {
      const best = v.repos.filter(isRel)[0];
      line.textContent = best
        ? `관심 분야 ${total}개, 하루 새 스타가 가장 많이 늘어난 건 ${best.full_name.split("/")[1]}`
        : "오늘은 관심 분야로 판단된 레포가 없어요";
    }
    const prevDates = okDates().filter((d) => d < S.date);
    const prev = prevDates.length ? tabInfo().counts[prevDates[prevDates.length - 1]] : null;
    const ch = prev && biggestChange(counts, prev);
    note.textContent = prev
      ? (ch ? `직전 수집보다 ${ch.k} 분야가 ${Math.abs(ch.d)}개 ${ch.d > 0 ? "늘었어요" : "줄었어요"}.` : "직전 수집과 분야별 개수가 같아요.")
      : S.tab === "interest"
        ? "직전 수집과 비교한 스타 증가량 기준이에요. 관련 없다고 판단한 레포는 맨 아래에 따로 모아뒀어요."
        : "분야별 개수와 추이는 기록이 쌓일수록 비교할 수 있어요.";
  }

  function renderBar() {
    const counts = S.view ? S.view.counts : {};
    const cats = categories();
    const order = [...cats].sort((a, b) => (counts[b] || 0) - (counts[a] || 0) || cats.indexOf(a) - cats.indexOf(b));
    const values = order.map((c) => counts[c] || 0);
    $("bar-title").textContent = S.mode === "week" ? "분야별 개수 (이 주, 중복 제외)" : "분야별 개수";
    $("bar-table").innerHTML = "<caption>분야별 레포 개수</caption><tr><th>분야</th><th>개수</th></tr>" +
      order.map((c, i) => `<tr><td>${h(c)}</td><td>${values[i]}</td></tr>`).join("");

    const canvas = $("bar-chart");
    if (typeof Chart === "undefined" || !canvas) {
      const wrap = document.querySelector(".bar-wrap");
      const max = Math.max(1, ...values);
      wrap.innerHTML = order.map((c, i) => `
        <div style="display:grid;grid-template-columns:9.5rem 1fr 2rem;gap:8px;align-items:center;font-size:.8125rem">
          <span style="color:var(--ink-2)">${h(c)}</span>
          <span style="height:12px;border-radius:0 4px 4px 0;background:var(--accent);width:${(values[i] / max) * 100}%"></span>
          <b>${values[i]}</b></div>`).join("");
      wrap.style.height = "auto";
      return;
    }
    const accent = cssVar("--accent"), dim = cssVar("--bar-dim");
    const ink2 = cssVar("--ink-2"), line = cssVar("--line"), font = cssVar("--font");
    const data = {
      labels: order,
      datasets: [{ data: values, backgroundColor: order.map((c) => (!S.category || S.category === c ? accent : dim)),
        borderRadius: { topRight: 4, bottomRight: 4 }, borderSkipped: "left", barThickness: 14 }],
    };
    if (S.chart) {
      S.chart.data = data;
      S.chart.options.scales.x.grid.color = line;
      S.chart.options.scales.x.ticks.color = ink2;
      S.chart.options.scales.y.ticks.color = ink2;
      S.chart.update();
      return;
    }
    S.chart = new Chart(canvas, {
      type: "bar", data,
      options: {
        indexAxis: "y", maintainAspectRatio: false, animation: { duration: 250 },
        plugins: { legend: { display: false },
          tooltip: { callbacks: { label: (c) => ` ${c.raw}개` }, displayColors: false } },
        scales: {
          x: { beginAtZero: true, ticks: { precision: 0, color: ink2, font: { family: font } },
               grid: { color: line }, border: { display: false } },
          y: { ticks: { color: ink2, font: { family: font, size: 12 } }, grid: { display: false }, border: { display: false } },
        },
        onClick: (_e, els) => {
          if (!els.length) return;
          const c = S.chart.data.labels[els[0].index];
          setCategory(S.category === c ? null : c);
        },
        onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
      },
    });
  }

  function renderMultiples() {
    const info = tabInfo(), cats = categories();
    let slots, hint;
    if (S.mode === "week" && S.view) {
      // 그 주의 월~일 7칸 (수집 안 된 날은 빈 칸)
      slots = [...Array(7)].map((_, i) => addDays(S.view.mon, i));
      hint = "그 주 월~일, 모든 칸이 같은 눈금 (빈 칸은 수집 안 된 날)";
    } else {
      slots = okDates().filter((d) => d <= S.date).slice(-14);
      hint = slots.length < 2 ? "기록이 이틀 이상 쌓이면 비교할 수 있어요" : `최근 ${slots.length}회 수집, 모든 칸이 같은 눈금`;
    }
    const has = (d) => info.status[d] === "ok";
    const val = (d, c) => (has(d) ? info.counts[d][c] || 0 : null);
    const max = Math.max(1, ...slots.flatMap((d) => cats.map((c) => val(d, c) || 0)));
    $("trend-hint").textContent = hint;
    $("multiples").innerHTML = cats.map((c) => {
      const shown = S.view ? (S.view.counts[c] || 0) : 0;
      const bars = slots.map((d) => {
        const v = val(d, c);
        if (v === null) return `<span class="mult__bar mult__bar--none" title="${fmtDate(d, "mdw")}: 수집 없음"></span>`;
        return v === 0
          ? `<span class="mult__bar mult__bar--zero" title="${fmtDate(d, "mdw")}: 0개"></span>`
          : `<span class="mult__bar" style="height:${(v / max) * 100}%" title="${fmtDate(d, "mdw")}: ${v}개"></span>`;
      }).join("");
      const dimmed = S.category && S.category !== c ? " mult--dim" : "";
      return `<div class="mult${dimmed}" role="img" aria-label="${h(c)} 추이, ${shown}개">
        <div class="mult__head"><span class="mult__name">${h(c)}</span><span class="mult__val">${shown}</span></div>
        <div class="mult__plot">${bars}</div></div>`;
    }).join("");
  }

  function filtered() {
    if (!S.view) return { shown: [], excluded: [], relevantAll: [] };
    const q = S.query.trim().toLowerCase();
    const match = (r) => !q || [r.full_name, r.description, r.ai.description_ko, r.ai.summary_ko,
      (r.topics || []).join(" ")].join(" ").toLowerCase().includes(q);
    const pool = S.view.repos.filter(match);
    return {
      shown: pool.filter((r) => isRel(r) && (!S.category || r.ai.category === S.category)),
      excluded: pool.filter((r) => !isRel(r)),
      relevantAll: S.view.repos.filter(isRel),
    };
  }

  function renderChips() {
    const { relevantAll } = filtered();
    const n = (c) => relevantAll.filter((r) => r.ai.category === c).length;
    $("chips").innerHTML =
      `<button type="button" class="chip" data-cat="" aria-pressed="${!S.category}">전체<span class="chip__n">${relevantAll.length}</span></button>` +
      categories().map((c) => `<button type="button" class="chip" data-cat="${h(c)}" aria-pressed="${S.category === c}"
        ${n(c) === 0 && S.category !== c ? "disabled" : ""}>${h(c)}<span class="chip__n">${n(c)}</span></button>`).join("");
  }

  // 정리된 README 평문: 빈 줄로 나뉜 블록. "# "는 제목, "• "는 목록
  function excerptHTML(text) {
    const out = [];
    let list = [];
    const flush = () => { if (list.length) { out.push(`<ul>${list.join("")}</ul>`); list = []; } };
    for (const b of String(text).split(/\n{2,}/)) {
      const t = b.trim();
      if (!t) continue;
      if (t.startsWith("• ")) { list.push(`<li>${h(t.slice(2))}</li>`); continue; }
      flush();
      out.push(t.startsWith("# ") ? `<p class="orig-h">${h(t.slice(2))}</p>` : `<p>${h(t)}</p>`);
    }
    flush();
    return out.join("");
  }

  function repoHTML(r, opts = {}) {
    const [owner, name] = r.full_name.split("/");
    const showOrig = (S.lang === "orig") !== S.flipped.has(r.full_name);
    const tags = [`<span class="tag tag--cat">${h(r.ai.category)}</span>`];
    if (r.language) tags.push(`<span class="tag">${h(r.language)}</span>`);

    let stars;
    if (r.week) {
      tags.push(`<span class="tag tag--streak">${r.week.total}일 중 ${r.week.days}일 등장</span>`);
      if (r.week.cats.length > 1)
        tags.push(`<span class="tag tag--new" title="AI 분류가 날짜마다 달랐어요">분류 변동: ${r.week.cats.map(h).join(" / ")}</span>`);
      stars = S.tab === "interest"
        ? `★ <b>+${num(r.week.stars)}</b> 이 주 합계 · 총 ${num(r.stars)}`
        : `★ <b>+${num(r.week.stars)}</b> 등장한 날 합계 · 최고 ${r.week.bestRank}위`;
    } else {
      const multiDay = tabInfo().dates.some((d) => d < S.date);
      if (r.streak >= 2) tags.push(`<span class="tag tag--streak">${r.streak}일 연속 Trending</span>`);
      if (r.is_new && multiDay) tags.push(`<span class="tag tag--new">처음 등장</span>`);
      stars = S.tab === "interest"
        ? `★ <b>+${num(r.stars_delta)}</b> 직전 대비 · 총 ${num(r.stars)}`
        : `★ <b>+${num(r.stars_today)}</b> 오늘 · 총 ${num(r.stars)}`;
    }

    const body = showOrig
      ? `<p class="repo__label">설명 (원문)</p>
        <p class="repo__desc" lang="en">${r.description ? h(r.description) : '<span style="color:var(--muted)">설명 없음</span>'}</p>
        <p class="repo__label">README 앞부분</p>
        ${r.readme_excerpt ? `<div class="repo__orig" lang="en">${excerptHTML(r.readme_excerpt)}</div>` : '<p class="repo__summary">README 없음</p>'}`
      : `${r.ai.description_ko ? `<p class="repo__desc">${h(r.ai.description_ko)}</p>` : ""}
        <p class="repo__summary">${h(r.ai.summary_ko) || "요약을 만들지 못했어요."}</p>`;

    const warns = (r.warnings || []).length
      ? `<div class="warn" role="note"><span class="warn__icon" aria-hidden="true">!</span>
           <span><strong>근거 부족</strong> ${r.warnings.map(h).join(", ")}</span></div>` : "";
    const why = [];
    if (opts.excluded && r.ai.relevance_reason) why.push(`제외 이유: ${h(r.ai.relevance_reason)}`);
    if (r.ai.category_reason) why.push(`분류 이유: ${h(r.ai.category_reason)}`);
    const rank = opts.excluded ? "–" : (r.shownRank ?? r.rank);

    return `<li class="repo">
      <div class="repo__rank" aria-label="${rank}위">${rank}</div>
      <div class="repo__body">
        <div class="repo__top">
          <a class="repo__name" href="${h(r.url)}" target="_blank" rel="noopener"><span class="repo__owner">${h(owner)} /</span> ${h(name)}</a>
          <span class="repo__stars">${stars}</span>
        </div>
        <div class="tags">${tags.join("")}</div>
        ${body}
        ${warns}
        <div class="repo__actions">
          <a class="linkbtn" href="${h(r.url)}" target="_blank" rel="noopener">GitHub에서 열기</a>
          <button type="button" class="linkbtn" data-flip="${h(r.full_name)}">${showOrig ? "한국어로 보기" : "원문 보기"}</button>
          ${why.length ? `<button type="button" class="linkbtn" data-why>AI 판단 근거</button>` : ""}
        </div>
        ${why.length ? `<div class="why" hidden>${why.join("<br>")}</div>` : ""}
      </div></li>`;
  }

  function renderList() {
    const list = $("repos"), ex = $("excluded"), v = S.view;
    const notReady = !v || v.status === "baseline" || v.status === "empty";
    if (notReady) {
      list.innerHTML = "";
      $("result-count").textContent = "";
      ex.innerHTML = v && S.tab === "interest" ? `<div class="empty"><strong>순위는 다음 수집부터 나와요.</strong><br>
        첫 수집일의 스타 수를 기준점으로 저장했어요. 다음 수집 때 같은 레포의 스타 수와 비교해 가장 많이 늘어난 순서로 보여줘요.</div>` : "";
      return;
    }
    const { shown, excluded } = filtered();
    $("result-count").textContent = (S.category || S.query ? `${shown.length}개 표시 중 (필터 적용)` : `${shown.length}개`)
      + (v.kind === "week" ? (S.tab === "interest" ? " · 이 주 스타 증가 합계 순" : " · 등장한 날 수 → 스타 합계 순") : "");
    list.innerHTML = shown.length ? shown.map((r) => repoHTML(r)).join("")
      : `<li class="empty">조건에 맞는 레포가 없어요. 위에서 <strong>전체</strong>를 누르거나 검색어를 지워 보세요.</li>`;
    ex.innerHTML = excluded.length ? `<details class="excluded"><summary>관련 없다고 판단해 제외한 레포 ${excluded.length}개</summary>
      <ol class="repos">${excluded.map((r) => repoHTML(r, { excluded: true })).join("")}</ol></details>` : "";
  }

  function renderFoot() {
    const v = S.view;
    $("foot-meta").textContent = v && v.model
      ? `AI 모델 ${v.model} · 프롬프트 ${v.prompt}${S.tab === "interest" && v.candidates ? ` · 관심 분야 후보 ${num(v.candidates)}개 추적 중` : ""}`
      : "";
  }

  function renderAll() {
    renderHeader(); renderHero(); renderBar(); renderMultiples(); renderChips(); renderList(); renderFoot();
  }

  // ---------- 조작 ----------
  function setCategory(c) {
    S.category = c || null;
    renderBar(); renderMultiples(); renderChips(); renderList();
  }

  async function go({ tab, date, mode } = {}) {
    if (tab && tab !== S.tab) { S.tab = tab; S.category = null; S.date = null; }
    if (mode) S.mode = mode;
    if (date) S.date = date;
    try {
      if (S.mode === "week") {
        // 주를 고르면 그 주의 가장 최근 수집일을 기준 날짜로
        if (date) { const inWeek = tabInfo().dates.filter((d) => d >= date && d <= addDays(date, 6)); if (inWeek.length) S.date = inWeek[inWeek.length - 1]; }
        S.view = await loadWeekView();
      } else {
        S.view = await loadDayView();
      }
      if (S.date) writeHash();
      renderAll();
    } catch (err) {
      showError(err);
    }
  }

  function showError(err) {
    $("hero-line").textContent = "데이터를 불러오지 못했어요";
    $("hero-note").innerHTML = `파일: ${h(err.message)}. 내 PC에서 볼 때는 파일을 직접 열지 말고, 프로젝트 폴더에서
      <code>uv run python -m http.server -d site 8000</code> 실행 후 <code>http://localhost:8000</code>으로 여세요.`;
  }

  function bind() {
    document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => go({ tab: b.dataset.tab })));
    document.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => {
      if (b.dataset.mode !== S.mode) { S.category = null; go({ mode: b.dataset.mode }); }
    }));
    $("date-select").addEventListener("change", (e) => go({ date: e.target.value }));
    $("chips").addEventListener("click", (e) => {
      const b = e.target.closest(".chip");
      if (b && !b.disabled) setCategory(b.dataset.cat);
    });
    let t;
    $("search").addEventListener("input", (e) => {
      clearTimeout(t);
      t = setTimeout(() => { S.query = e.target.value; renderList(); }, 120);
    });
    document.querySelectorAll("[data-lang]").forEach((b) => b.addEventListener("click", () => {
      S.lang = b.dataset.lang; S.flipped.clear();
      document.querySelectorAll("[data-lang]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      renderList();
    }));
    document.querySelector("main").addEventListener("click", (e) => {
      const flip = e.target.closest("[data-flip]");
      if (flip) {
        const n = flip.dataset.flip;
        S.flipped.has(n) ? S.flipped.delete(n) : S.flipped.add(n);
        renderList();
        return;
      }
      const why = e.target.closest("[data-why]");
      if (why) {
        const box = why.closest(".repo__body").querySelector(".why");
        box.hidden = !box.hidden;
      }
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => renderBar());
  }

  async function init() {
    bind();
    readHash();
    try {
      S.index = await getJSON("data/index.json");
    } catch (err) {
      showError(err);
      return;
    }
    await go();
  }

  init();
})();
