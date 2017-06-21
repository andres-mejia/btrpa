import contextlib
import glob
import os
import re
from pathlib import Path

from invoke import task


@contextlib.contextmanager
def directory(dirname=None):
    """
    changes current directory to dirname
    used as with directory(dirname) as dir to
    move out of the changed directory at the end
    :param dirname: directory to change into
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield Path(dirname or curdir)
    finally:
        os.chdir(curdir)


@task
def install_tools_osx(ctx):
    """
    installs third party tools required to generate diagrams and documents
    from sources including imagemagick, graphviz, pantuml, and pandoc
    :param ctx:
    """
    ctx.run('brew install imagemagick '
            '--with-librsvg --with-pango --with-libwmf --with-openjpeg '
            '--with-ghostscript --with-fftw --with-fontconfig')
    ctx.run('brew install graphviz --with-librsvg --with-freetype '
            '--with-bindings --with-pango')
    ctx.run('brew install plantuml')
    ctx.run('brew install pandoc')


@task
def puml(ctx):
    ctx.run('plantuml -tsvg ./docs/diagrams.puml')


@task
def raster(ctx):
    for svg_path in glob.iglob('./docs/*.svg'):
        cmd = build_raster_command(svg_path)
        print('will run now')
        print(cmd)
        ctx.run(cmd)


def build_raster_command(input_file):
    output_file = re.sub(r'\.svg$', '.png', input_file, 1)
    converter = 'rsvg-convert'
    dpi = 300  # lossless density
    width_in = 6.3  # MS Word A4 page size sans fields
    width_px = int(dpi * width_in)
    size_opts = '--dpi-x={} --width={}'.format(dpi, width_px)
    other_opts = '--format=png --keep-aspect-ratio --background-color=none'
    output_opt = '--output {}'.format(output_file)
    cmd = ' '.join((converter, size_opts, other_opts, output_opt, input_file))
    return cmd


@task(puml, raster)
def dg(ctx):
    pass


@task
def doc(ctx):
    input_file = 'adding-ds-to-rpa.md'
    output_file = 'adding-ds-to-rpa.docx'
    reference_file = 'style-reference.docx'
    with directory('./docs'):
        ctx.run('pandoc {} -o {} --toc --reference-docx={}'.format(
            input_file, output_file, reference_file))
