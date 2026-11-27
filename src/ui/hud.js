// What is drawn over the world while playing: the crosshair, the hotbar, the name of the selected item, a progress bar while
// breaking a block, short notices, and (if wanted) the frame rate.
import { BLOCKS } from '../world/blocks.js';
import { blockIcon } from './icons.js';

export class Hud {
  constructor(root, tiles) {
    this.root = root;
    this.tiles = tiles;
    this.hotbarEl = root.querySelector('#hotbar');
    this.itemNameEl = root.querySelector('#itemName');
    this.fpsEl = root.querySelector('#fps');
    this.breakEl = root.querySelector('#breakBar');
    this.toastEl = root.querySelector('#toast');
    this.slots = [];
    this.timers = {};
  }

  show(on) { this.root.classList.toggle('open', on); }

  /** Draw the hotbar's slots (call when its contents change). */
  setHotbar(items, selected) {
    this.hotbarEl.innerHTML = '';
    this.slots = items.map(id => {
      const slot = document.createElement('div');
      slot.className = 'slot';
      if (id) slot.appendChild(blockIcon(id, this.tiles));
      this.hotbarEl.appendChild(slot);
      return slot;
    });
    this.items = items;
    this.select(selected, false);
  }

  select(index, announce = true) {
    this.slots.forEach((s, i) => s.classList.toggle('selected', i === index));
    if (announce) this.flash(this.itemNameEl, BLOCKS[this.items[index]]?.name ?? '', 1600);
  }

  /** Breaking progress, 0..1, or null to hide the bar. */
  setBreaking(progress) {
    this.breakEl.style.display = progress == null ? 'none' : 'block';
    if (progress != null) this.breakEl.firstElementChild.style.width = `${Math.round(progress * 100)}%`;
  }

  toast(text, ms = 2500) { this.flash(this.toastEl, text, ms); }

  flash(el, text, ms) {
    el.textContent = text;
    el.classList.add('show');
    clearTimeout(this.timers[el.id]);
    this.timers[el.id] = setTimeout(() => el.classList.remove('show'), ms);
  }

  setFps(text) {
    this.fpsEl.style.display = text ? 'block' : 'none';
    if (text) this.fpsEl.textContent = text;
  }
}
