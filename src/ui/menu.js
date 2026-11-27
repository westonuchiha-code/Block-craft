// A menu: a column of items moved through with up / down. Left and right change a setting's value; confirm presses a button;
// back closes the menu. Built for a controller first (no cursor); the mouse can also point and click.
//
// Item kinds:
//   { type: 'button', label, onPress, hint?, disabled? }
//   { type: 'range',  label, get, set, min, max, step, format?, hint? }      a number, changed in steps with left / right
//   { type: 'toggle', label, get, set, hint? }                              on / off
//   { type: 'choice', label, get, set, options: [{ value, label }], hint? }

export class Menu {
  /**
   * @param {HTMLElement} container where the items are drawn
   * @param {object[]} items
   * @param {{ onBack?: () => void, hintEl?: HTMLElement }} options
   */
  constructor(container, items, options = {}) {
    this.container = container;
    this.items = items;
    this.onBack = options.onBack;
    this.hintEl = options.hintEl;
    this.focus = Math.max(0, items.findIndex(i => !i.disabled));
    this.render();
  }

  render() {
    this.container.innerHTML = '';
    this.rows = this.items.map((item, i) => {
      const row = document.createElement('div');
      row.className = `item ${item.type}${item.disabled ? ' disabled' : ''}`;
      if (item.type === 'button') row.textContent = item.label;
      else {
        const label = document.createElement('span'); label.textContent = item.label;
        const value = document.createElement('span'); value.className = 'value';
        row.append(label, value);
      }
      row.addEventListener('mouseenter', () => { if (!item.disabled) this.setFocus(i); });
      row.addEventListener('click', e => {
        if (item.disabled) return;
        this.setFocus(i);
        if (item.type === 'button') item.onPress();
        else this.change(e.offsetX < row.clientWidth / 2 ? -1 : 1);
      });
      this.container.appendChild(row);
      return row;
    });
    this.refresh();
  }

  /** Redraw values and the focus mark. */
  refresh() {
    this.rows.forEach((row, i) => {
      const item = this.items[i];
      row.classList.toggle('focus', i === this.focus);
      if (item.type === 'button') return;
      const value = row.querySelector('.value');
      const v = item.get();
      let text, bar = '';
      if (item.type === 'toggle') text = v ? 'On' : 'Off';
      else if (item.type === 'choice') text = item.options.find(o => o.value === v)?.label ?? String(v);
      else {
        text = item.format ? item.format(v) : String(v);
        bar = `<span class="bar"><i style="width:${((v - item.min) / (item.max - item.min)) * 100}%"></i></span>`;
      }
      value.innerHTML = `<span class="arrow">◀</span>${bar}<span>${text}</span><span class="arrow">▶</span>`;
    });
    const focused = this.rows[this.focus];
    focused?.scrollIntoView({ block: 'nearest' });
    if (this.hintEl) this.hintEl.textContent = this.items[this.focus]?.hint ?? '';
  }

  setFocus(i) { this.focus = i; this.refresh(); }

  move(step) {
    for (let k = 1; k <= this.items.length; k++) {
      const i = (this.focus + step * k + this.items.length * k) % this.items.length;
      if (!this.items[i].disabled) { this.setFocus(i); return; }
    }
  }

  /** Change the focused setting's value one step left (-1) or right (+1). */
  change(dir) {
    const item = this.items[this.focus];
    if (!item || item.disabled) return;
    if (item.type === 'toggle') item.set(!item.get());
    else if (item.type === 'choice') {
      const i = item.options.findIndex(o => o.value === item.get());
      item.set(item.options[(i + dir + item.options.length) % item.options.length].value);
    } else if (item.type === 'range') {
      const v = Math.round((item.get() + dir * item.step) / item.step) * item.step;
      item.set(Math.max(item.min, Math.min(item.max, +v.toFixed(4))));
    }
    this.refresh();
  }

  /** Handle one navigation action (from Input.takeNav). */
  nav(action) {
    const item = this.items[this.focus];
    switch (action) {
      case 'up': this.move(-1); break;
      case 'down': this.move(1); break;
      case 'left': this.change(-1); break;
      case 'right': this.change(1); break;
      case 'confirm':
        if (item?.type === 'button' && !item.disabled) item.onPress();
        else if (item?.type === 'toggle') this.change(1);
        break;
      case 'back': this.onBack?.(); break;
    }
  }
}
