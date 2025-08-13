import os
import sys
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import inspect

from downsub import get_video_id, is_arabic, client

def get_subtitles(video_id, proxies):
    """
    Fetch subtitles for the given video ID using the provided proxy settings.
    Adapts to multiple youtube-transcript-api versions.
    """
    # Try ProxyConfig-based API (youtube-transcript-api >=1.2.0)
    try:
        sig = inspect.signature(YouTubeTranscriptApi.__init__)
        if 'proxy_config' in sig.parameters:
            from youtube_transcript_api.proxies import ProxyConfig

            proxy_cfg = ProxyConfig.from_requests_dict(proxies) if proxies else None
            api = YouTubeTranscriptApi(proxy_config=proxy_cfg)
            return api.fetch(video_id)
    except Exception:
        pass

    # Try static get_transcript (older versions)
    try:
        sig = inspect.signature(YouTubeTranscriptApi.get_transcript)
        if 'proxies' in sig.parameters:
            return YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception:
        pass

    # helper to call list/list_transcripts on obj
    def _call_list(obj):
        for method_name in ('list_transcripts', 'list'):
            if hasattr(obj, method_name):
                meth = getattr(obj, method_name)
                try:
                    sig = inspect.signature(meth)
                    if 'proxies' in sig.parameters:
                        return meth(video_id, proxies=proxies)
                    return meth(video_id)
                except Exception:
                    continue
        return None

    # try static list methods
    transcripts = _call_list(YouTubeTranscriptApi)
    # fallback to instance-based API
    if transcripts is None:
        api = YouTubeTranscriptApi()
        transcripts = _call_list(api)
    if transcripts is None:
        raise RuntimeError('Could not list transcripts for video ' + video_id)

    # if TranscriptList: pick manual then generated (robust to missing attrs/types)
    if hasattr(transcripts, 'find_manually_created_transcript'):
        manual_list = getattr(transcripts, 'manually_created_transcripts',
                              getattr(transcripts, '_manually_created_transcripts', []))
        codes = [t if isinstance(t, str) else getattr(t, 'language_code', None)
                 for t in manual_list]
        codes = [c for c in codes if c]
        if codes:
            try:
                tr = transcripts.find_manually_created_transcript(codes)
            except Exception:
                tr = None
        else:
            tr = None
        if tr is None:
            gen_list = getattr(transcripts, 'generated_transcripts',
                               getattr(transcripts, '_generated_transcripts', []))
            codes = [t if isinstance(t, str) else getattr(t, 'language_code', None)
                     for t in gen_list]
            codes = [c for c in codes if c]
            tr = transcripts.find_generated_transcript(codes)
        return tr.fetch()

    # otherwise transcripts is an iterable of Transcript objects
    return next(iter(transcripts)).fetch()

def translate_and_rewrite_with_gpt(text, max_chunk_size=2000, model="gpt-4o-mini"):
    # يقوم بالترجمة وإعادة الصياغة معاً في نفس الاستدعاء
    chunks = []
    while text:
        chunk = text[:max_chunk_size]
        if len(text) > max_chunk_size:
            last_space = chunk.rfind(" ")
            if last_space != -1:
                chunk = text[:last_space]
        chunks.append(chunk)
        text = text[len(chunk):].lstrip()

    translated_and_rewritten = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {idx}/{total}...", file=sys.stdout)
        response = client.responses.create(
            model=model,
            input=f"""قم بالترجمة إلى العربية وإعادة صياغة النص التالي ليكون أكثر وضوحاً وأفضل ترتيباً مع وضع عنوان لكل فقرة.

استخدم Markdown format بالضبط كما يلي:
- استخدم # للعنوان الرئيسي
- استخدم ## للعناوين الفرعية
- اترك سطر فارغ قبل وبعد كل عنوان
- اترك سطر فارغ بين الفقرات

مثال على التنسيق المطلوب:
# العنوان الرئيسي

## العنوان الفرعي الأول

محتوى الفقرة الأولى.

## العنوان الفرعي الثاني

محتوى الفقرة الثانية.

النص المراد ترجمته وإعادة صياغته:
{chunk}

النتيجة يجب أن تكون باللغة العربية مع إعادة صياغة واضحة وعناوين للفقرات باستخدام Markdown بالضبط كما في المثال أعلاه.""",
        )
        translated_and_rewritten.append(response.output_text.strip())
    return "\n".join(translated_and_rewritten)

def rewrite_arabic_with_gpt(text, max_chunk_size=2000, model="gpt-4o-mini"):
    """إعادة صياغة النص العربي فقط دون أي ترجمة، مع إخراج منسّق Markdown كما في الترجمة."""
    chunks = []
    while text:
        chunk = text[:max_chunk_size]
        if len(text) > max_chunk_size:
            last_space = chunk.rfind(" ")
            if last_space != -1:
                chunk = text[:last_space]
        chunks.append(chunk)
        text = text[len(chunk):].lstrip()

    rewritten_chunks = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Processing Arabic rewrite chunk {idx}/{total}...", file=sys.stdout)
        response = client.responses.create(
            model=model,
            input=f"""أعد صياغة النص العربي التالي فقط دون ترجمته إلى لغة أخرى، واجعله أكثر وضوحاً وتنظيماً.

استخدم Markdown format بالضبط كما يلي:
- استخدم # للعنوان الرئيسي
- استخدم ## للعناوين الفرعية
- اترك سطر فارغ قبل وبعد كل عنوان
- اترك سطر فارغ بين الفقرات

مثال على التنسيق المطلوب:
# العنوان الرئيسي

## العنوان الفرعي الأول

محتوى الفقرة الأولى.

## العنوان الفرعي الثاني

محتوى الفقرة الثانية.

النص العربي المطلوب إعادة صياغته:
{chunk}

النتيجة يجب أن تكون بالعربية فقط مع إعادة صياغة واضحة وعناوين للفقرات باستخدام Markdown كما في المثال أعلاه.""",
        )
        rewritten_chunks.append(response.output_text.strip())
    return "\n".join(rewritten_chunks)

def fetch_transcripts(video_url, proxy_url=None):
    """
    Returns (original_single_line, translated_and_rewritten_single_line_or_None).
    """
    video_id = get_video_id(video_url)
    # Allow proxy_url from environment if not explicitly provided
    if not proxy_url:
        proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    proxies = {"http":"http://vpqjkhfk:lu9m1z3hv108@23.95.150.145:6114","https":"http://vpqjkhfk:lu9m1z3hv108@23.95.150.145:6114"}
    fetched = get_subtitles(video_id, proxies)
    raw = "\n".join(sn.text for sn in fetched)
    original = " ".join(raw.splitlines())

    if is_arabic(raw):
        # إذا كان النص بالعربية، نقوم بإعادة الصياغة فقط ونخفي النص الأصلي
        rewritten_raw = rewrite_arabic_with_gpt(raw)
        rewritten = rewritten_raw.strip()
        return None, rewritten
    else:
        # إذا لم يكن بالعربية، نقوم بالترجمة وإعادة الصياغة معاً
        translated_and_rewritten_raw = translate_and_rewrite_with_gpt(raw)
        translated_and_rewritten = translated_and_rewritten_raw.strip()
        return original, translated_and_rewritten