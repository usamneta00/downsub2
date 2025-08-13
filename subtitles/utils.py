import os
import sys
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

from downsub import get_video_id, is_arabic, client

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

def fetch_transcripts(video_url):
    """
    Returns (original_single_line, translated_and_rewritten_single_line_or_None).
    """
    video_id = get_video_id(video_url)
    transcripts = YouTubeTranscriptApi().list(video_id)
    transcript = next(iter(transcripts))
    fetched = transcript.fetch()
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