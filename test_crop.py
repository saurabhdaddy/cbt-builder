from parser import crop_questions
import base64, os

os.makedirs("crops", exist_ok=True)
qs = crop_questions(open("yourpaper.pdf", "rb").read())
print("questions found:", len(qs))
for q in qs:
    open(f"crops/q{q['no']}.png", "wb").write(base64.b64decode(q["image_b64"]))
print("saved to crops/ folder - open the PNG files and check them")