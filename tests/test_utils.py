import sys
import types

if 'PIL' not in sys.modules:
    pil_stub = types.ModuleType('PIL')

    class DummyImage:
        pass

    class DummyImageDraw:
        pass

    class DummyImageFont:
        pass

    pil_stub.Image = DummyImage
    pil_stub.ImageDraw = DummyImageDraw
    pil_stub.ImageFont = DummyImageFont
    sys.modules['PIL'] = pil_stub
    sys.modules['PIL.Image'] = DummyImage
    sys.modules['PIL.ImageDraw'] = DummyImageDraw
    sys.modules['PIL.ImageFont'] = DummyImageFont

if 'gradio' not in sys.modules:
    gradio_stub = types.ModuleType('gradio')

    class DummySoft:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, **kwargs):
            return self

    class DummyColor:
        def __init__(self, *args, **kwargs):
            pass

    class DummySizes:
        radius_sm = 0

    class DummyThemes:
        Soft = DummySoft
        Color = DummyColor
        sizes = DummySizes()

    gradio_stub.themes = DummyThemes()
    sys.modules['gradio'] = gradio_stub

if 'mdtex2html' not in sys.modules:
    mdtex_stub = types.ModuleType('mdtex2html')

    def convert(text, extensions=None):
        return text

    mdtex_stub.convert = convert
    sys.modules['mdtex2html'] = mdtex_stub

if 'markdown' not in sys.modules:
    markdown_stub = types.ModuleType('markdown')

    def markdown(text, extensions=None):
        return text

    markdown_stub.markdown = markdown
    sys.modules['markdown'] = markdown_stub

if 'pygments' not in sys.modules:
    pygments_stub = types.ModuleType('pygments')

    def highlight(code, lexer, formatter):
        return code

    pygments_stub.highlight = highlight

    formatters_stub = types.ModuleType('pygments.formatters')

    class HtmlFormatter:
        pass

    formatters_stub.HtmlFormatter = HtmlFormatter

    lexers_stub = types.ModuleType('pygments.lexers')

    class ClassNotFound(Exception):
        pass

    def get_lexer_by_name(name, stripall=True):
        return None

    def guess_lexer(text):
        return None

    lexers_stub.ClassNotFound = ClassNotFound
    lexers_stub.get_lexer_by_name = get_lexer_by_name
    lexers_stub.guess_lexer = guess_lexer

    sys.modules['pygments'] = pygments_stub
    sys.modules['pygments.formatters'] = formatters_stub
    sys.modules['pygments.lexers'] = lexers_stub

from Nicole.serve.app_modules.utils import is_variable_assigned


def test_is_variable_assigned_true():
    x = 123
    assert is_variable_assigned("x") is True


def test_is_variable_assigned_false():
    assert is_variable_assigned("x") is False
