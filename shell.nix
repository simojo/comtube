{ pkgs ? import (fetchTarball https://git.io/Jf0cc) {} }:

let
  shellname = "python";
  mach-nix = import (
  builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix/";
      ref = "2.0.0";
    }
  );

  mods = mach-nix.mkPython {
    python = pkgs.python38;
    requirements = ''
      opencv-python
      pillow
      spacy
      youtube_transcript_api
      ffmpeg
      pillow
      youtube_dl
    '';
  };
in
  pkgs.mkShell {
    name = shellname;
    buildInputs = [
      mods
      pkgs.python38Packages.pip
    ];
    shellHook = ''
      export NIX_SHELL_NAME='${shellname}'
      alias p='python3'
    '';
  }

