from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def watermark_image(image_name):
    im = Image.open(image_name)
    drawing = ImageDraw.Draw(im)
    color = (255,255,255,125)
    font = ImageFont.truetype('SupermercadoOne-Regular.ttf', 48)
    drawing.text((0, 0), '@my_wallpapers_PROWEB_bot', fill=color, font=font)
    im.save(f'water_{image_name}')