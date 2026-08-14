# final_html_generator.py - Saurabh Daddy Test Series
# Auto-crop pipeline ka final HTML generator.
# parser.crop_questions se questions crop karo -> jee_player se final HTML banao.
# Watermark + password gate jee_player me built-in hai, isliye yahan sirf glue code hai.
import argparse
import json
import os

try:
    from parser import crop_questions
except ImportError:
    crop_questions = None

import jee_player as jp

# Compatibility constants - agar purane code me ye import ho rahe hain
WATERMARK_CSS = jp.WATERMARK_CSS
GATE_CSS = ""  # ab gate jee_player ke andar hi hai
GATE_HTML = jp.GATE_HTML


def render_final_html(questions, answers, settings, welcome_title="",
                      welcome_message="", password="", answer_key_url="",
                      sections=None):
    """jee_player ka wrapper - same signature, watermark ke saath."""
    return jp.render_final_html(questions, answers, settings, welcome_title,
                                welcome_message, password, answer_key_url,
                                sections)


def generate(question_pdf, output_path, title="Test", password="1234",
             answers=None, duration=180, positive=4, negative=1,
             answer_key_url=""):
    """PDF se questions crop karo (parser.crop_questions) aur final HTML banao.

    crop_questions se [{no, image_b64}, ...] wali list aana chahiye.
    Agar tumhare parser.py ka signature alag hai to bas ye call adjust kar lena.
    """
    if crop_questions is None:
        raise RuntimeError("parser.py nahi mila - crop_questions import nahi ho paya")
    if not os.path.exists(question_pdf):
        raise FileNotFoundError(question_pdf)
    questions = crop_questions(question_pdf)
    if not questions:
        raise RuntimeError("crop_questions ne koi question return nahi kiya")
    settings = {"title": title, "duration": duration,
                "positive": positive, "negative": negative}
    html = render_final_html(questions, answers or {}, settings, title,
                             "Read all instructions carefully before starting the test.",
                             password, answer_key_url)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def main():
    ap = argparse.ArgumentParser(description="Saurabh Daddy Test Series - final HTML generator")
    ap.add_argument("pdf", help="Questions PDF ka path")
    ap.add_argument("-o", "--out", default="final_test.html", help="Output HTML file")
    ap.add_argument("-t", "--title", default="Test", help="Test title")
    ap.add_argument("-p", "--password", default="1234", help="Paper password")
    ap.add_argument("-a", "--answers", default="", help="Answers JSON file ({'1':'A', ...})")
    ap.add_argument("-d", "--duration", type=int, default=180)
    ap.add_argument("--pos", type=int, default=4)
    ap.add_argument("--neg", type=int, default=1)
    args = ap.parse_args()

    answers = {}
    if args.answers and os.path.exists(args.answers):
        with open(args.answers, encoding="utf-8") as f:
            answers = json.load(f)

    out = generate(args.pdf, args.out, args.title, args.password, answers,
                   args.duration, args.pos, args.neg)
    print("Final HTML ready:", out)


if __name__ == "__main__":
    main()