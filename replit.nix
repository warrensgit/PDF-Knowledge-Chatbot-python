{pkgs}: {
  deps = [
    pkgs.bash
    pkgs.xcbuild
    pkgs.swig
    pkgs.openjpeg
    pkgs.mupdf
    pkgs.libjpeg_turbo
    pkgs.jbig2dec
    pkgs.harfbuzz
    pkgs.gumbo
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.glibcLocales
    pkgs.glibc
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.openjpeg
      pkgs.jbig2dec
      pkgs.harfbuzz
      pkgs.gumbo
      pkgs.freetype
      pkgs.glibcLocales
    ];
  };
}
