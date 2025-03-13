from PIL import Image
from PIL import Image
from PIL.ExifTags import TAGS

def get_image_exif(image):
    img = Image.open(image)

    img_info = img._getexif()
    for tag_id in img_info:
        tag = TAGS.get(tag_id, tag_id)
        if tag != "GPSInfo":
            continue
        data = img_info.get(tag_id)
        print(f"{int(data[2][0])}°{int(data[2][1])}'{data[2][2]}\"{data[1]}", f"{int(data[4][0])}°{int(data[4][1])}'{data[4][2]}\"{data[3]}")
    img.close()

image ='임병은.jpg'
print(get_image_exif(image))
