from PIL import Image
import os
import random as rd
import time



about = "Module for hiding data in PNG images."
f = {
    "extract(png)": "Extracts a GIF image from a PNG image.",
    "extract_txt(png)": "Extracts most ASCII chars from a PNG.",
    "weave(png, gif)": "Inserts a GIF image into a PNG image.",
    "weave_txt(png, txt)": "Plants most ASCII chars to a PNG.",
}


def extract(png):
    '''Extracts a GIF image from a PNG image.
    Gif image will have the same size as the PNG.
    '''
    if png[-4:] != ".png": png += ".png"
    try:
        host_image = Image.open(png)
        host_pxlmap = host_image.load()
    except:
        print("Error: PNG image not found.")
        return None
    bit_data = ""
    t = time.process_time()
    print("Beginning to extract GIF from {}...".format(png))
    w, h = host_image.size[0], host_image.size[1]
    for rw in range(h):
        for cl in range(w):
            hmap = host_pxlmap[cl, rw]
            cv = ["{0:08b}".format(hmap[i], "b") for i in range(3)]
            byte = cv[0][-3:] + cv[1][-3:] + cv[2][-2:]
            bit_data += byte
    new_gif = Image.new('P', host_image.size)  # still black/white
    new_pxlmap = new_gif.load()
    for rw in range(h):
        for cl in range(w):
            n = cl + (rw * w)
            z = n * 8
            a = int(bit_data[z:z+8], 2)
            new_pxlmap[cl, rw] = a
    endtime = time.process_time() - t
    print("Extraction successful. {0:.2f} second(s)\n".format(endtime))
    new_gif.save("{}-g.gif".format(png[:-4]))
    try:
        host_image.close()
        new_gif.close()
    except:
        pass


