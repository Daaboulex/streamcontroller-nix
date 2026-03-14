# StreamController — Elgato Stream Deck control application for Linux.
# Python GTK4/libadwaita application with plugin ecosystem and Pyro5 RPC.
{
  lib,
  stdenv,
  python3Packages,
  fetchFromGitHub,
  wrapGAppsHook4,
  gobject-introspection,
  gtk4,
  libadwaita,
  webkitgtk_6_0,
  glib,
  cairo,
  pango,
  gdk-pixbuf,
  librsvg,
  libusb1,
  hidapi,
  libevdev,
  libportal,
  pulseaudio,
  libpulseaudio,
  ffmpeg,
}:
let
  version = "1.5.0-beta.14";

  src = fetchFromGitHub {
    owner = "StreamController";
    repo = "StreamController";
    rev = version;
    hash = "sha256-iRG570/K51aXUXCgwiD1dJugH1iGc2i7uv01a20Bio4=";
  };

  python = python3Packages.python.withPackages (
    ps: with ps; [
      pygobject3
      pycairo
      pillow
      pyro5
      evdev
      pyudev
      pyusb
      pulsectl
      loguru
      click
      dbus-python
      psutil
      requests
      numpy
      websocket-client
      pydantic
      setproctitle
      natsort
      rich
      rpyc
      serpent
      cairosvg
      tqdm
      pyyaml
      jinja2
      werkzeug
      matplotlib
      imageio
      pyperclip
      rapidfuzz
      streamcontroller-plugin-tools
      streamcontroller-streamdeck
      usb-monitor
      python-wayland-extra
      indexed-bzip2
      opencv4
      async-lru
      bcrypt
      blinker
      cairocffi
      fuzzywuzzy
      levenshtein
      nltk
      pyclip
      pyspellchecker
      regex
      textual
      typing-inspection
      urllib3
      get-video-properties
      imageio-ffmpeg
      speedtest-cli
      pip
      websockets
      pygame
      python-vlc
      pyjwt
      cryptography
      redis
      flask
      python-osc
      aiofiles
      spotipy
    ]
  );
in
python3Packages.stdenv.mkDerivation {
  pname = "streamcontroller";
  inherit version src;

  nativeBuildInputs = [
    wrapGAppsHook4
    gobject-introspection
    python3Packages.wrapPython
  ];

  buildInputs = [
    gtk4
    libadwaita
    webkitgtk_6_0
    glib
    cairo
    pango
    gdk-pixbuf
    librsvg
    libusb1
    hidapi
    libevdev
    libportal
    pulseaudio
    libpulseaudio
    python
  ];

  patches = [
    ./patches/native-linux.patch
  ];

  postPatch = ''
    # Fix: upstream references DeviceManager.USB_VID_ELGATO which doesn't exist —
    # USB_VID_ELGATO is defined on USBVendorIDs, not DeviceManager.
    # Replace with the literal Elgato USB vendor ID.
    find . -name "*.py" -exec sed -i 's/DeviceManager.USB_VID_ELGATO/0x0fd9/g' {} +
  '';

  dontBuild = true;

  installPhase = ''
    runHook preInstall

    mkdir -p $out/share/streamcontroller
    cp -r . $out/share/streamcontroller/

    # Create wrapper script
    mkdir -p $out/bin
    cat > $out/bin/streamcontroller <<WRAPPER
    #!/bin/sh
    exec ${python}/bin/python3 $out/share/streamcontroller/main.py "\$@"
    WRAPPER
    chmod +x $out/bin/streamcontroller

    # Desktop entry
    mkdir -p $out/share/applications
    cat > $out/share/applications/com.core447.StreamController.desktop <<EOF
    [Desktop Entry]
    Name=StreamController
    Comment=Control your Elgato Stream Deck
    Exec=$out/bin/streamcontroller
    Icon=com.core447.StreamController
    Terminal=false
    Type=Application
    Categories=Utility;
    StartupWMClass=streamcontroller
    EOF

    # Icons - copy the entire hicolor directory from Assets
    mkdir -p "$out/share/icons/hicolor"
    cp -r Assets/icons/hicolor/* "$out/share/icons/hicolor/"

    # udev rules
    mkdir -p $out/lib/udev/rules.d
    cp udev.rules $out/lib/udev/rules.d/70-streamcontroller.rules

    runHook postInstall
  '';

  preFixup = ''
    makeWrapperArgs+=(
      "''${gappsWrapperArgs[@]}"
      --prefix LD_LIBRARY_PATH : "${
        lib.makeLibraryPath [
          libusb1
          hidapi
          libevdev
          glib
          stdenv.cc.cc.lib
          libpulseaudio
        ]
      }"
      --prefix PATH : "${lib.makeBinPath [ ffmpeg ]}"
    )
  '';

  # No tests in upstream
  doCheck = false;

  meta = {
    homepage = "https://github.com/StreamController/StreamController";
    description = "Elgato Stream Deck control application for Linux with plugin ecosystem";
    license = lib.licenses.gpl3Only;
    platforms = [ "x86_64-linux" ];
    mainProgram = "streamcontroller";
  };
}
