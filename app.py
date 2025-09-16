from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import base64

app = Flask(__name__)

def luminosite(rgb):
    r, g, b = rgb
    return 0.299*r + 0.587*g + 0.114*b

def get_sorted_colors(img):
    img = img.convert("RGB")
    colors = list({px for px in img.getdata()})  # unique couleurs
    return sorted(colors, key=luminosite, reverse=True)

def remap_image(img, src_palette, dst_palette):
    img = img.convert("RGB")
    px = img.load()

    # associer chaque couleur source à une couleur cible
    mapping = {}
    for i, src in enumerate(src_palette):
        if i < len(dst_palette):
            mapping[src] = dst_palette[i]

    for y in range(img.height):
        for x in range(img.width):
            c = px[x, y]
            if c in mapping:
                px[x, y] = mapping[c]

    return img

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file1 = request.files["image1"]
        file2 = request.files["image2"]

        if file1 and file2:
            img1 = Image.open(file1.stream)
            img2 = Image.open(file2.stream)

            palette1 = get_sorted_colors(img1)
            palette2 = get_sorted_colors(img2)

            result = remap_image(img2, palette2, palette1)

            # renvoyer l’image en mémoire
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode()
            result_url = "data:image/png;base64," + img_b64
            #return send_file(buf, mimetype="image/png")
            return render_template("index.html", result_url=result_url)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")

