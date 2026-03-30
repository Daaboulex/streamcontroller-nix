# StreamController Home Manager module — declarative page and device configuration.
#
# Manages StreamController page JSON files declaratively and applies device
# settings (brightness, active page, defaults) via activation hooks.
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

  # Filter out null values from an attrset (non-recursive)
  filterNulls = lib.filterAttrs (_: v: v != null);

  # Build a label position attrset, omitting null fields
  mkLabelPos =
    posCfg:
    let
      attrs = filterNulls {
        inherit (posCfg) text;
        font-size = posCfg.size;
        inherit (posCfg) color;
        inherit (posCfg) font-family;
        inherit (posCfg) font-weight;
        inherit (posCfg) outline_width;
      };
    in
    if attrs == { } then null else attrs;

  # Build media attrset, omitting null fields
  mkMedia =
    mediaCfg:
    let
      attrs = filterNulls {
        inherit (mediaCfg) path size valign;
      };
    in
    if attrs == { } then null else attrs;

  # Build page JSON files from Nix config
  mkPageFile =
    name: pageCfg:
    let
      keysJson = builtins.mapAttrs (_coord: keyCfg: {
        states = builtins.mapAttrs (
          _stateId: stateCfg:
          let
            labels = filterNulls {
              top = mkLabelPos stateCfg.label.top;
              center = mkLabelPos stateCfg.label.center;
              bottom = mkLabelPos stateCfg.label.bottom;
            };
            media = mkMedia stateCfg.media;
          in
          {
            inherit (stateCfg) actions;
            inherit (stateCfg) image-control-action;
            inherit (stateCfg) label-control-actions;
            inherit (stateCfg) background-control-action;
          }
          // (if labels != { } then { inherit labels; } else { })
          // (if media != null then { inherit media; } else { })
          // (lib.optionalAttrs (stateCfg.background != null) {
            background.color = stateCfg.background;
          })
        ) keyCfg.states;
      }) pageCfg.keys;

      pageJson = {
        keys = keysJson;
      }
      // (lib.optionalAttrs (pageCfg.brightness.value != null) {
        brightness = filterNulls {
          inherit (pageCfg.brightness) value overwrite;
        };
      })
      // (lib.optionalAttrs (pageCfg.screensaver != null) {
        inherit (pageCfg) screensaver;
      })
      // pageCfg.extraConfig;
    in
    pkgs.writeText "streamcontroller-page-${name}.json" (builtins.toJSON pageJson);

  # Build the default-pages JSON
  defaultPagesJson = pkgs.writeText "streamcontroller-default-pages.json" (
    builtins.toJSON { default-pages = cfg.defaultPages; }
  );

  labelPositionSubmodule = lib.types.submodule {
    options = {
      text = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Label text";
      };
      size = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = null;
        description = "Label font size";
      };
      color = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Label colour as RRGGBBAA hex string";
      };
      font-family = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Label font family";
      };
      font-weight = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = null;
        description = "Label font weight";
      };
      outline_width = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = null;
        description = "Label outline width in pixels";
      };
    };
  };

  mediaSubmodule = lib.types.submodule {
    options = {
      path = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Path to media file (image/icon)";
      };
      size = lib.mkOption {
        type = lib.types.nullOr (lib.types.either lib.types.int lib.types.float);
        default = null;
        description = "Media size (integer pixels or float scale factor)";
      };
      valign = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Vertical alignment of media";
      };
    };
  };

  brightnessSubmodule = lib.types.submodule {
    options = {
      value = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = null;
        description = "Brightness value (0-100)";
      };
      overwrite = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = "Whether to overwrite device brightness";
      };
    };
  };

  stateSubmodule = lib.types.submodule {
    options = {
      label = lib.mkOption {
        type = lib.types.submodule {
          options = {
            top = lib.mkOption {
              type = labelPositionSubmodule;
              default = { };
              description = "Top label configuration";
            };
            center = lib.mkOption {
              type = labelPositionSubmodule;
              default = { };
              description = "Center label configuration";
            };
            bottom = lib.mkOption {
              type = labelPositionSubmodule;
              default = { };
              description = "Bottom label configuration";
            };
          };
        };
        default = { };
        description = "Label configuration for each position (top, center, bottom)";
      };
      media = lib.mkOption {
        type = mediaSubmodule;
        default = { };
        description = "Media (image/icon) configuration";
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
      image-control-action = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = 0;
        description = "Image control action (0 = default)";
      };
      label-control-actions = lib.mkOption {
        type = lib.types.listOf lib.types.int;
        default = [
          0
          0
          0
        ];
        description = "Label control actions for top, center, bottom";
      };
      background-control-action = lib.mkOption {
        type = lib.types.nullOr lib.types.int;
        default = 0;
        description = "Background control action (0 = default)";
      };
    };
  };

  keySubmodule = lib.types.submodule {
    options = {
      states = lib.mkOption {
        type = lib.types.lazyAttrsOf stateSubmodule;
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
        type = lib.types.lazyAttrsOf keySubmodule;
        default = { };
        example = {
          "0x0" = {
            states."0" = {
              label.center = {
                text = "Play";
              };
              media.path = "/path/to/play.png";
            };
          };
        };
        description = "Key definitions. Keys are coordinates as 'COLxROW' (e.g., '0x0', '1x2').";
      };
      brightness = lib.mkOption {
        type = brightnessSubmodule;
        default = { };
        description = "Page brightness settings";
      };
      screensaver = lib.mkOption {
        type = lib.types.nullOr lib.types.attrs;
        default = null;
        description = "Screensaver settings";
      };
      extraConfig = lib.mkOption {
        type = lib.types.attrs;
        default = { };
        description = "Additional page JSON attributes merged at the top level (e.g., auto-change)";
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
      type = lib.types.lazyAttrsOf pageSubmodule;
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

    # Asset files (icons, images) to copy into the data directory
    assets = lib.mkOption {
      type = lib.types.attrsOf lib.types.path;
      default = { };
      example = {
        "my-icon.png" = ./icons/my-icon.png;
      };
      description = "Asset files to copy into the StreamController data directory. Keys are filenames, values are source paths. Files are placed at <dataPath>/assets/<key>.";
    };

    # Extra commands to run after applying config
    extraCommands = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Additional commands to run after applying StreamController configuration.";
    };
  };

  config = lib.mkIf cfg.enable {
    # Migrate runtime data from old Flatpak path to native XDG path (one-time)
    home.activation.streamcontrollerMigrate = lib.hm.dag.entryBefore [ "streamcontrollerPages" ] (
      let
        oldDir = "${config.home.homeDirectory}/.var/app/com.core447.StreamController/data";
        marker = "${dataDir}/.migrated-from-flatpak";
      in
      ''
        if [ -d "${oldDir}" ] && [ ! -f "${marker}" ] && [ "${oldDir}" != "${dataDir}" ]; then
          echo "StreamController: migrating data from Flatpak path to native path"
          mkdir -p "${dataDir}"

          # Move runtime directories (skip pages — HM manages those declaratively)
          for dir in plugins settings cache Store icons wallpapers sd_plus_bar_wallpapers logs; do
            if [ -d "${oldDir}/$dir" ] && [ ! -d "${dataDir}/$dir" ]; then
              cp -a "${oldDir}/$dir" "${dataDir}/$dir"
              echo "StreamController: migrated $dir/"
            fi
          done

          # Copy skip-onboarding marker if present
          if [ -f "${oldDir}/.skip-onboarding" ] && [ ! -f "${dataDir}/.skip-onboarding" ]; then
            cp "${oldDir}/.skip-onboarding" "${dataDir}/.skip-onboarding"
          fi

          touch "${marker}"
          echo "StreamController: migration complete (old data preserved at ${oldDir})"
        fi
      ''
    );

    # Deploy assets and declarative page files via activation hook
    home.activation.streamcontrollerPages =
      lib.mkIf (cfg.pages != { } || cfg.defaultPages != { } || cfg.assets != { })
        (
          lib.hm.dag.entryAfter [ "writeBoundary" ] ''
            mkdir -p "${dataDir}/pages"
            mkdir -p "${dataDir}/settings"
            mkdir -p "${dataDir}/assets"

            ${lib.concatStringsSep "\n" (
              lib.mapAttrsToList (name: src: ''
                if ! cmp -s "${src}" "${dataDir}/assets/${name}" 2>/dev/null; then
                  install -m 644 "${src}" "${dataDir}/assets/${name}"
                  echo "StreamController: updated asset '${name}'"
                fi
              '') cfg.assets
            )}

            ${lib.concatStringsSep "\n" (
              lib.mapAttrsToList (
                name: _pageCfg:
                let
                  pageFile = mkPageFile name _pageCfg;
                in
                ''
                  # Only overwrite if content changed (preserve manual edits if Nix config unchanged)
                  if ! cmp -s "${pageFile}" "${dataDir}/pages/${name}.json" 2>/dev/null; then
                    install -m 644 "${pageFile}" "${dataDir}/pages/${name}.json"
                    echo "StreamController: updated page '${name}'"
                  fi
                ''
              ) cfg.pages
            )}

            ${lib.optionalString (cfg.defaultPages != { }) ''
              # Write default pages to settings
              if ! cmp -s "${defaultPagesJson}" "${dataDir}/settings/pages.json" 2>/dev/null; then
                install -m 644 "${defaultPagesJson}" "${dataDir}/settings/pages.json"
                echo "StreamController: updated default pages"
              fi
            ''}
          ''
        );

    # Run extra commands after StreamController starts (if any)
    systemd.user.services.streamcontroller-apply = lib.mkIf (cfg.extraCommands != [ ]) {
      Unit = {
        Description = "Apply StreamController device configuration";
        After = [ "graphical-session.target" ];
      };
      Service = {
        Type = "oneshot";
        RemainAfterExit = true;
        ExecStartPre = "${pkgs.coreutils}/bin/sleep 5";
        ExecStart = pkgs.writeShellScript "streamcontroller-apply" ''
          set -euo pipefail
          ${lib.concatStringsSep "\n" cfg.extraCommands}
          echo "StreamController config applied"
        '';
      };
      Install = {
        WantedBy = [ "graphical-session.target" ];
      };
    };
  };
}
