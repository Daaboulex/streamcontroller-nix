# StreamController Home Manager module — declarative page and device configuration.
#
# Manages StreamController page JSON files declaratively and applies device
# settings (brightness, active page) via the StreamController CLI at login.
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.programs.streamcontroller;

  # StreamController uses ~/.var/app/com.core447.StreamController/data for flatpak
  # or XDG_DATA_HOME/streamcontroller for native
  dataDir = cfg.dataPath;

  # Build page JSON files from Nix config
  mkPageFile =
    name: pageCfg:
    let
      keysJson = builtins.mapAttrs (_coord: keyCfg: {
        states = builtins.mapAttrs (_stateId: stateCfg: {
          labels = lib.filterAttrs (_: v: v != null) {
            top = lib.optionalAttrs (stateCfg.labelTop != null) {
              text = stateCfg.labelTop;
              font-size = stateCfg.labelSize;
              color = stateCfg.labelColor;
            };
            center = lib.optionalAttrs (stateCfg.labelCenter != null) {
              text = stateCfg.labelCenter;
              font-size = stateCfg.labelSize;
              color = stateCfg.labelColor;
            };
            bottom = lib.optionalAttrs (stateCfg.labelBottom != null) {
              text = stateCfg.labelBottom;
              font-size = stateCfg.labelSize;
              color = stateCfg.labelColor;
            };
          };
          media = lib.optionalAttrs (stateCfg.image != null) {
            path = stateCfg.image;
          };
          background = lib.optionalAttrs (stateCfg.background != null) {
            color = stateCfg.background;
          };
          inherit (stateCfg) actions;
        }) keyCfg.states;
      }) pageCfg.keys;

      pageJson = {
        keys = keysJson;
        settings = lib.filterAttrs (_: v: v != null) {
          inherit (pageCfg) brightness;
          inherit (pageCfg) screensaver;
        };
      }
      // pageCfg.extraConfig;
    in
    pkgs.writeText "streamcontroller-page-${name}.json" (builtins.toJSON pageJson);

  # Generate page change commands for device defaults
  defaultPageCmds = lib.mapAttrsToList (
    serial: pageName:
    "${cfg.package}/bin/streamcontroller --change-page ${serial} ${lib.escapeShellArg pageName}"
  ) cfg.defaultPages;

  stateSubmodule = lib.types.submodule {
    options = {
      labelTop = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Top label text";
      };
      labelCenter = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Center label text";
      };
      labelBottom = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Bottom label text";
      };
      labelSize = lib.mkOption {
        type = lib.types.int;
        default = 16;
        description = "Label font size";
      };
      labelColor = lib.mkOption {
        type = lib.types.str;
        default = "255,255,255,255";
        description = "Label colour as R,G,B,A";
      };
      image = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Path to button image";
      };
      background = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Background colour as hex RRGGBBAA";
      };
      actions = lib.mkOption {
        type = lib.types.listOf lib.types.attrs;
        default = [ ];
        description = "List of action definitions (plugin-specific attrs)";
      };
    };
  };

  keySubmodule = lib.types.submodule {
    options = {
      states = lib.mkOption {
        type = lib.types.attrsOf stateSubmodule;
        default = {
          "0" = { };
        };
        description = "Button states (keys are state IDs as strings: \"0\", \"1\", etc.)";
      };
    };
  };

  pageSubmodule = lib.types.submodule {
    options = {
      keys = lib.mkOption {
        type = lib.types.attrsOf keySubmodule;
        default = { };
        example = {
          "0x0" = {
            states."0" = {
              labelCenter = "Play";
              image = "/path/to/play.png";
            };
          };
        };
        description = "Key definitions. Keys are coordinates as 'COLxROW' (e.g., '0x0', '1x2').";
      };
      brightness = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = null;
        description = "Page brightness (0-100)";
      };
      screensaver = lib.mkOption {
        type = lib.types.nullOr lib.types.attrs;
        default = null;
        description = "Screensaver settings";
      };
      extraConfig = lib.mkOption {
        type = lib.types.attrs;
        default = { };
        description = "Additional page JSON attributes merged at the top level";
      };
    };
  };
in
{
  options.programs.streamcontroller = {
    enable = lib.mkEnableOption "declarative StreamController page and device configuration";

    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.streamcontroller;
      description = "The StreamController package to use.";
    };

    dataPath = lib.mkOption {
      type = lib.types.str;
      default = "${config.xdg.dataHome}/StreamController";
      description = "StreamController data directory path.";
    };

    # Declarative pages
    pages = lib.mkOption {
      type = lib.types.attrsOf pageSubmodule;
      default = { };
      description = "Declarative page definitions. Keys are page names.";
    };

    # Default page per device
    defaultPages = lib.mkOption {
      type = lib.types.attrsOf lib.types.str;
      default = { };
      example = {
        "CL12345678" = "Main";
      };
      description = "Map of device serial numbers to their default page name.";
    };

    # Extra commands to run after applying config
    extraCommands = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Additional commands to run after applying StreamController configuration.";
    };
  };

  config = lib.mkIf cfg.enable {
    # Deploy declarative page files
    home.activation.streamcontrollerPages = lib.mkIf (cfg.pages != { }) (
      lib.hm.dag.entryAfter [ "writeBoundary" ] ''
        mkdir -p "${dataDir}/pages"
        ${lib.concatStringsSep "\n" (
          lib.mapAttrsToList (
            name: _pageCfg:
            let
              pageFile = mkPageFile name _pageCfg;
            in
            ''
              # Only overwrite if content changed (preserve manual edits if Nix config unchanged)
              if ! cmp -s "${pageFile}" "${dataDir}/pages/${name}.json" 2>/dev/null; then
                cp "${pageFile}" "${dataDir}/pages/${name}.json"
                echo "StreamController: updated page '${name}'"
              fi
            ''
          ) cfg.pages
        )}
      ''
    );

    # Apply device defaults after StreamController starts
    systemd.user.services.streamcontroller-apply =
      lib.mkIf (defaultPageCmds != [ ] || cfg.extraCommands != [ ])
        {
          Unit = {
            Description = "Apply StreamController device configuration";
            After = [ "graphical-session.target" ];
          };
          Service = {
            Type = "oneshot";
            RemainAfterExit = true;
            # Wait for StreamController to be running
            ExecStartPre = "${pkgs.coreutils}/bin/sleep 5";
            ExecStart = pkgs.writeShellScript "streamcontroller-apply" ''
              set -euo pipefail
              ${lib.concatStringsSep "\n" (defaultPageCmds ++ cfg.extraCommands)}
              echo "StreamController config applied"
            '';
          };
          Install = {
            WantedBy = [ "graphical-session.target" ];
          };
        };
  };
}
