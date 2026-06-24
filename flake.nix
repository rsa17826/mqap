{
  description = "Archipelago Python Environment with local venv and graphics";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python313
          pkgs.python313Packages.pip
          pkgs.python313Packages.setuptools
          
          # Native libraries required for Kivy and system compiling
          pkgs.stdenv.cc.cc.lib
          pkgs.zlib
          pkgs.libGL
          pkgs.mtdev
          pkgs.libX11
          pkgs.libxkbcommon
          pkgs.glib
          pkgs.alsa-lib # Solves potential audio initialization warnings
        ];

        shellHook = ''
          if [ ! -d ".venv" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv .venv
          fi
          
          source .venv/bin/activate
          pip install --upgrade pip setuptools wheel > /dev/null

          # Map out all the newly added native libraries so Kivy can see them
          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.libGL}/lib:${pkgs.mtdev}/lib:${pkgs.xorg.libX11}/lib:${pkgs.libxkbcommon}/lib:${pkgs.glib}/lib:${pkgs.alsa-lib}/lib:$LD_LIBRARY_PATH"
          
          echo "Environment with GUI libraries ready! Run 'python Launcher.py'."
        '';
      };
    };
}