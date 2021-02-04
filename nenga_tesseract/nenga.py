import sys
import PIL
from PIL import ImageFilter
import numpy as np
# PDF
from pdf2image import convert_from_path
# OCR
import pyocr
import pyocr.builders

# Init OCR
# - ref: https://techacademy.jp/magazine/18992
tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
else:
    tool = tools[0]
    #print("Will use tool '%s'" % (tool.get_name()))
    langs = tool.get_available_languages()
    #print("Available languages: %s" % ", ".join(langs))
    lang = langs[0]
    #print("Will use lang '%s'" % (lang))
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    #builder = pyocr.builders.DigitBuilder(tesseract_layout=6)

# PDF
if len(sys.argv) == 2:
    #print(sys.argv[1])
    pages = convert_from_path(sys.argv[1], dpi = 200)
    if len(pages) == 2:
        # Select page 1 and convert into grayscale
        img_gray = pages[0].convert('L')

        b1_results = []
        b2_results = []
        #for th in [35, 40, 45, 50, 55, 60, 65, 70, 75]:
        for th in [45, 50, 55, 60, 65, 70, 75]:
            # Thresholding
            img = ((np.array(img_gray) > th) * 255).astype(np.uint8)
            img = PIL.Image.fromarray(img)
            img = img.filter(ImageFilter.MedianFilter(size = 3))
            #print(type(img))
            #print(img.size)

            # Crop bottom regions
            img_b1 = img.crop((int(img.size[0] * 0.05), int(img.size[1] * 0.91),
                               int(img.size[0] * 0.35), int(img.size[1] * 0.98)))
                               #int(img.size[0] * 0.35), img.size[1]))
            img_b2 = img.crop((int(img.size[0] * 0.65), int(img.size[1] * 0.91),
                               int(img.size[0] * 0.95), int(img.size[1] * 0.98)))
                               #int(img.size[0] * 0.95), img.size[1]))
            img_b1.save('tmp1.png')
            img_b2.save('tmp2.png')

            # OCR
            b1_txt = tool.image_to_string(img_b1, lang = lang, builder = builder)
            b2_txt = tool.image_to_string(img_b2, lang = lang, builder = builder)
            #print('orig =', b1_txt, b2_txt)
            # b1
            b1_c = ''
            for c in b1_txt[1:]:
                if c == ' ':
                    continue
                if not c.isdigit():
                    if c in ['o', 'O']:
                        c = '0'
                    if c in ['i', 'I', 'l', '|']:
                        c = '1'
                    if c in ['T']:
                        c = '7'
                b1_c += c
            try:
                b1_results.append(int(b1_c[0:4]))
            except ValueError as e:
                print(e)
            # b2
            b2_c = ''
            for c in b2_txt:
                if c == ' ':
                    continue
                if not c.isdigit():
                    if c in ['o', 'O']:
                        c = '0'
                    if c in ['i', 'I', 'l', '|']:
                        c = '1'
                    if c in ['R']:
                        c = '2'
                    if c in ['T']:
                        c = '7'
                b2_c += c
            try:
                b2_results.append(int(b2_c[0:6]))
            except ValueError as e:
                print(e)
        print('B{0:04d}組 {1:06d}'.format(
              sorted(b1_results)[int(len(b1_results) / 2)],
              sorted(b2_results)[int(len(b2_results) / 2)]))

