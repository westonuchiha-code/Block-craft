// The player's body: where it is, how it moves and how it collides with the world.
// Sizes and speeds follow Minecraft: 0.6 wide, 1.8 tall, eyes at 1.62; walk 4.3 blocks a second, sprint 5.6.
import { BLOCK } from '../world/blocks.js';

const HALF_WIDTH = 0.3, HEIGHT = 1.8, EYE_HEIGHT = 1.62;
const GRAVITY = 32, TERMINAL = 60, JUMP_SPEED = 8.9;              // a jump clears one and a quarter blocks
const WALK = 4.3, SPRINT = 5.6, SNEAK = 1.3, FLY = 11, FLY_SPRINT = 22;
const GROUND_ACCEL = 60, AIR_ACCEL = 18, SWIM_ACCEL = 20;
const PITCH_LIMIT = Math.PI / 2 - 0.01;

export class Player {
  constructor(x, y, z) {
    this.x = x; this.y = y; this.z = z;          // feet, centre
    this.vx = 0; this.vy = 0; this.vz = 0;
    this.yaw = 0; this.pitch = 0;                // yaw 0 looks towards -z (north)
    this.onGround = false;
    this.inWater = false;
    this.flying = false;
    this.sprinting = false;
    this.sneaking = false;
    this.walked = 0;                             // distance walked, for the view bob and footsteps
  }

  get eyeY() { return this.y + (this.sneaking && !this.flying ? EYE_HEIGHT - 0.3 : EYE_HEIGHT); }

  /** The direction the player is looking, as a unit vector. */
  lookDirection() {
    const cp = Math.cos(this.pitch);
    return { x: -Math.sin(this.yaw) * cp, y: Math.sin(this.pitch), z: -Math.cos(this.yaw) * cp };
  }

  /**
   * @param {ReturnType<import('../input/input.js').Input['emptyState']>} input
   */
  /** Once per frame: turn the view and take the button presses (things that must happen exactly once, not once per step). */
  look(input) {
    this.yaw += input.lookX;
    this.pitch = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, this.pitch + input.lookY));
    if (input.fly) { this.flying = !this.flying; this.vy = 0; }
    if (input.sprintToggle) this.sprinting = !this.sprinting;
    if (input.sneakToggle) this.sneaking = !this.sneaking;
  }

  /** One physics step of dt seconds (called at a fixed rate, so movement is the same whatever the frame rate). */
  step(dt, input, world) {
    if (input.sprint) this.sprinting = true;
    if (input.moveZ >= 0 && !input.sprint && !input.sprintToggle && Math.hypot(input.moveX, input.moveZ) < 0.2) this.sprinting = false;
    const sneaking = this.sneaking || input.sneak;

    this.inWater = this.bodyIn(world, BLOCK.water);
    const speed = this.flying ? (this.sprinting ? FLY_SPRINT : FLY)
      : sneaking ? SNEAK : this.sprinting && input.moveZ < 0 ? SPRINT : WALK;
    const swimFactor = this.inWater && !this.flying ? 0.55 : 1;

    // turn the stick or keys into a wanted velocity in the world, relative to where the player faces
    const sin = Math.sin(this.yaw), cos = Math.cos(this.yaw);
    const wantX = (input.moveX * cos + input.moveZ * sin) * speed * swimFactor;
    const wantZ = (-input.moveX * sin + input.moveZ * cos) * speed * swimFactor;
    const accel = (this.flying ? GROUND_ACCEL : this.inWater ? SWIM_ACCEL : this.onGround ? GROUND_ACCEL : AIR_ACCEL) * dt;
    this.vx += Math.max(-accel, Math.min(accel, wantX - this.vx));
    this.vz += Math.max(-accel, Math.min(accel, wantZ - this.vz));

    if (this.flying) {
      const up = (input.jump ? 1 : 0) - (sneaking ? 1 : 0);
      this.vy += Math.max(-accel, Math.min(accel, up * speed * 0.7 - this.vy));
    } else if (this.inWater) {
      this.vy -= GRAVITY * 0.18 * dt;
      if (input.jump) this.vy = Math.min(this.vy + 22 * dt, 3.2);       // swim up
      this.vy = Math.max(this.vy, -3);
    } else {
      if (input.jump && this.onGround) this.vy = JUMP_SPEED;
      this.vy = Math.max(-TERMINAL, this.vy - GRAVITY * dt);
    }

    // move one axis at a time, so sliding along walls works
    const ox = this.x, oz = this.z;
    this.onGround = false;
    this.moveAxis(world, 'y', this.vy * dt);
    this.moveAxis(world, 'x', this.vx * dt);
    this.moveAxis(world, 'z', this.vz * dt);
    // sneaking keeps you from walking off an edge
    if (sneaking && this.onGround && !this.flying && !this.standingOnSomething(world)) { this.x = ox; this.z = oz; this.vx = this.vz = 0; }
    if (this.onGround && this.flying) this.flying = false;
    this.sneaking = sneaking && this.sneaking;
    this.walked += Math.hypot(this.x - ox, this.z - oz);
  }

  moveAxis(world, axis, delta) {
    if (!delta) return;
    this[axis] += delta;
    const box = this.box();
    for (let x = Math.floor(box.x0); x <= Math.floor(box.x1); x++)
      for (let y = Math.floor(box.y0); y <= Math.floor(box.y1); y++)
        for (let z = Math.floor(box.z0); z <= Math.floor(box.z1); z++) {
          if (!world.isSolid(x, y, z)) continue;
          // push back out of this block along the axis we moved on
          if (axis === 'x') this.x = delta > 0 ? x - HALF_WIDTH - 1e-4 : x + 1 + HALF_WIDTH + 1e-4;
          if (axis === 'z') this.z = delta > 0 ? z - HALF_WIDTH - 1e-4 : z + 1 + HALF_WIDTH + 1e-4;
          if (axis === 'y') { if (delta < 0) { this.y = y + 1; this.onGround = true; } else this.y = y - HEIGHT - 1e-4; }
          this[`v${axis}`] = 0;
          return;
        }
  }

  box() {
    return { x0: this.x - HALF_WIDTH, x1: this.x + HALF_WIDTH - 1e-6, y0: this.y, y1: this.y + HEIGHT - 1e-6, z0: this.z - HALF_WIDTH, z1: this.z + HALF_WIDTH - 1e-6 };
  }

  standingOnSomething(world) {
    const b = this.box(), y = Math.floor(this.y - 0.05);
    for (let x = Math.floor(b.x0); x <= Math.floor(b.x1); x++) for (let z = Math.floor(b.z0); z <= Math.floor(b.z1); z++) if (world.isSolid(x, y, z)) return true;
    return false;
  }

  bodyIn(world, id) {
    return world.getBlock(Math.floor(this.x), Math.floor(this.y + 0.4), Math.floor(this.z)) === id;
  }

  /** Would a block at (x, y, z) overlap the player's body? (You cannot place a block inside yourself.) */
  overlaps(x, y, z) {
    const b = this.box();
    return b.x1 > x && b.x0 < x + 1 && b.y1 > y && b.y0 < y + 1 && b.z1 > z && b.z0 < z + 1;
  }
}

