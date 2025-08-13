from django.shortcuts import render

from .forms import URLForm
from .utils import fetch_transcripts


def index(request):
    form = URLForm(request.POST or None)
    original = translated_and_rewritten = None
    if form.is_valid():
        url = form.cleaned_data['url']
        original, translated_and_rewritten = fetch_transcripts(url)

    return render(request, 'subtitles/index.html', {
        'form': form,
        'original': original,
        'translated_and_rewritten': translated_and_rewritten,
    })