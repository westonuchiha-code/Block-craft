# Blockcraft desktop build

A thin Electron shell around `game/blockcraft.html`. The game itself is unchanged; this gives it its own window, full screen,
and a save folder of its own.

## What it does

- Starts full screen with no menu bar. **F11** or **Alt+Enter** toggles full screen. Everything else is in the game's own MENU.
- Saves live in the app's profile folder (Windows: `%APPDATA%\Blockcraft`), so replacing the game file does not touch them.
  The game's EXPORT / IMPORT still works for moving a world between the browser and the desktop app.
- Keyboard, mouse and gamepad work as in Chrome. The GPU renderer is used when the machine has real graphics hardware.

## Run it from source (any PC with Node.js 20+)

```
cd desktop
npm install
npm start
```

## Make the Windows files

On a Windows PC:

```
cd desktop
npm install
npm run dist:win
```

That writes `desktop/dist/Blockcraft <version>.exe` (portable, no install) and `Blockcraft Setup <version>.exe` (installer).

Or without a PC: on GitHub open **Actions -> Desktop build (Windows) -> Run workflow**, then download the files from the run's
**Artifacts**. That workflow only runs when started by hand.

## Self-test

`npm test` starts the app, makes a world, checks the game is running and saving, writes a screenshot and prints a report.

## What has and has not been checked (2026-11-15)

- Checked on Linux (the build sandbox): the app starts, makes a world, runs at about 27 frames a second on the CPU renderer
  (the sandbox has no graphics card), saves, and reports no errors. See `proof/desktop_selftest.png`.
- An unpacked Windows build was produced from Linux (`Blockcraft.exe`, about 110 MB zipped), but **it has never been run on
  Windows**. The GitHub workflow has been written but **never run**.
- Not done: an icon, Steam integration (achievements, cloud saves, overlay), code signing. Windows will show a
  "unknown publisher" warning until the build is signed.
