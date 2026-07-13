{
  description = "StreamController — Linux Stream Deck application with plugin ecosystem";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    std = {
      url = "github:Daaboulex/nix-packaging-standard?ref=v2.10.0";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.git-hooks.follows = "git-hooks";
    };
  };

  outputs =
    inputs@{
      flake-parts,
      self,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      imports = [ inputs.std.flakeModules.base ];

      flake.overlays.default = final: _prev: {
        streamcontroller = final.callPackage ./package.nix { };
      };
      flake.nixosModules.default = import ./module.nix;
      flake.homeManagerModules.default = import ./hm-module.nix;

      perSystem =
        {
          system,
          pkgs,
          self',
          ...
        }:
        {
          packages.streamcontroller = pkgs.callPackage ./package.nix { };
          packages.streamcontroller-cli = pkgs.callPackage ./cli/package.nix { };
          packages.default = self'.packages.streamcontroller;

          # An env+source python app has no wheel metadata, so a new upstream
          # requirement ships silently (dasbus, 1.5.0-beta.15) -- this gate
          # reads the source's requirements.txt against the built env.
          checks.requirements-covered = inputs.std.lib.requirementsCoveredCheck {
            inherit pkgs;
            env = self'.packages.streamcontroller.passthru.python;
            src = self'.packages.streamcontroller.passthru.src;
            # One source of truth with update.sh's auto-add skip list.
            ignore = (builtins.fromJSON (builtins.readFile ./.github/update.json)).pythonRequirements.ignore;
          };

          checks.module-eval-nixos = inputs.std.lib.nixosModuleCheck {
            inherit (inputs) nixpkgs;
            inherit system;
            overlays = [ self.overlays.default ];
            module = ./module.nix;
            config.programs.streamcontroller.enable = true;
          };

          checks.module-eval-hm = inputs.std.lib.homeModuleCheck {
            inherit (inputs) nixpkgs home-manager;
            inherit system;
            overlays = [ self.overlays.default ];
            module = ./hm-module.nix;
            config.programs.streamcontroller.enable = true;
          };
        };
    };
}
