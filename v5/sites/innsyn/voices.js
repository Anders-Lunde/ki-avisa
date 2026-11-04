/* Progressive enhancement; the audio and transcript also work without JS. */
(() => {
  const cards = [...document.querySelectorAll('[data-sample]')];
  const selected = new Set();
  const filter = document.getElementById('provider-filter');
  const status = document.getElementById('compare-status');
  const compare = document.getElementById('show-comparison');
  const reset = document.getElementById('show-all');
  const list = document.querySelector('.voice-list');
  let comparing = false;

  const update = () => {
    for (const card of cards) {
      card.hidden = comparing ? !selected.has(card.dataset.sample)
        : filter.value !== 'all' && card.dataset.provider !== filter.value;
      const button = card.querySelector('[data-compare]');
      const picked = selected.has(card.dataset.sample);
      button.setAttribute('aria-pressed', String(picked));
      button.textContent = picked ? 'Valgt ✓' : 'Sammenlign';
      button.disabled = !picked && selected.size === 2;
      if (card.hidden) card.querySelector('audio').pause();
    }
    for (const section of document.querySelectorAll('.provider')) {
      section.hidden = ![...section.querySelectorAll('[data-sample]')].some(card => !card.hidden);
    }
    compare.disabled = selected.size !== 2;
    compare.hidden = comparing;
    reset.hidden = !comparing;
    filter.disabled = comparing;
    list.classList.toggle('is-comparing', comparing);
    status.textContent = selected.size
      ? `${selected.size} av 2 valgt: ${cards.filter(card => selected.has(card.dataset.sample)).map(card => card.dataset.name).join(' og ')}.`
      : 'Velg to prøver for å sammenligne.';
  };

  document.querySelectorAll('[data-enhance]').forEach(element => { element.hidden = false; });
  document.querySelectorAll('[data-compare]').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.compare;
      if (selected.has(id)) selected.delete(id);
      else if (selected.size < 2) selected.add(id);
      if (selected.size < 2) comparing = false;
      update();
    });
  });
  filter.addEventListener('change', update);
  compare.addEventListener('click', () => {
    comparing = true;
    update();
    reset.focus();
  });
  reset.addEventListener('click', () => {
    comparing = false;
    filter.value = 'all';
    update();
    compare.focus();
  });
  const audio = cards.map(card => card.querySelector('audio'));
  audio.forEach(player => {
    player.addEventListener('play', () => audio.forEach(other => { if (other !== player) other.pause(); }));
    player.addEventListener('error', () => { player.closest('.audition').querySelector('.audio-error').hidden = false; });
  });
  // A stable sample link also works when a provider filter hid that sample.
  const revealLinkedSample = () => {
    const linkedSample = cards.find(card => `#${card.id}` === location.hash);
    const linkedProvider = [...document.querySelectorAll('.provider')].find(section => `#${section.id}` === location.hash);
    if (linkedSample || linkedProvider) {
      comparing = false;
      filter.value = 'all';
      update();
      (linkedSample || linkedProvider).scrollIntoView({block: linkedSample ? 'center' : 'start'});
    }
  };
  window.addEventListener('hashchange', revealLinkedSample);
  document.querySelectorAll('.jump a').forEach(link => link.addEventListener('click', () => {
    comparing = false;
    filter.value = 'all';
    update();
  }));
  update();
  revealLinkedSample();
})();
