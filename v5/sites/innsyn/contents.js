(() => {
  const menu = document.querySelector('.contents');
  if (!menu) return;
  const entries = [...menu.querySelectorAll('a[href^="#"]')]
    .map(link => ({link, section: document.getElementById(link.hash.slice(1))}))
    .filter(entry => entry.section);
  if (!entries.length) return;

  const desktop = window.matchMedia('(min-width:761px)');
  let active = null;
  let frame = 0;

  function revealActive() {
    if (!active || !desktop.matches || !menu.getClientRects().length) return;
    const bounds = menu.getBoundingClientRect();
    const link = active.link.getBoundingClientRect();
    // Scroll only the menu; scrollIntoView would also move the article.
    if (link.top < bounds.top + 8) menu.scrollTop += link.top - bounds.top - 8;
    else if (link.bottom > bounds.bottom - 8) menu.scrollTop += link.bottom - bounds.bottom + 8;
  }

  function update() {
    frame = 0;
    const readingLine = Math.min(160, window.innerHeight * 0.25);
    let next = null;
    for (const entry of entries) {
      if (entry.section.getBoundingClientRect().top > readingLine) break;
      next = entry;
    }
    if (next && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      next = entries[entries.length - 1];
    }
    if (next === active) return;
    if (active) active.link.removeAttribute('aria-current');
    active = next;
    if (active) active.link.setAttribute('aria-current', 'location');
    revealActive();
  }

  function schedule() {
    if (!frame) frame = window.requestAnimationFrame(update);
  }

  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', () => { schedule(); revealActive(); });
  window.addEventListener('pageshow', schedule);
  // Lazy images and expanded details can move headings without a scroll event.
  const body = document.querySelector('.article-body');
  if (body) new ResizeObserver(schedule).observe(body);
  schedule();
})();
