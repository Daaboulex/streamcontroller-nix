# StreamController NixOS module — udev rules and system integration.
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.programs.streamcontroller;
  pkg = cfg.package;
in
{
  options.programs.streamcontroller = {
    enable = lib.mkEnableOption "StreamController — Elgato Stream Deck control application";

    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.streamcontroller;
      description = "The StreamController package to use.";
    };

    autostart = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = "Whether to autostart StreamController at login.";
    };
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [ pkg ];

    # Elgato Stream Deck USB device access (vendor 0x0fd9)
    services.udev.packages = [ pkg ];

    # XDG autostart entry
    environment.etc."xdg/autostart/streamcontroller.desktop" = lib.mkIf cfg.autostart {
      text = ''
        [Desktop Entry]
        Name=StreamController
        Comment=Control your Elgato Stream Deck
        Exec=${pkg}/bin/streamcontroller -b
        Terminal=false
        Type=Application
        X-GNOME-Autostart-enabled=true
      '';
    };
  };
}
