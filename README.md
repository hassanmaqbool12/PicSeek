# PicSeek

PicSeek is an image search tool similar to Samsung’s Circle To Search.

# Support

PicSeek is written in Python and officially supports almost all Ubuntu/Debian-based distributions.

# Note

This is a beta release intended for testing purposes. It may not work properly on all desktop environments, window managers, or display servers. This version was tested on Linux Mint 21.1 Vera with Cinnamon 5.6.8. It will not work on Wayland. 

![PicSeek Screenshot](https://github.com/hassanmaqbool12/PicSeek/blob/72e3482d6b898d89bee7f8e176b8b5721ae1fb55/Screenshot%20from%202026-03-14%2004-03-58.png)

# How it Wroks?

PicSeek works by first creating an overlay on your screen. You use your cursor to draw a square around the object you want to search. This selection determines the area that will be captured as a screenshot.

Once you release the cursor, the overlay disappears and a confirmation window appears. You can press ESC to cancel or Enter to continue.

If you continue, 

- PicSeek uploads the selected image to the cloud and performs a Google Lens search.

- If you have Chrome or Chromium, it opens the Google Lens result in an isolated profile window.

- If you don’t have Chrome or Chromium, it opens the Google Lens result page in your default browser.

# Limitation of this version

Since PicSeek takes screenshots of specific areas of the screen and uses GTK3, it may behave differently on different desktop environments, window managers, and display servers. It will not work on Wayland, never and ever.

# Shortcuts and Usage

- On GNOME, PicSeek automatically creates its hotkey shortcuts upon installation.

- On Cinnamon, you need to manually add the shortcut via the Keyboard settings from the menu.

After installation, you can run PicSeek from the terminal using its command: `picseek`