def extract_txt(png):
    if png[-4:] != ".png": png += ".png"
    try: host_image = Image.open(png)
    except:
        print("Error: {} not found.".format(png))
        return None
    host_pxlmap = host_image.load()
    w, h = host_image.size[0], host_image.size[1]
    bit_data = ""  # bytes
    full_data = ""  # characters
    t = time.process_time()
    print("Beginning to extract data from {}...".format(png))
    for rw in range(h):
        for cl in range(w):
            hpxmap = host_pxlmap[cl, rw]
            cv = ["{0:08b}".format(hpxmap[i], "b") for i in range(3)]
            partial_byte = cv[0][-2:] + cv[1][-2:] + cv[2][-2:]  # r g b
            bit_data += partial_byte
    # bytes to string
    for i in range(len(bit_data) // 8):
        n = i * 8
        try: a = str(chr(int(bit_data[n:n+8], 2)))
        except: a = "[?]"  # unknown character
        full_data += a
    txt = full_data.split("{#ß#}")[0]
    endtime = time.process_time() - t
    print("Extraction successful. {0:.2f} second(s)".format(endtime))
    print("End file length: {}\n".format(len(txt)))
    host_image.close()
    return txt


def weave(png, gif):
    '''Inserts a GIF image into a PNG image.
    Png and gif images MUST have the same size.
    '''
    if png[-4:] != ".png": png += ".png"
    if gif[-4:] != ".gif": gif += ".gif"
    try:
        p_img, g_img = Image.open(png), Image.open(gif)
        p_pxlmap, g_pxlmap = p_img.load(), g_img.load()
    except:
        print("Error: Arg0 is not a PNG / Arg1 is not a GIF image.")
        return None
    if p_img.size != g_img.size:
        print("Error: Image sizes are not the same.")
        return None
    g_bytes = ""
    # encrypt directly in function
    t = time.process_time()
    print("Beginning to weave {} into {}[0].png...".format(gif, png[:-4]))
    # get GIF values and turn them into bytes
    for rw in range(g_img.size[1]):
        for cl in range(g_img.size[0]):
            a = g_pxlmap[cl, rw]
            g_bytes += "{0:08b}".format(a, "b")
    # create new PNG for data
    new_png = Image.new(p_img.mode, p_img.size)
    new_pxlmap = new_png.load()
    bits_encoded = 0
    # weave GIF data into each PNG px
    w, h = p_img.size[0], p_img.size[1]
    for rw in range(h):
        for cl in range(w):
            n = cl + (rw * p_img.size[0])
            pngmap = p_pxlmap[cl, rw]
            # convert PNG px values to binary string
            cv = ["{0:08b}".format(pngmap[i], "b") for i in range(3)]
            # weave bytes in PNG px
            j = n * 8
            r0 = cv[0][:5] + g_bytes[j:j+3]
            g0 = cv[1][:5] + g_bytes[j+3:j+6]
            b0 = cv[2][:6] + g_bytes[j+6:j+8]
            bits_encoded += 8
            # convert back to int
            r, g, b = int(r0, 2), int(g0, 2), int(b0, 2)
            new_pxlmap[cl, rw] = (r, g, b)
    endtime = time.process_time() - t
    print("Weave successful. {0:.2f} second(s)".format(endtime))
    print("Bytes encoded: {}, {}x{}px\n".format((bits_encoded//8), w, h))
    os.remove(png)
    new_png.save("{}[0].png".format(png[:-4]))
    try:
        p_img.close(); g_img.close(); new_png.close()
    except: pass


def weave_txt(png, txt):
    if png[-4:] != ".png": png += ".png"
    txt = str(txt) + "{#ß#}"  # closing symbol
    txt += "0" * (len(txt) % 6)  # 6bits / px
    bmsg = ""
    for letter in txt:  # convert to bytes
        try: a = "{0:08b}".format(ord(letter), "b")
        except: a = "{0:08b}".format(ord("?"), "b")
        bmsg += a
    try:
        host_image = Image.open(png)  # image to be copied
        host_pxlmap = host_image.load()
    except:
        print("Error: {} not found.".format(png))
        return None
    w, h = host_image.size[0], host_image.size[1]
    if (len(bmsg) / 6) < (w * h):  # 6 bits / px
        new_image = Image.new(host_image.mode, host_image.size)
        new_pxlmap = new_image.load()
        bits_encoded = 0
        t = time.process_time()
        print("Weaving data into {}-00.png...".format(png[:-4]))
        for rw in range(h):
            for cl in range(w):
                n = cl + (rw * w)
                hpxmap = host_pxlmap[cl, rw]
                # convert to binary string
                cv = ["{0:08b}".format(hpxmap[i], "b") for i in range(3)]
                # create random 2LSB to replace
                rn = [str(rd.randint(0, 1)) for x in range(6)]
                r0 = cv[0][:6] + rn[0] + rn[1]
                g0 = cv[1][:6] + rn[2] + rn[3]
                b0 = cv[2][:6] + rn[4] + rn[5]
                if n < (len(bmsg) // 6):
                    # encode 6bits in a pixel
                    j = n * 6
                    r0 = cv[0][:6] + bmsg[j:j+2]
                    g0 = cv[1][:6] + bmsg[j+2:j+4]
                    b0 = cv[2][:6] + bmsg[j+4:j+6]
                    bits_encoded += 6
                # convert back to int
                r, g, b = int(r0, 2), int(g0, 2), int(b0, 2)
                new_pxlmap[cl, rw] = (r, g, b)
        endtime = time.process_time() - t
        print("Weave successful. {0:.2f} second(s)".format(endtime))
        print("Bits encoded: {}\n".format(bits_encoded))
        os.remove(png)
        new_image.save("{}-00.png".format(png[:-4]))
    else:
        print("Error: {}x{}px is not enough.".format(w, h))
        return None
    try:
        host_image.close(); new_image.close()
    except: pass


def help():
    print("Functions:")
    for x in f.items():
        print("{} :: {}".format(x[0], x[1]))
    print()
