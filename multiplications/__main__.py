from urllib import parse

import ollama
from fasthtml.common import *
from ollama import ShowResponse

app, rt = fast_app(live=True, debug=True)


def layout(title, *args, **kwargs):
    return Main(
        H1(title),
        Div(*args, **kwargs),
        cls="container"
    )


def fh_li_model(model):
    return Div(
        H3(model.model),
        A(Span(model.digest), href=f"/model/{model.model}"),
        Div(model)
    )

def fh_detail_model(model: ShowResponse):
    return Div(
        H3(model.model),
        Div(model.model_fields),
        Div(model.template)
    )

@rt('/')
def get():
    return Div(Titled("Hello"), hx_get="/change")


@rt('/change')
def get(): return P('Nice to be here!')


@rt("/model/{name}")
def get_model(name:str):
    res = ollama.show(name)
    # assert False
    return Titled(name, fh_detail_model(res))

@rt('/models/')
def get_models():
    return layout(
        "Available Ollama Models",
        Ul(*[Li(fh_li_model(m)) for m in (ollama.list().models)])
    )




serve()
