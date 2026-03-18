# PicSeek

PicSeek is a reverse image search tool for Linux, similar to Samsung's Circle to Search. Draw around anything on your screen and search it instantly with Google Lens.

![PicSeek Preview](https://github.com/hassanmaqbool12/PicSeek/blob/3870140ef9ffd7d3bab108b5c81d431faa0b02ec/untitled.GIF)

# Installation

Download the latest `.deb` file from [Releases](https://github.com/hassanmaqbool12/PicSeek/releases) and install it:
```bash
sudo dpkg -i picseek.deb
```

All dependencies are installed automatically.

# Dependencies

PicSeek requires the following packages, all of which are installed automatically with the `.deb`:

`python3` `python3-requests` `python3-gi` `python3-cairo` `scrot` `libgtk-3-0`

# How it Works

1. Press `Ctrl + Shift + G` to launch PicSeek
2. Your screen dims and a crosshair cursor appears
3. Click and drag to draw a selection around the area you want to search
4. Release the mouse — a confirmation window appears with a preview
5. Press **Enter** to search or **Esc** to cancel
6. Google Lens opens with your results

If Chrome or Chromium is installed, results open in an isolated app window. Otherwise they open in your default browser.

# Privacy

The selected area is temporarily uploaded to an image host for processing and is automatically deleted after 10 seconds. Nothing is stored permanently.

# Shortcuts

| Action | Shortcut |
|---|---|
| Launch PicSeek | `Ctrl + Shift + G` |
| Confirm search | `Enter` |
| Cancel | `Esc` |

Shortcuts are registered automatically on installation for Cinnamon.

You can also launch PicSeek manually from the terminal:
```bash
picseek
```

# Compatibility

| | Status |
|---|---|
| X11 | ✅ Supported |
| Wayland | ❌ Not supported | Coming up version will support |

Tested on Linux Mint 21.1 Vera with Cinnamon 5.6.8. Should work on most Ubuntu and Debian based distributions running X11.

This is a beta release. Behavior may vary across desktop environments and window managers.

# Issues & Feedback

Found a bug or something looks wrong? Open an issue on [GitHub Issues](https://github.com/hassanmaqbool12/PicSeek/issues) and include any terminal output along with your distro and desktop environment.
